import base64
import os

class InputFile(object):
    """
    Input file
    """
    def __init__(self, filename=None):
        self._input_file = None
        if filename:
            self._input_file = filename

    def json(self):
        """
        JSON representation
        """
        if not self._input_file:
            return []

        with open(self._input_file, 'rb') as fh:
            data = {'filename': os.path.basename(self._input_file),
                    'content': base64.b64encode(fh.read()).decode("utf-8")}
            return data

