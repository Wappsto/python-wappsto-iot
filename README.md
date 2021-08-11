Wappsto IoT
===============================================================================

[![Build Status](https://travis-ci.com/Wappsto/python-wappsto-iot.svg?branch=master)](https://travis-ci.com/Wappsto/python-wappsto-iot)
[![Coverage Status](https://coveralls.io/repos/github/Wappsto/python-wappsto-iot/badge.svg?branch=master)](https://coveralls.io/github/Wappsto/python-wappsto-iot?branch=master)

The wappsto module provide a simple python interface to [wappsto.com](https://wappsto.com/) for easy Prototyping.


## Prerequisites

A [wappsto.com](https://wappsto.com/) Account, that the device can connect to.

The wappsto module requires two things: A set of certificates for authentication and the JSON data model for representing your data and structure of your physical device. 
The certificates provides the physical device the secure connection to wappsto.com.
The data model provides context and structure for the data stored at wappsto.com and systematic handling of your device. It is an instance of our Unified Data Model (UDM) specifying the structure of your network, devices, values and their states. Be sure to read more about the UDM [here](https://documentation.wappsto.com) before moving on.


## Getting Started

Working examples of usage can be found in the [example folder](./example).

The following explains the example code found in [info.py](./example/info.py). 

<!-- Go through the examples! -->

## Installation using pip

The wappsto module can be installed using PIP (Python Package Index) as follows:

```bash
$ pip install -U wappsto_iot
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details.
