class Dependency(object):
    """
    Dependency
    """
    def __init__(self, parent, children):
        self._parent = parent
        self._children = children

    @property
    def parent(self):
        """
        """
        return self._parent

    @parent.setter
    def parent(self, parent):
        """
        """
        self._parent = parent

    @property
    def children(self):
        """
        """
        return self._children

    @children.setter
    def children(self, children):
        """
        """
        self._children = children

    def to_dict(self):
        """
        """
        if self._parent and self._children:
            children = []
            for child in self._children:
                children.append(child.name)
            return {self._parent.name: children}
        return None
