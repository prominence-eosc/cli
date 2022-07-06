import base64
import os

class InputFile(object):
    """
    Input file
    """
    def __init__(self, filename, content=None):
        self._input_file = filename
        self._content = content

    def to_dict(self):
        """
        JSON representation
        """
        if not self._content:
            with open(self._input_file, 'rb') as fh:
                data = {'filename': os.path.basename(self._input_file),
                        'content': base64.b64encode(fh.read()).decode("utf-8")}
        else:
            data = {'filename': os.path.basename(self._input_file),
                    'content': base64.b64encode(bytes(self._content, "utf-8")).decode("utf-8")}

        return data
