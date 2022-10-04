import base64
import io
import os
import sys
import tarfile
import time
import requests

from prominence import InputFile, JobPolicies, ProminenceClient, Resources, Task

def read_from_tarfile(content):
    """
    Return a string extracted from the provided .tgz content
    """
    if content:
        with tarfile.open(fileobj=io.BytesIO(content.encode('utf-8'))) as tf:
            for entry in tf:
                fileobj = tf.extractfile(entry)
                return fileobj.read().decode()

def get_or_download(url, save_as):
    """
    Download from a URL into memory or save to disk
    """
    if not save_as:
        try:
            response = requests.get(url)
        except Exception as err:
            return False
        return response.text
    else:
        try:
            response = requests.get(url, stream=True, timeout=30)
        except requests.exceptions.RequestException as err:
            return False

    total_length = response.headers.get('content-length')

    if response.status_code != 200:
        return False

    with open(save_as, 'wb') as fh:
        if total_length is None:
            fh.write(response.content)
        else:
            for data in response.iter_content(chunk_size=4096):
                fh.write(data)

    return True

class Execution(object):
    def __init__(self, execution):
        self._execution = execution

    @property
    def site(self):
        if 'site' in self._execution:
            return self._execution['site']
        return None

    @property
    def runtime_version(self):
        if 'runtimeVersion' in self._execution:
            return self._execution['runtimeVersion']
        return None

    @property
    def provisioned_resources(self):
        if 'provisionedResources' in self._execution:
            return self._execution['provisionedResources']
        return None

    @property
    def cpu_info(self):
        if 'cpu' in self._execution:
            return self._execution['cpu']
        return None

    @property
    def tasks(self):
        if 'tasks' in self._execution:
            return self._execution['tasks']
        return None

class Events(object):
    def __init__(self, create, start, end):
        self._create = create
        self._start = start
        self._end = end

    @property
    def create(self):
        return self._create

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    def to_dict(self):
        return {'createTime': self._create,
                'startTime': self._start,
                'endTime': self._end}
    
class Job(object):
    """
    Job
    """
    def __init__(self, id=None):
        self._last_status_check = 0
        self._client = ProminenceClient(authenticated=True)
        self._job = None
        self._tasks = []
        self._id = id
        self._name = ''
        self._labels = {}
        self._status = None
        self._output_files = []
        self._output_directories = []
        self._resources = Resources()
        self._input_files = []
        self._artifacts = []
        self._execution = {}
        self._policies = JobPolicies()
        self._notifications = []
        self._events = None

        if self._id:
            self._update()

    @property
    def id(self):
        """
        Return the job id
        """
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property                   
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, labels):
        self._labels = labels

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, resources):
        self._resources = resources

    @property
    def notifications(self):
        return self._notifications

    @notifications.setter
    def notifications(self, notifications):
        self._notifications = notifications

    @property
    def tasks(self):
        """
        Return the list of tasks
        """
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        """
        Set tasks
        """
        self._tasks = tasks

    @property
    def output_files(self):
        return self._output_files

    @output_files.setter
    def output_files(self, output_files):
        self._output_files = output_files

    @property
    def artifacts(self):
        return self._artifacts

    @artifacts.setter
    def artifacts(self, artifacts):
        self._artifacts = artifacts

    @property
    def output_directories(self):
        return self._output_directories

    @output_directories.setter
    def output_directories(self, output_directories):
        self._output_directories = output_directories

    @property
    def input_files(self):
        return self._input_files

    @input_files.setter
    def input_files(self, input_files):
        self._input_files = input_files

    @property
    def policies(self):
        return self._policies

    @policies.setter
    def policies(self, policies):
        self._policies = policies

    def create(self):
        self._id = self._client.create_job(self.to_dict())

    def get_input_file(self, name):
        """
        Return the specified input file
        """
        job = self._client.describe_job(self._id)
        for input in job['inputs']:
            if name == input['filename']:
                return base64.b64decode(input['content'])

        return None

    def get_output_file(self, name, save_as=None):
        """
        Download the specified output file
        """
        job = self._client.describe_job(self._id)
        for output in job['outputFiles']:
            if output['name'] == name:
                url = output['url']
                return get_or_download(url, save_as)

        return False

    def get_output_directory(self, name, save_as=None):
        """
        Download the specified output file
        """
        job = self._client.describe_job(self._id)
        for output in job['outputDirs']:
            if output['name'] == name:
                url = output['url']
                return get_or_download(url, save_as)

        return False

    def to_dict(self):
        """
        Return a JSON description of the job
        """
        data = {}
        data['tasks'] = []
        data['resources'] = self._resources.to_dict()
        for task in self._tasks:
            data['tasks'].append(task.to_dict())
        if self._artifacts:
            data['artifacts'] = []
            for artifact in self._artifacts:
                data['artifacts'].append(artifact.to_dict())
        if self._output_files:
            data['outputFiles'] = []
            for output_file in self._output_files:
                data['outputFiles'].append(output_file)
        if self._output_directories:
            data['outputDirs'] = []
            for output_directory in self._output_directories:
                data['outputDirs'].append(output_directory)
        if self._input_files:
            data['inputs'] = []
            for input_file in self._input_files:
                if type(input_file) is InputFile:
                    data['inputs'].append(input_file.to_dict())
                else:
                    data['inputs'].append(input_file)
        if self._policies.to_dict():
            data['policies'] = self._policies.to_dict()
        if self._notifications:
            data['notifications'] = []
            for notification in self._notifications:
                data['notifications'].append(notification.to_dict())
        data['name'] = self._name
        if self._labels:
            data['labels'] = self._labels
        return data

    def _update(self):
        """
        Update internal representation of job
        """
        # If the status is non-terminal, get the current job JSON
        if self._status not in ('completed', 'failed', 'deleted', 'killed'):
            # Ensure we don't run this too frequently
            if time.time() - self._last_status_check > 5:
                try:
                    self._job = self._client.describe_job(self._id)
                except:
                    return False

                self._last_status_check = time.time()

                if 'status' in self._job:
                    self._status = self._job['status']

    @property
    def status(self):
        """
        Get the job status
        """
        self._update()
        return self._status

    def done(self):
        """
        Return True if the job is in a terminal state
        """
        self._update()

        if self._status in ('completed', 'failed', 'deleted', 'killed'):
            return True
        return False

    def wait(self, timeout=0):
        """
        Wait for the job to complete
        """
        start = time.time()
        while not self.done():
            if timeout > 0 and time.time() - start > timeout:
                return
            time.sleep(5)
        return

    @property
    def events(self):
        """
        """
        create = None
        start = None
        end = None
        self._update()
        if 'events' in self._job:
            if 'createTime' in self._job['events']:
                create = self._job['events']['createTime']
            if 'startTime' in self._job['events']:
                start = self._job['events']['startTime']
            if 'endTime' in self._job['events']:
                end = self._job['events']['endTime']
        events = Events(create, start, end)
        return events

    @property
    def execution(self):
        """
        Return the execution block
        """
        self._update()
        if 'execution' in self._job:
            self._execution = self._job['execution']
            return Execution(self._execution)
        return Execution(None)

    def stdout(self, node=0, offset=0):
        """
        Return the job standard output
        """
        return self._client.stdout_job(self._id, node, offset)

    def stderr(self, node=0, offset=0):
        """
        Return the job standard error
        """
        return self._client.stderr_job(self._id, node, offset)

    def execute(self, command):
        """
        Execute a command within a running job
        """
        return self._client.execute_command(self._id, command)

    def get_snapshot(self, path, save_as=None):
        """
        Get a snapshot
        """
        if self._client.create_snapshot(self._id, path):
            response = self._client.get_snapshot_url(self._id)
            if 'url' in response:
                if not save_as:
                    return read_from_tarfile(get_or_download(response['url'], save_as))
                else:
                    return get_or_download(response['url'], save_as)

        return None

    def delete(self):
        """
        Delete the job
        """
        return self._client.delete_job(self._id)

    def remove(self):
        """
        Remove the job from the queue
        """
        return self._client.remove('job', self._id)
