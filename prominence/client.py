import json
import os
import time
import requests

from prominence import auth
from prominence import exceptions

__all__ = ['ProminenceClient']

class ProminenceClient(object):
    """
    PROMINENCE client class
    """
    def __init__(self, authenticated=False, timeout=30):
        self._url = os.environ.get('PROMINENCE_URL', 'https://host-130-246-215-158.nubes.stfc.ac.uk/prominence/v1')
        self._timeout = timeout

        self._verify = True
        if 'PROMINENCE_SSL_VERIFY' in os.environ:
            if os.environ['PROMINENCE_SSL_VERIFY'] == 'False':
                self._verify = False

        if authenticated:
            token = auth.get_token()
            # Check if we could get a token
            if not token:
                raise exceptions.TokenError('Unable to obtain a token')

            # Check if the token has expired
            if time.time() - auth.get_expiry(token) > 0:
                raise exceptions.TokenExpiredError('Token has expired')

            self._headers = {"Authorization":"Bearer %s" % token}

    def authenticate_user(self):
        """
        Obtain token from OIDC provider
        """
        token = auth.authenticate_user(create_client_if_needed=True, token_in_file=False)
        if token:
            print('Successfully retrieved token')
            self._headers = {"Authorization":"Bearer %s" % token}
        else:
            raise exceptions.TokenError('Unable to obtain a token')

    def list_jobs(self, completed=False, all=False, num=1, constraint=None, name_constraint=None, workflow_id=None):
        """
        List running/idle jobs or completed jobs
        """
        params = {}

        if completed:
            params['completed'] = 'true'
        if num:
            params['num'] = num
        if all:
            params['all'] = 'true'
        if constraint:
            params['constraint'] = constraint
        if name_constraint:
            params['name'] = name_constraint
        if workflow_id:
            params['id'] = workflow_id
            params['workflow'] = 'true'
            params['num'] = -1

        try:
            response = requests.get(self._url + '/jobs', params=params, timeout=self._timeout, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif response.status_code < 500:
            if 'error' in response.json():
                raise exceptions.JobGetError(response.json()['error'])

        raise exceptions.JobGetError('Unknown error')

    def list_workflows(self, completed=False, all=False, num=1, constraint=None, name_constraint=None):
        """
        List running/idle workflows or completed workflows
        """
        params = {}

        if completed:
            params['completed'] = 'true'
        if num:
            params['num'] = num
        if all:
            params['all'] = 'true'
        if constraint:
            params['constraint'] = constraint
        if name_constraint:
            params['name'] = name_constraint

        try:
            response = requests.get(self._url + '/workflows', params=params, timeout=self._timeout, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif response.status_code < 500:
            if 'error' in response.json():
                raise exceptions.WorkflowGetError(response.json()['error'])

        raise exceptions.WorkflowGetError('Unknown error')

    def execute_command(self, job_id, command):
        """
        Execute a command inside a job
        """
        headers = dict(self._headers)
        headers['Content-type'] = 'application/json'

        params = {}
        params['command'] = ','.join(command)

        try:
            response = requests.post(self._url + '/jobs/%d/exec' % job_id, timeout=self._timeout, headers=headers, params=params, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            return response.text
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif 'error' in response.json():
            raise exceptions.ExecError(response.json()['error'])

        raise exceptions.ExecError('Unknown error')

    def get_snapshot_url(self, job_id):
        """
        Get the URL of the current snapshot
        """
        try:
            response = requests.get(self._url + '/jobs/%d/snapshot' % job_id, timeout=self._timeout, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif response.status_code < 500:
            if 'error' in response.json():
                raise exceptions.SnapshotGetError(response.json()['error'])

        raise exceptions.SnapshotGetError('Unknown error')

    def create_snapshot(self, job_id, path):
        """
        Create a snapshot of a file or directory in a running job
        """
        headers = dict(self._headers)
        headers['Content-type'] = 'application/json'

        params = {}
        params['path'] = path

        try:
            response = requests.put(self._url + '/jobs/%d/snapshot' % job_id, timeout=self._timeout, headers=headers, params=params, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            return response.text
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif 'error' in response.json():
            raise exceptions.SnapshotCreateError(response.json()['error'])

        raise exceptions.SnapshotCreateError('Unknown error')

    def create_job(self, job):
        """
        Create a job from a JSON description
        """
        headers = dict(self._headers)
        headers['Content-type'] = 'application/json'

        try:
            response = requests.post(self._url + '/jobs', data=json.dumps(job), timeout=self._timeout, headers=headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 201:
            if 'id' in response.json():
                return response.json()['id']
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif response.status_code < 500:
            if 'error' in response.json():
                raise exceptions.JobCreationError(response.json()['error'])

        raise exceptions.JobCreationError('Unknown error')

    def create_workflow(self, workflow):
        """
        Create a workflow from a JSON description
        """
        headers = dict(self._headers)
        headers['Content-type'] = 'application/json'

        try:
            response = requests.post(self._url + '/workflows', data=json.dumps(workflow), timeout=self._timeout, headers=headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 201:
            if 'id' in response.json():
                return response.json()['id']
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif response.status_code < 500:
            if 'error' in response.json():
                raise exceptions.WorkflowCreationError(response.json()['error'])

        raise exceptions.WorkflowCreationError('Unknown error')

    def rerun_workflow(self, workflow_id):
        """
        Rerun any failed jobs from a completed workflow
        """
        try:
            response = requests.put(self._url + '/workflows/%d' % workflow_id, timeout=self._timeout, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            if 'id' in response.json():
                return response.json()['id']
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif response.status_code < 500:
            if 'error' in response.json():
                raise exceptions.WorkflowCreationError(response.json()['error'])

        raise exceptions.WorkflowCreationError('Unknown error')

    def delete_job(self, job_id):
        """
        Delete the specified job
        """
        return self.delete_generic(job_id, 'jobs')

    def delete_workflow(self, workflow_id):
        """
        Delete the specified workflow
        """
        return self.delete_generic(workflow_id, 'workflows')

    def delete_generic(self, id, resource):
        """
        Delete the specified job or workflow
        """
        try:
            response = requests.delete(self._url + '/%s/%d' % (resource, id), timeout=self._timeout, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            return True
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif response.status_code == 500:
            raise exceptions.DeletionError('Got a 500 internal server error from PROMINENCE')
        else:
            if 'error' in response.json():
                raise exceptions.DeletionError(response.json()['error'])

        raise exceptions.DeletionError('Unknown error')

    def describe_job(self, job_id):
        """
        Describe a specific job
        """
        try:
            response = requests.get(self._url + '/jobs/%d' % job_id, timeout=self._timeout, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            if response.json():
                return response.json()[0]
            else:
                raise exceptions.JobGetError('No such job')
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif response.status_code < 500:
            if 'error' in response.json():
                raise exceptions.JobGetError(response.json()['error'])

        raise exceptions.JobGetError('Unknown error')

    def describe_workflow(self, workflow_id):
        """
        Describe a specific workflow
        """
        try:
            response = requests.get(self._url + '/workflows/%d' % workflow_id, timeout=self._timeout, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            if response.json():
                return response.json()[0]
            else:
                raise exceptions.JobGetError('No such workflow')
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif response.status_code < 500:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})

        raise exceptions.WorkflowGetError('Unknown error')

    def stdout_job(self, job_id):
        """
        Get standard output from a job
        """
        return self.stdout_generic('jobs', job_id)

    def stdout_workflow(self, job_id, job, instance):
        """
        Get standard output from a workflow
        """
        return self.stdout_generic('workflows', job_id, job, instance)

    def stdout_generic(self, type, id, job=None, instance=-1):
        """
        Get standard output from a job or workflow
        """
        if job is not None:
            if instance > -1:
                path = '/%s/%d/%s/%d/stdout' % (type, id, job, instance)
            else:
                path = '/%s/%d/%s/stdout' % (type, id, job)
        else:
            path = '/%s/%d/stdout' % (type, id)

        try:
            response = requests.get(self._url + path, timeout=self._timeout, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            return response.text
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        else:
            if 'error' in response.json():
                raise exceptions.StdStreamsError(response.json()['error'])

        raise exceptions.StdStreamsError('Unknown error')

    def stderr_job(self, job_id):
        """
        Get standard error from a job
        """
        return self.stderr_generic('jobs', job_id)

    def stderr_workflow(self, job_id, job, instance):
        """
        Get standard error from a workflow
        """
        return self.stderr_generic('workflows', job_id, job, instance)

    def stderr_generic(self, type, id, job=None, instance=-1):
        """
        Get standard error from a job
        """
        if job is not None:
            if instance > -1:
                path = '/%s/%d/%s/%d/stderr' % (type, id, job, instance)
            else:
                path = '/%s/%d/%s/stderr' % (type, id, job)
        else:
            path = '/%s/%d/stderr' % (type, id)

        try:
            response = requests.get(self._url + path, timeout=self._timeout, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            return response.text
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        else:
            if 'error' in response.json():
                raise exceptions.StdStreamsError(response.json()['error'])

        raise exceptions.StdStreamsError('Unknown error')

    def upload(self, file, filename):
        """
        Upload a file to transient cloud storage
        """   
        # Get S3 URL
        data = {'filename':file}

        headers = dict(self._headers)
        headers['Content-type'] = 'application/json'
        
        try:
            response = requests.post(self._url + '/data/upload', data=json.dumps(data), headers=headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 201:
            if 'url' in response.json():
                url = response.json()['url']
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        else:
            if 'error' in response.json():
                raise exceptions.FileUploadError(response.json()['error'])
            raise exceptions.FileUploadError('Unknown error when querying the PROMINENCE server')

        # Upload
        try:
            with open(filename, 'rb') as file_obj:
                response = requests.put(url, data=file_obj, timeout=30)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)
        except IOError as err:
            raise exceptions.FileUploadError(err)

        if response.status_code == 200:
            return True
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid cloud storage URL, got a 404 not found error from cloud storage')

        raise exceptions.FileUploadError('Got status code', response.status_code, 'from cloud storage')

    def list_objects(self, path):
        """
        List objects in cloud storage
        """
        url = self._url + '/data'
        if path:
            url += '/%s' % path

        try:
            response = requests.get(url, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        else:
            if 'error' in response.json():
                raise exceptions.ObjectError(response.json()['error'])
            raise exceptions.ObjectError('Unknown error when querying the PROMINENCE server')

    def delete_object(self, object):
        """
        Delete an object in cloud storage
        """
        url = self._url + '/data/' + object
        try:
            response = requests.delete(url, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 204:
            return True
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        else:
            if 'error' in response.json():
                raise exceptions.ObjectError(response.json()['error'])
            raise exceptions.ObjectError('Unknown error when querying the PROMINENCE server')

        return False

    def get_usage(self, start_date, end_date, by_group, show_all_users):
        """
        Return historical usage
        """
        params = {}
        params['start'] = start_date
        params['end'] = end_date
        if by_group:
            params['by_group'] = 'true'
        if show_all_users:
            params['show_all_users'] = 'true'

        try:
            response = requests.get(self._url + '/accounting', params=params, headers=self._headers, verify=self._verify)
        except requests.exceptions.RequestException as err:
            raise exceptions.ConnectionError(err)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise exceptions.AuthenticationError()
        elif response.status_code == 404:
            raise exceptions.ConnectionError('Invalid PROMINENCE URL, got a 404 not found error')
        elif response.status_code == 500:
            raise exceptions.UsageError('Unknown error when querying the PROMINENCE server')
        else:
            if 'error' in response.json():
                raise exceptions.UsageError(response.json()['error'])
            raise exceptions.UsageError('Unknown error when querying the PROMINENCE server')

        return {}
