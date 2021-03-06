from setuptools import find_packages
from setuptools import setup

import codecs
import os
import re


def get_long_description():
    long_description = ""
    with open("README.md", "r") as file:
        long_description += file.read()

    long_description += "\n\n"

    with open("CHANGELOG.md", "r") as file:
        long_description += file.read()

    return long_description


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


def find_auther(*file_paths):
    path = os.path.join(here, *file_paths)
    with codecs.open(path, 'r') as fp:
        auther_file = fp.read()
        auther_match = re.search(r"__auther__ = ['\"]([^'\"]*)['\"]",
                                 auther_file, re.M)
        if auther_match:
            return auther_match.group(1)
        raise RuntimeError("Unable to find auther string.")


setup(
    name="wappstoiot",
    python_requires='>=3.6.0',
    version=find_version("wappstoiot", "__init__.py"),
    author=find_auther("wappstoiot", "__init__.py"),
    author_email="support@seluxit.com",
    license="Apache-2.0",
    description="Simple Wappsto Python user-interface to Wappsto IoT",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Wappsto/python-wappsto-iot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    packages=find_packages(),
    # tests_require=[
    #     'pytest',
    #     'tox'
    # ],
    install_requires=[
        'slxjsonrpc>=0.8.1',
        'pydantic>=1.6.1',
        'requests>=2.25.1'
    ],
    # entry_points={  # TODO: fix __main__.py to be optional.
    #     "console_scripts": "wappstoiot=wappstoiot:__main__"
    # },
    # extras_require={  # TODO: fix __main__.py to be optional.
    #     "cli": [
    #         'requests',
    #     ]
    # },
)
