import re
import setuptools

with open('prominence/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
fd.read(), re.MULTILINE).group(1)

setuptools.setup(
    name="prominence",
    version=version,
    author="Andrew Lahiff",
    author_email="andrew.lahiff@ukaea.uk",
    description="PROMINENCE CLI for managing batch jobs running across clouds",
    url="https://alahiff.github.io/prominence/",
    platforms=["any"],
    install_requires=["requests"],
    package_dir={'': '.'},
    scripts=["bin/prominence"],
    packages=['prominence'],
    package_data={"": ["README.md"]},
)
