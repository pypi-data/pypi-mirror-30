from setuptools import setup

setup(
    name = "fitchain",
    version = "0.0.11",
    author = "Fitchain",
    author_email = "code@fitchain.io",
    description = ("Fitchain Python Client"),
    license = "Proprietary",
    keywords = "fitchain data client",
    url = "https://bitbucket.org/fitchain/fitchain-sdk-python",
    packages=['fitchain'],
    long_description="""
This repo implements the SDK to manage projects and models on a local fitchain pod

### Feedback ###
Reach out and tell us how we can improve this SDK to make it easier for you to work with the pod and build your models. 

You may always drop us a mail at ```code@fitchain.io``` 
""",
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