from prominence import ProminenceClient

class Artifact(object):
    """
    Artifact
    """
    def __init__(self, name, directory_name=None, mount_point=None):
        self._name = name
        self._directory_name = directory_name
        self._mount_point = mount_point

    def upload(self, filename):
        """
        Upload file
        """
        client = ProminenceClient(authenticated=True)
        client.upload(self._name, filename)

    def to_dict(self):
        """
        JSON representation
        """
        data = {'url': self._name}
        if self._directory_name and self._mount_point:
            data['mountpoint'] = '%s:%s' % (self._directory_name, self._mount_point)

        return data
