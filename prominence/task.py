class Task(object):
    """
    Task
    """
    def __init__(self):
        self._image = None
        self._runtime = None
        self._command = None
        self._type = None
        self._workdir = None
        self._env = None
        self._procs_per_node = 0

    @property
    def image(self):
        """
        Return the image
        """
        return self._image

    @image.setter
    def image(self, image):
        """
        Set the image
        """
        self._image = image

    @property
    def procs_per_node(self):
        """
        Return the procs per node
        """
        return self._procs_per_node

    @procs_per_node.setter
    def procs_per_node(self, procs_per_node):
        """
        Set the procs per node
        """
        self._procs_per_node = procs_per_node

    @property
    def runtime(self):
        return self._runtime

    @runtime.setter
    def runtime(self, runtime):
        self._runtime = runtime

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, command):
        self._command = command

    @property                       
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def workdir(self):
        return self._workdir

    @workdir.setter
    def workdir(self, workdir):
        self._workdir = workdir

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, env):
        self._env = env

    def to_dict(self):
        data = {}
        data['image'] = self._image
        if self._command:
            data['cmd'] = self._command

        if self._runtime:
            data['runtime'] = self._runtime
        else:
            data['runtime'] = 'singularity'
            if '.tar' in self._image or '.tgz' in self._image:
                data['runtime'] = 'udocker'

        if self._workdir:
            data['workdir'] = self._workdir
        if self._type:
            data['type'] = self._type
        if self._env:
            data['env'] = self._env
        if self._procs_per_node > 0:
            data['procsPerNode'] = self._procs_per_node
        return data
