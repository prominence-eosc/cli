class ParameterSet(object):
    """
    """
    def __init__(self, name, start=None, end=None, step=None, values=[]):
        self._name = name
        self._start = start
        self._end = end
        self._step = step
        self._values = values

    @property
    def name(self):
        """
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        """
        self._name = name

    @property
    def start(self):
        """
        """
        return self._start

    @start.setter
    def start(self, start):
        """
        """
        self._start = start

    @property
    def end(self):
        """
        """
        return self._end

    @end.setter
    def end(self, end):
        """
        """
        self._end = end

    @property
    def step(self):
        """
        """
        return self._step

    @step.setter
    def step(self, step):
        """
        """
        self._step = step

    @property
    def values(self):
        """
        """
        return self._values

    @values.setter
    def values(self, values):
        """
        """
        self._values = values

    def to_dict(self):
        """
        """
        if self._name and self._start is not None and self._end is not None and self._step is not None:
            return {'name': self._name,
                    'start': self._start,
                    'end': self._end,
                    'step': self._step}
        elif self._name and self._values:
            return {'name': self._name,
                    'values': self._values}
        return {}

class Factory(object):
    """
    Factory base class
    """
    def __init__(self):
        self._name = None
        self._jobs = []

    @property
    def name(self):
        """
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        """
        self._name = name

    @property
    def jobs(self):
        """
        """
        return self._jobs

    @jobs.setter
    def jobs(self, jobs):
        """
        """
        self._jobs = jobs

class ParameterSweep(Factory):
    def __init__(self):
        super().__init__()
        self._parameters = []

    @property
    def parameters(self):
        """
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """
        """
        self._parameters = parameters

    def to_dict(self):
        """
        """
        data = {}
        data['name'] = self._name
        data['type'] = 'parameterSweep'
        data['jobs'] = []
        for job in self._jobs:
            data['jobs'].append(job.name)
        data['parameters'] = []
        for set in self._parameters:
            data['parameters'].append(set.to_dict())

        return data

class Zip(Factory):
    def __init__(self):
        super().__init__()
        self._parameters = []

    @property
    def parameters(self):
        """
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """
        """
        self._parameters = parameters

    def to_dict(self):
        """
        """
        data = {}
        data['name'] = self._name
        data['type'] = 'zip'
        data['jobs'] = []
        for job in self._jobs:
            data['jobs'].append(job.name)
        data['parameters'] = []
        for set in self._parameters:
            data['parameters'].append(set.to_dict())

        return data

class Repeat(Factory):
    def __init__(self, num=None):
        super().__init__()
        self._num = num

    @property
    def num(self):
        """
        """
        return self._num

    @num.setter
    def num(self, num):
        """
        """
        self._num = num

    def to_dict(self):
        """
        """
        data = {}
        data['name'] = self._name
        data['type'] = 'repeat'
        data['jobs'] = []
        for job in self._jobs:
            data['jobs'].append(job.name)
        data['num'] = self._num

        return data
