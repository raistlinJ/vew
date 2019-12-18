# The Reproducible Experimentation System (RES)
## Table of Contents
- [The Reproducible Experimentation System (RES)](#the-reproducible-experimentation-system-res)
  - [Table of Contents](#table-of-contents)
    - [Description](#description)
    - [Limitations](#limitations)
    - [Installation](#installation)
        - [Requirements](#requirements)
        - [Windows](#windows)
    - [Run Tests](#run-tests)
    - [Troubleshooting](#troubleshooting)

### Description
RES is a wrapper system that enables analysts and researchers to easily create, package, and execute experiments that are generated using virtual machines.

The current version of RES supports VirtualBox machines. 

### Limitations
* Currently the system only consists of a few working functions; it is in very early stages. 

The project is actively and intensively being developed.

### Installation
RES has been tested on:
* Ubuntu 16.04 LTE (64-bit)
* Windows 10 (64-bit)

##### Requirements
* [Python 3.7.3 (64-bit) ](https://www.python.org/downloads/release/python-373/)
* [VirtualBox 6.x](https://www.virtualbox.org/wiki/Downloads)
* [Several Other Python packages] (see requirements.txt)
##### Windows
Clone the source and then cd into the directory:
```
git clone https://github.com/raistlinJ/res
cd res
```
Setup and activate the virtualenv container
```
python -m venv venv
venv\Scripts\activate
```
Install the res python dependencies
```
pip install -r requirements.txt
```

To run the tests, follow the steps in [Run Tests](#run-tests).

### Run Tests
A driver program is included that will demonstrate several of the functions provided by RES.

Download the Sample VMs from [here](http://bit.ly/2Pzdqnx) and save them into the following directory
```
res/src/main/python/ExperimentData/sample/VMs
```
Activate the virtualenv container
```
cd res
venv\Scripts\activate
```
Run the Engine Tests:
```
cd src/main/python/
python TestEngine.py
```

### Troubleshooting

RES is stil under development, please bear with us and contribute!