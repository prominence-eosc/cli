# PROMINENCE Command Line Interface

[![PyPI version shields.io](https://img.shields.io/pypi/v/prominence.svg)](https://pypi.python.org/pypi/ansicolortags/)

The PROMINENCE CLI presents a simple batch-system style interface to PROMINENCE. It is written in Python and works with both Python 2.x and 3.x. There are a number of ways the PROMINENCE CLI can be installed using pip.

## With sudo or root access
The PROMINENCE CLI can be installed on a host by typing the following:
```
sudo pip install prominence
```

## As a normal user without using virtualenv
The PROMINENCE CLI can be installed in a user's home directory by running:
```
pip install --user prominence
```
and then ensuring that `$HOME/.local/bin` is added to your `PATH`.

## As a normal user using virtualenv
If `virtualenv` is not available it can be installed in a user's home directory by typing:
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user
pip install --user virtualenv
```
The PROMINENCE CLI can be installed in a new virtual environment, e.g.
```
virtualenv ~/.virtualenvs/prominence
source ~/.virtualenvs/prominence/bin/activate
pip install prominence
```

See https://prominence-eosc.github.io/docs/ for more information.
