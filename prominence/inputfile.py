import base64
import os

class InputFile(object):
    """
    Input file
    """
    def __init__(self, filename):
        self._input_file = filename

    def json(self):
        """
        JSON representation
        """
        with open(self._input_file, 'rb') as fh:
            data = {'filename': os.path.basename(self._input_file),
                    'content': base64.b64encode(fh.read()).decode("utf-8")}
            return data

