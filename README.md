# The Reproducible Experimentation System (RES)
## Table of Contents
- [The Reproducible Experimentation System (RES)](#the-reproducible-experimentation-system-res)
    - [Description](#description)
    - [Limitations](#limitations)
    - [Installation](#installation)
        - [Requirements](#requirements)
        - [Windows](#windows)
    - [Run The GUI](#run-the-gui)
    - [Run Engine Tests](#run-engine-tests)
    - [Troubleshooting](#troubleshooting)

### Description
RES is a wrapper system that enables analysts and researchers to easily create, package, and execute experiments that are generated using virtual machines.

The current version of RES supports VirtualBox machines. 

### Limitations
* The system currently does not allow entry of custom VM commands. This feature is forthcoming.

### Installation
RES has been tested on:
* Windows 10 (64-bit)
* Ubuntu 16.04 LTE (64-bit)

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

To run the GUI, follow the steps in [Run the GUI](#run-the-gui).
To run the engine tests, follow the steps in [Run Engine Tests](#run-engine-tests).


### Run the GUI
Navigate to the folder where you downloaded res and activate the virtualenv container
```
cd res
venv\Scripts\activate
```
Start the GUI
```
fbs run
```
A sample RES file can be downloaded [here](http://bit.ly/2TtRLiX). After downloading the file, right-click and select to Import the file.

### Run Engine Tests
A driver program is included that will demonstrate several of the functions provided by RES.

Download the Sample RES file from [here](http://bit.ly/2TtRLiX) and save it into the following directory
```
res/src/main/python/ExperimentData/samples/
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
