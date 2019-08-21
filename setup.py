import re
import setuptools

with open('prominence/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="prominence",
    version=version,
    author="Andrew Lahiff",
    author_email="andrew.lahiff@ukaea.uk",
    description="PROMINENCE CLI for managing batch jobs running across clouds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://prominence-eosc.github.io/docs",
    platforms=["any"],
    install_requires=["requests", "PyJWT"],
    package_dir={'': '.'},
    scripts=["bin/prominence"],
    packages=['prominence'],
    package_data={"": ["README.md"]},
)
