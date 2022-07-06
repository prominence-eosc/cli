class JobPolicies(object):
    """
    Job policy
    """
    def __init__(self):
        self._maximum_task_retries = 0
        self._maximum_retries = 0
        self._maximum_time_in_queue = -2
        self._priority = -1
        self._leave_in_queue = None
        self._ignore_task_failures = None
        self._run_serial_tasks_on_all_nodes = None
        self._report_job_success_on_task_failure = None

    @property
    def maximum_task_retries(self):
        """
        """
        return self._maximum_task_retries

    @maximum_task_retries.setter
    def maximum_task_retries(self, maximum_task_retries):
        """
        """
        self._maximum_task_retries = maximum_task_retries

    @property
    def maximum_retries(self):
        """
        """
        return self._maximum_retries

    @maximum_retries.setter
    def maximum_retries(self, maximum_retries):
        """
        """
        self._maximum_retries = maximum_retries

    @property
    def maximum_time_in_queue(self):
        """
        """
        return self._maximum_time_in_queue

    @maximum_time_in_queue.setter
    def maximum_time_in_queue(self, maximum_time_in_queue):
        """
        """
        self._maximum_time_in_queue = maximum_time_in_queue

    @property
    def priority(self):
        """
        """
        return self._priority

    @priority.setter
    def priority(self, priority):
        """
        """
        self._priority = priority

    @property
    def leave_in_queue(self):
        """
        """
        return self._leave_in_queue

    @leave_in_queue.setter
    def leave_in_queue(self, leave_in_queue):
        """
        """
        self._leave_in_queue = leave_in_queue

    @property
    def ignore_task_failures(self):
        """
        """
        return self._ignore_task_failures

    @ignore_task_failures.setter
    def ignore_task_failures(self, ignore_task_failures):
        """
        """
        self._ignore_task_failures = ignore_task_failures

    @property
    def run_serial_tasks_on_all_nodes(self):
        """
        """
        return self._run_serial_tasks_on_all_nodes

    @run_serial_tasks_on_all_nodes.setter
    def run_serial_tasks_on_all_nodes(self, run_serial_tasks_on_all_nodes):
        """
        """
        self._run_serial_tasks_on_all_nodes = run_serial_tasks_on_all_nodes

    @property
    def report_job_success_on_task_failure(self):
        """
        """
        return self._report_job_success_on_task_failure

    @report_job_success_on_task_failure.setter
    def report_job_success_on_task_failure(self, report_job_success_on_task_failure):
        """
        """
        self._report_job_success_on_task_failure = report_job_success_on_task_failure

    def to_dict(self):
        """
        Return a JSON representation of the job policy
        """
        policies = {}
        if self._maximum_retries > 0:
            policies['maximumRetries'] = self._maximum_retries

        if self._maximum_task_retries > 0:
            policies['maximumTaskRetries'] = self._maximum_task_retries

        if self._maximum_time_in_queue > -2:
            policies['maximumTimeInQueue'] = self._maximum_time_in_queue

        if self._priority > -1:
            policies['priority'] = self._priority

        if self._leave_in_queue is not None:
            policies['leaveInQueue'] = self._leave_in_queue

        if self._ignore_task_failures is not None:
            policies['ignoreTaskTailures'] = self._ignore_task_failures

        if self._report_job_success_on_task_failure is not None:
            policies['reportJobSuccessOnTaskFailure'] = self._report_job_success_on_task_failure

        if self._run_serial_tasks_on_all_nodes is not None:
            policies['runSerialTasksOnAllNodes'] = self._run_serial_tasks_on_all_nodes

        return policies

class WorkflowPolicies(object):
    """
    Workflow policy
    """
    def __init__(self):
        self._maximum_retries = 0
        self._leave_in_queue = None

    @property
    def maximum_retries(self):
        """
        """
        return self._maximum_retries

    @maximum_retries.setter
    def maximum_retries(self, maximum_retries):
        """
        """
        self._maximum_retries = maximum_retries

    @property
    def leave_in_queue(self):
        """
        """
        return self._leave_in_queue

    @leave_in_queue.setter
    def leave_in_queue(self, leave_in_queue):
        """
        """
        self._leave_in_queue = leave_in_queue

    def to_dict(self):
        """
        Return a JSON representation of the workflow policy
        """
        policies = {}
        if self._maximum_retries > 0:
            policies['maximumRetries'] = self._maximum_retries

        if self._leave_in_queue is not None:
            policies['leaveInQueue'] = self._leave_in_queue

        return policies
