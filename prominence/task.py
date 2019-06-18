class ProminenceTask(object):
    """
    PROMINENCE task class
    """

    # List of all attribute names
    attrs = ['image',
             'cmd',
             'runtime',
             'env',
             'workdir',
             'type',
             'procs_per_node']

    # The key is the attribute name and the value is the JSON key
    attr_map = {'image':'image',
                'cmd':'cmd',
                'runtime':'runtime',
                'env':'env',
                'workdir':'workdir',
                'type':'type',
                'procs_per_node':'procsPerNode'}

    def __init__(self, image=None, cmd=None, runtime=None, env={}, workdir=None, type=None, procs_per_node=None):
        self._image = image
        self._cmd = cmd
        self._runtime = runtime
        self._workdir = workdir
        self._env = env
        self._type = type
        self._procs_per_node = procs_per_node

    @property
    def image(self):
        """
        Gets the container image
        """
        return self._image

    @image.setter
    def image(self, image):
        """
        Sets the container image
        """
        self._image = image

    @property
    def cmd(self):
        """
        Gets the command
        """
        return self._cmd

    @cmd.setter
    def cmd(self, cmd):
        """
        Sets the command
        """
        self._cmd = cmd

    @property
    def runtime(self):
        """
        Returns the container runtime
        """
        return self._runtime

    @runtime.setter
    def runtime(self, runtime):
        """
        Sets the container runtime
        """
        self._runtime = runtime

    @property
    def workdir(self):
        """
        Returns the container working directory
        """
        return self._workdir

    @workdir.setter
    def workdir(self, workdir):
        """
        Sets the container working directory
        """
        self._workdir = workdir

    @property
    def env(self):
        """
        Returns the list of environment variables to be set in the container
        """
        return self._env

    @env.setter
    def env(self, env):
        """
        Sets the list of environment variables to be set in the container
        """
        self._env = env

    def add_env(self, key, value):
        """
        Add an environment variable
        """
        self._env[key] = value

    @property
    def type(self):
        """
        Returns the type of job
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of job ('basic', 'openmpi', 'mpich')
        """
        self._type = type

    @property
    def procs_per_node(self):
        """
        Returns the MPI processes per node
        """
        return self._procs_per_node

    @procs_per_node.setter
    def procs_per_node(self, procs_per_node):
        """
        Sets the MPI processes per node
        """
        self._procs_per_node = procs_per_node

    def to_json(self):
        """
        Returns the job as JSON
        """
        data = {}
        for attr in self.attrs:
            value = getattr(self, attr, None)
            if value:
                data[self.attr_map[attr]] = value
        return data

    def from_json(self, data):
        """
        Initializes task using JSON representation
        """
        for attr in self.attrs:
            attr_json = self.attr_map[attr]
            if attr_json in data:
                setattr(self, attr, data[attr_json])


