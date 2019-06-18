class ProminenceJob(object):
    """
    PROMINENCE job class
    """

    # Attribute names
    attrs = {'artifacts':None,
             'inputs':None,
             'output_files':None,
             'output_dirs':None,
             'nodes':'resources',
             'cpus':'resources',
             'memory':'resources',
             'disk':'resources',
             'walltime':'resources',
             'tasks':'tasks',
             'preemptible':None,
             'labels':None,
             'name':None,
             'constraints':None,
             'storage':None}

    # The key is the attribute name and the value is the JSON key
    attr_map = {'artifacts':'artifacts',
                'inputs':'inputs',
                'output_files':'outputFiles',
                'output_dirs':'outputDirs',
                'nodes':'nodes',
                'cpus':'cpus',
                'memory':'memory',
                'disk':'disk',
                'walltime':'walltime',
                'tasks':'tasks',
                'preemptible':'preemptible',
                'labels':'labels',
                'name':'name',
                'constraints':'constraints',
                'storage':'storage'}

    def __init__(self, artifacts=[], inputs=[], output_files=[], output_dirs=[], nodes=None, cpus=None, memory=None, disk=None, walltime=None, tasks=[], preemptible=None, labels={}, name=None, constraints=None, storage=None):
        self._artifacts = artifacts
        self._inputs = inputs
        self._output_files = output_files
        self._output_dirs = output_dirs
        self._nodes = nodes
        self._cpus = cpus
        self._memory = memory
        self._disk = disk
        self._walltime = walltime
        self._tasks = tasks
        self._preemptible = preemptible
        self._labels = labels
        self._name = name
        self._constraints = constraints
        self._storage = storage

    @property
    def artifacts(self):
        """
        Returns the list of artifacts to be downloaded before the job starts
        """
        return self._artifacts

    @artifacts.setter
    def artifacts(self, artifacts):
        """
        Sets the list of artifacts to be downloaded before the job starts
        """
        self._artifacts = artifacts

    def add_artifact(self, artifact):
        """
        Adds an artifact
        """
        self._artifacts.append(artifact)

    @property
    def inputs(self):
        """
        Returns the input files
        """
        return self._inputs

    @inputs.setter
    def inputs(self, inputs):
        """
        Sets the list of inputs
        """
        self._inputs = inputs

    @property
    def output_files(self):
        """
        Returns the list of output files to be uploaded to cloud storage
        """
        return self._output_files

    @output_files.setter
    def output_files(self, output_files):
        """
        Sets the list of output files to be uploaded to cloud storage
        """
        self._output_files = output_files

    def add_output_file(self, output_file):
        """
        Adds an output file
        """
        self._output_files.append(output_file)

    @property
    def output_dirs(self):
        """
        Returns the list of output directories to be uploaded to cloud storage
        """
        return self._output_dirs

    @output_dirs.setter
    def output_dirs(self, output_dirs):
        """
        Sets the list of output directories to be uploaded to cloud storage
        """
        self._output_dirs = output_dirs

    def add_output_dir(self, output_dir):
        """
        Adds an output directory
        """
        self._output_dirs.append(output_dir)

    @property
    def storage(self):
        """
        Returns the storage details
        """
        return self._storage

    @storage.setter
    def storage(self, storage):
        """
        Sets the storage details
        """
        self._storage = storage

    @property
    def nodes(self):
        """
        Returns the number of nodes
        """
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        """
        Sets the number of nodes
        """
        self._nodes = nodes

    @property
    def cpus(self):
        """
        Gets the number of CPUs
        """
        return self._cpus

    @cpus.setter
    def cpus(self, cpus):
        """
        Sets the number of CPUs
        """
        self._cpus = cpus

    @property
    def memory(self):
        """
        Returns the memory in GB
        """
        return self._memory

    @memory.setter
    def memory(self, memory):
        """
        Sets the memory in GB
        """
        self._memory = memory

    @property
    def disk(self):
        """
        Returns the disk size in GB
        """
        return self._disk

    @disk.setter
    def disk(self, disk):
        """
        Sets the disk size in GB
        """
        self._disk = disk

    @property
    def walltime(self):
        """
        Returns the maximum runtime in mins
        """
        return self._walltime

    @walltime.setter
    def walltime(self, walltime):
        """
        Sets the maximum runtime in mins
        """
        self._walltime = walltime

    @property
    def tasks(self):
        """
        Gets the list of tasks
        """
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        """
        Sets the full list of tasks
        """
        self._tasks = tasks

    def add_task(self, task):
        """
        Appends a task
        """
        self._tasks.append(task)

    @property
    def preemptible(self):
        """
        Gets whether the job is preemptible or not
        """
        return self._preemptible

    @preemptible.setter
    def preemptible(self, preemptible):
        """
        Sets whether the job is preemptible or not
        """
        self._preemptible = preemptible

    @property
    def labels(self):
        """
        Returns the list of labels
        """
        return self._labels

    @labels.setter
    def labels(self, labels):
        """
        Sets the list of labels
        """
        self._labels = labels

    def add_label(self, key, value):
        """
        Adds a label
        """
        self._labels[key] = value

    def add_output_file(self, output_file):
        """
        Adds an output file
        """
        self._output_files.append(output_file)

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

    @property
    def constraints(self):
        """
        Returns the placement constraints
        """
        return self._constraints

    @constraints.setter
    def constraints(self, constraints):
        """
        Sets the placement constraints
        """
        self._constraints = constraints

    def to_json(self):
        """
        Returns the job as JSON
        """
        data = {}
        for attr in self.attrs:
            value = getattr(self, attr, None)
            if value:
                if self.attrs[attr]:
                    if self.attrs[attr] not in data:
                        data[self.attrs[attr]] = {}
                    if attr == 'tasks':
                        tasks = []
                        for task in value:
                            tasks.append(task.to_json())
                        data['tasks'] = tasks
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
            if self.attrs[attr]:
                if self.attrs[attr] in data:
                    data_item = data[self.attrs[attr]]
            else:
                data_item = data
            if attr_json in data_item:
                setattr(self, attr, data_item[attr_json])


