import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

setup(
    name = "kitchen_sink_logger",
    version = "0.0.4",
    author = "Troy Larson",
    author_email = "troylar@gmail.com",
    description = ("Easily log everything, including the kitchen sink"),
    license = "BSD",
    keywords = "logging",
    url = "http://packages.python.org/an_example_pypi_project",
    packages=find_packages(),
    long_description='here',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
