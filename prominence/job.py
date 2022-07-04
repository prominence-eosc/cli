import base64
import os
import sys
import time
import requests

from prominence import JobPolicies, ProminenceClient, Resources, Task

class Job(object):
    """
    Job
    """
    def __init__(self, id=None):
        self._last_status_check = 0
        self._client = ProminenceClient(authenticated=True)
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

    @property
    def output_files(self):
        return self._output_files

    @output_files.setter
    def output_files(self, output_files):
        self._output_files = output_files

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
        job = self.json()
        self._id = self._client.create_job(job)

    @tasks.setter
    def tasks(self, tasks):
        """
        Set tasks
        """
        self._tasks = tasks

    def get_input_file(self, name):
        """
        Return the specified input file
        """
        job = self._client.describe_job(self._id)
        for input in job['inputs']:
            if name == input['filename']:
                return base64.b64decode(input['content'])

        return None

    def get_output_file(self, name, filename=None):
        """
        Download the specified output file
        """
        job = self._client.describe_job(self._id)
        for output in job['outputFiles']:
            if output['name'] == name:
                url = output['url']
                if not filename:
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

                    with open(filename, 'wb') as fh:
                        if total_length is None:
                            fh.write(response.content)
                        else:
                            for data in response.iter_content(chunk_size=4096):
                                fh.write(data)


    def json(self):
        """
        Return a JSON description of the job
        """
        data = {}
        data['tasks'] = []
        data['resources'] = self._resources.json()
        for task in self._tasks:
            data['tasks'].append(task.json())
        if self._output_files:
            data['outputFiles'] = []
            for output_file in self._output_files:
                data['outputFiles'].append(output_file)
        if self._input_files:
            data['inputs'] = []
            for input_file in self._input_files:
                if 'filename' not in input_file and 'content' not in input_file:
                    if os.path.isfile(input_file):
                        with open(input_file, 'rb') as fh:
                            data['inputs'].append({'filename': input_file,
                                                   'content': base64.b64encode(fh.read()).decode("utf-8")})
                else:
                    data['inputs'].append(input_file)
        if self._policies.json():
            data['policies'] = self._policies.json()
        data['name'] = self._name
        if self._labels:
            data['labels'] = self._labels
        return data

    @property
    def status(self):
        """
        Get the job status
        """
        if time.time() - self._last_status_check > 5:
            try:
                job = self._client.describe_job(self._id)
            except Exception as err:
                if 'No such job' in str(err):
                    job = self._client.describe_job(self._id)
                return False
            self._status = job['status']
            self._last_status_check = time.time()

        return self._status

    def done(self):
        """
        Return True if the job is in a terminal state
        """
        if self.status in ('completed', 'failed', 'deleted', 'killed'):
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
    def execution(self):
        """
        Return the execution block
        """
        job = self._client.describe_job(self._id)
        if 'execution' in job:
            return job['execution']
        return {}
