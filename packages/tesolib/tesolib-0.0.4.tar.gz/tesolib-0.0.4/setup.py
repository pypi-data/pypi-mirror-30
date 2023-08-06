import os
from setuptools import setup, find_packages


# Tesodev LTD STI 2018
# Please read README for detailed information
# This place is not for (very) long description
# But there should be some head information about the project
# Library starts below


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "tesolib",
    version = "0.0.4",
    author = "Tesodev",
    author_email = "kenan.kurt@tesodev.com",
    description = ("Test script for publish "
                                   "packages in PIPY"),
    license = "BSD",
    keywords = "tesodev, tesolib",
    url = "http://packages.python.org/tesolib",
    packages= find_packages(),
    long_description=read('README'),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)