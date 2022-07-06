class CpusInterval(object):
    def __init__(self):
        self._min = None
        self._max = None

    @property
    def min(self):
        """
        """
        return self._min

    @min.setter
    def min(self, min):
        """
        """
        self._min = min

    @property
    def max(self):
        """
        """
        return self._max

    @max.setter
    def max(self, max):
        """
        """
        self._max = max

    def to_dict(self):
        """
        """
        if self._min and self._max:
            return [self._min, self._max]
        return []

class Resources(object):
    """
    Job resources
    """
    def __init__(self, cpus=1, memory=1, disk=10, nodes=1, walltime=0):
        self._cpus = cpus
        self._memory = memory
        self._disk = disk
        self._nodes = nodes
        self._walltime = walltime
        self._cpus_range = CpusInterval()
        self._cpus_options = CpusInterval()
        self._total_cpus_range = CpusInterval()
        self._memory_per_cpu = 0

    @property
    def cpus(self):
        """
        Return the number of CPUs
        """
        return self._cpus

    @cpus.setter
    def cpus(self, cpus):
        """
        Set the number of CPUs
        """
        self._cpus = cpus

    @property
    def memory(self):
        """
        Return the memory
        """
        return self._memory

    @memory.setter
    def memory(self, memory):
        """
        Set the memory
        """
        self._memory = memory

    @property
    def memory_per_cpu(self):
        """
        Return the memory_per_cpu
        """
        return self._memory_per_cpu

    @memory_per_cpu.setter
    def memory_per_cpu(self, memory_per_cpu):
        """
        Set the memory per CPU
        """
        self._memory_per_cpu = memory_per_cpu

    @property
    def disk(self):
        """
        Return the disk
        """
        return self._disk

    @disk.setter
    def disk(self, disk):
        """
        Set the disk
        """
        self._disk = disk

    @property
    def walltime(self):
        """
        Return the walltime
        """
        return self._walltime

    @walltime.setter
    def walltime(self, walltime):
        """
        Set the walltime
        """
        self._walltime = walltime

    @property
    def cpus_range(self):
        """
        """
        return self._cpus_range

    @cpus_range.setter
    def cpus_range(self, cpus_range):
        """
        """
        self._cpus_range = cpus_range

    @property
    def cpus_options(self):
        """
        """
        return self._cpus_options

    @cpus_options.setter
    def cpus_options(self, cpus_options):
        """
        """
        self._cpus_options = cpus_options

    @property
    def total_cpus_range(self):
        """
        """
        return self._total_cpus_range

    @total_cpus_range.setter
    def total_cpus_range(self, total_cpus_range):
        """
        """
        self._total_cpus_range = total_cpus_range

    def to_dict(self):
        """
        Return a JSON description of the resources
        """
        resources = {'cpus': self._cpus,
                     'disk': self._disk,
                     'nodes': self._nodes}
        if self._walltime > 0:
            resources['walltime'] = self._walltime

        if self._cpus_range.to_dict():
            resources['cpusRange'] = self._cpus_range.to_dict()

        if self._cpus_options.to_dict():
            resources['cpusOptions'] = self._cpus_options.to_dict()

        if self._total_cpus_range.to_dict():
            resources['totalCpusRange'] = self._total_cpus_range.to_dict()

        if self._memory_per_cpu > 0:
            resources['memoryPerCpu'] = self._memory_per_cpu
        else:
            resources['memory'] = self._memory

        return resources
