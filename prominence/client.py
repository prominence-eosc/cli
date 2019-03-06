from collections import namedtuple
import json
import requests

class ProminenceClient(object):
    """
    PROMINENCE client class
    """

    # Named tuple containing a return code & data object
    Response = namedtuple("Response", ["return_code", "data"])

    def __init__(self, url=None, token=None):
        self._url = url
        self._timeout = 10
        self._headers = {"Authorization":"Bearer %s" % token}

    def list_jobs(self, completed, all, num, constraint):
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

        try:
            response = requests.get(self._url + '/jobs', params=params, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data=response.json())
        elif response.status_code < 500:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def list_workflows(self, completed, all, num, constraint):
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

        try:
            response = requests.get(self._url + '/workflows', params=params, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data=response.json())
        elif response.status_code < 500:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def create_job(self, job):
        """
        Create a job
        """
        return self.create_job_from_json(job.to_json())

    def create_job_from_json(self, job):
        """
        Create a job from a JSON description
        """
        data = job
        try:
            response = requests.post(self._url + '/jobs', json=data, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})
        if response.status_code == 201:
            if 'id' in response.json():
                return self.Response(return_code=0, data={'id': response.json()['id']})
        elif response.status_code < 500:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})        
        return self.Response(return_code=1, data={'error': 'unknown'})

    def create_workflow(self, workflow):
        """
        Create a workflow
        """
        return self.create_workflow_from_json(workflow.to_json())

    def create_workflow_from_json(self, workflow):
        """
        Create a workflow from a JSON description
        """
        data = workflow
        try:
            response = requests.post(self._url + '/workflows', json=data, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})
        if response.status_code == 201:
            if 'id' in response.json():
                return self.Response(return_code=0, data={'id': response.json()['id']})
        elif response.status_code < 500:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

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
            response = requests.delete(self._url + '/%s/%d' % (resource, id), timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data={})
        elif response.status_code == 500:
            self.Response(return_code=1, data={'error': 'unknown'})
        else:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def describe_job(self, job_id, completed=False):
        """
        Describe a specific job
        """
        if completed:
            completed = 'true'
        else:
            completed = 'false'
        params = {'completed':completed, 'num':1}

        try:
            response = requests.get(self._url + '/jobs/%d' % job_id, params=params, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data=response.json())
        elif response.status_code < 500:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def describe_workflow(self, workflow_id, completed=False):
        """
        Describe a specific workflow
        """
        if completed:
            completed = 'true'
        else:
            completed = 'false'
        params = {'completed':completed, 'num':1}

        try:
            response = requests.get(self._url + '/workflows/%d' % workflow_id, params=params, timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data=response.json())
        elif response.status_code < 500:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def stdout_job(self, job_id):
        """
        Get standard output from a job
        """
        return self.stdout_generic('jobs', job_id, '0')

    def stdout_workflow(self, job_id, job):
        """
        Get standard output from a workflow
        """
        return self.stdout_generic('workflows', job_id, job)

    def stdout_generic(self, type, id, job):
        """
        Get standard output from a job or workflow
        """
        try:
            response = requests.get(self._url + '/%s/%d/%s/stdout' % (type, id, job), timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data=response.text)
        else:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def stderr_job(self, job_id):
        """
        Get standard error from a job
        """
        return self.stderr_generic('jobs', job_id, '0')

    def stderr_workflow(self, job_id, job):
        """
        Get standard error from a workflow
        """
        return self.stderr_generic('workflows', job_id, job)

    def stderr_generic(self, type, id, job):
        """
        Get standard error from a job
        """
        try:
            response = requests.get(self._url + '/%s/%d/%s/stderr' % (type, id, job), timeout=self._timeout, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 200:
            return self.Response(return_code=0, data=response.text)
        else:
            if 'error' in response.json():
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
        return self.Response(return_code=1, data={'error': 'unknown'})

    def upload(self, file, filename):
        """
        Upload a file to transient cloud storage
        """   
        # Get Swift URL
        data = {'filename':file}
        
        try:
            response = requests.post(self._url + '/data/upload', json=data, headers=self._headers)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to PROMINENCE server'})

        if response.status_code == 201:
            if 'url' in response.json():
                url = response.json()['url']
        else:
            if 'error' in response.text:
                return self.Response(return_code=1, data={'error': '%s' % response.json()['error']})
            return self.Response(return_code=1, data={'error': 'unknown'})

        # Upload
        try:
            with open(filename, 'rb') as file_obj:
                response = requests.put(url, data=file_obj)
        except requests.exceptions.RequestException:
            return self.Response(return_code=1, data={'error': 'cannot connect to cloud storage'})
        except IOError as e:
            return self.Response(return_code=1, data={'error': e})

        if response.status_code == 201:
            return self.Response(return_code=0, data={})
        return self.Response(return_code=1, data={'error': 'got status code %d from cloud storage' % response.status_code})

