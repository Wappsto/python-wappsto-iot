from setuptools import find_packages
from setuptools import setup

import codecs
import os
import re


with open("README.md", "r") as file:
    long_description = file.read()


here = os.path.abspath(os.path.dirname(__file__))


def find_version(*file_paths):
    path = os.path.join(here, *file_paths)
    with codecs.open(path, 'r') as fp:
        version_file = fp.read()
        version_match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]",
                                  version_file, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


setup(
    name="wappstoiot",
    version=find_version("wappstoiot", "__init__.py"),
    author="Seluxit A/S",
    author_email="support@seluxit.com",
    license="Apache-2.0",
    description="Simple Wappsto Python user-interface to the Wappsto devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Wappsto/python-wappstoiot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(),
    # package_data={
    #     # 'slxjsonrpc': ['jsonrpc.pyi'],
    # },
    # tests_require=[
    #     'pytest',
    #     'tox'
    # ],
    install_requires=[
       'slxjsonrpc>=0.0.2',
       'rich',
    ],
    python_requires='>3.6.0',
)
