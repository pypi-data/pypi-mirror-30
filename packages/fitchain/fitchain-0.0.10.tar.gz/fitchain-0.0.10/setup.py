import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "fitchain",
    version = "0.0.10",
    author = "Fitchain",
    author_email = "code@fitchain.io",
    description = ("Fitchain Python Client"),
    license = "Proprietary",
    keywords = "fitchain data client",
    url = "https://bitbucket.org/fitchain/fitchain-sdk-python",
    packages=['fitchain'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    install_requires=[
        'pandas',
        'numpy',
        'faker',
        'requests',
        'pyyaml',
        'joblib',
    ],
)