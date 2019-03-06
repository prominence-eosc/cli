class ProminenceWorkflow(object):
    """
    PROMINENCE workflow class
    """

    # Attribute names
    attrs = {'name':None,
             'jobs':None,
             'dependencies':None}

    # The key is the attribute name and the value is the JSON key
    attr_map = {'name':'name',
                'jobs':'jobs',
                'dependencies':'dependencies'}

    def __init__(self, name=None, jobs=None, dependencies=None):
        self._name = name
        self._jobs = jobs
        self._dependencies = dependencies

    @property
    def jobs(self):
        """
        Gets the jobs
        """
        return self._jobs

    @jobs.setter
    def jobs(self, tasks):
        """
        Sets the jobs
        """
        self._jobs = jobs

    @property
    def dependencies(self):
        """
        Gets list of job dependencies
        """
        return self._dependencies

    @dependencies.setter
    def dependencies(self, dependencies):
        """
        Sets the job dependencies
        """
        self._dependencies = dependencies

    @property
    def name(self):
        """
        Returns the job name
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the job name
        """
        self._name = name

    def to_json(self):
        """
        Returns the job as JSON
        """
        data = {}
        for attr in self.attrs:
            value = getattr(self, attr, None)
            if value is not None:
                if self.attrs[attr] is not None:
                    if self.attrs[attr] not in data:
                        data[self.attrs[attr]] = {}
                    if attr == 'jobs':
                        jobs = []
                        for job in value:
                            jobs.append(job.to_json())
                        data['jobs'] = jobs
                    else:
                        data[self.attrs[attr]][self.attr_map[attr]] = value
                else:
                    data[self.attr_map[attr]] = value
        return data

    def from_json(self, data):
        """
        Initializes job from JSON
        """
        for attr in self.attrs:
            attr_json = self.attr_map[attr]
            if self.attrs[attr] is not None:
                if self.attrs[attr] in data:
                    data_item = data[self.attrs[attr]]
            else:
                data_item = data
            if attr_json in data_item:
                setattr(self, attr, data_item[attr_json])


