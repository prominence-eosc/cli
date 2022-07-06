class Notification(object):
    """
    Notification
    """
    def __init__(self, event=None, type=None):
        self._event = event
        self._type = type

    @property
    def event(self):
        """
        """
        return self._event

    @event.setter
    def event(self, event):
        """
        """
        self._event = event

    @property
    def type(self):
        """
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        """
        self._type = type

    def to_dict(self):
        """
        """
        if self._event and self._type:
            return {'event': self._event, 'type': self._type}
        return None
