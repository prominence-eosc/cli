import time

from prominence import ProminenceClient, WorkflowPolicies

class JobFactory(object):
    """
    Job factory
    """
    def __init__(self, type=None):
        self._type = type
        


class Workflow(object):
    """
    Workflow
    """
    def __init__(self, id=None):
        self._last_status_check = 0
        self._client = ProminenceClient(authenticated=True)
        self._jobs = []
        self._id = id
        self._name = ''
        self._labels = {}
        self._status = None
        self._policies = WorkflowPolicies()
        self._notifications = []
        self._factories = []
        self._dependencies = []
        self._factories = []

    @property
    def id(self):
        """
        Return the workflow id
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
    def factories(self):
        return self._factories

    @factories.setter
    def factories(self, factories):
        self._factories = factories

    @property
    def jobs(self):
        return self._jobs

    @jobs.setter
    def jobs(self, jobs):
        self._jobs = jobs

    @property
    def dependencies(self):
        return self._dependencies

    @dependencies.setter
    def dependencies(self, dependencies):
        self._dependencies = dependencies

    @property
    def notifications(self):
        return self._notifications

    @notifications.setter
    def notifications(self, notifications):
        self._notifications = notifications

    def create(self):
        self._id = self._client.create_workflow(self.to_dict())

    @property
    def status(self):
        """
        Get the workflow status
        """
        if time.time() - self._last_status_check > 5:
            try:
                job = self._client.describe_job(self._id)
            except Exception as err:
                if 'No such workflow' in str(err):
                    workflow = self._client.describe_workflow(self._id)
                return False
            self._status = workflow['status']
            self._last_status_check = time.time()

        return self._status

    def done(self):
        """
        Return True if the workflow is in a terminal state
        """
        if self.status in ('completed', 'failed', 'deleted', 'killed'):
            return True
        return False

    def wait(self, timeout=0):
        """
        Wait for the workflwo to complete
        """
        start = time.time()
        while not self.done():
            if timeout > 0 and time.time() - start > timeout:
                return
            time.sleep(5)
        return

    def to_dict(self):
        """
        Return a JSON description of the job
        """
        data = {}
        data['jobs'] = []
        for job in self._jobs:
            data['jobs'].append(job.to_dict())
        if self._policies.to_dict():
            data['policies'] = self._policies.to_dict()
        if self._notifications:
            data['notifications'] = []
            for notification in self._notifications:
                data['notifications'].append(notification.to_dict())
        data['name'] = self._name
        if self._labels:
            data['labels'] = self._labels
        if self._dependencies:
            data['dependencies'] = {}
            for dependency in self._dependencies:
                for key in dependency.to_dict():
                    data['dependencies'][key] = dependency.to_dict()[key]
        if self._factories:
            data['factories'] = []
            for factory in self._factories:
                data['factories'].append(factory.to_dict())

        return data

    def delete(self):
        """
        Delete the workflow
        """
        return self._client.delete_workflow(self._id)

    def remove(self):
        """
        Remove the workflow from the queue
        """
        return self._client.remove('workflow', self._id)

    def rerun(self):
        """
        Rerun any failed jobs from the workflow.
        """
        return self._client.rerun(self._id)
