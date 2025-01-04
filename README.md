# The Reproducible Experimentation System (RES)
## Table of Contents
- [The Reproducible Experimentation System (RES)](#the-reproducible-experimentation-system-res)
    - [Description](#description)
    - [Limitations](#limitations)
    - [Installation](#installation)
        - [Requirements](#requirements)
        - [Windows](#windows)
        - [Linux](#linux)
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
* Windows 10+ (64-bit)
* Ubuntu 16.04+ LTE (64-bit)

##### Requirements
* [Python 3.6 (64-bit) - Python 3.9 ](https://www.python.org/downloads/release/python-360/) (Note that RES does not work with Python 3.12 due to double-inheritance issues in the console handler code). It is recommended to use conda with a Python 3.9 virtual environment.

* [VirtualBox 6.1.6](https://www.virtualbox.org/wiki/Downloads) or VMWare Workstation 17+
* [Several Other Python packages] (see requirements.txt)
##### Windows
Clone the source and then cd into the directory:
```
git clone https://github.com/ARL-UTEP-OC/res
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

##### Linux
Setup and activate the virtualenv container
```
python3 -m venv venv
```
Clone RES repo 
```  
git clone https://github.com/ARL-UTEP-OC/res
cd res
```
Activate the venv and install python dependencides
```
source venv/bin/activate
pip3 install -r requirements.txt
```

To run the GUI, follow the steps in [Run the GUI](#run-the-gui).
To run the engine tests, follow the steps in [Run Engine Tests](#run-engine-tests).

#### VMware Workstation Special Considerations
By default promiscous mode is disabled for virtual machines. To enable this, open the following file /etc/init.d/vmware

Change the vmwareStartVmnet() function as follows:
```
vmwareStartVmnet() {
   vmwareLoadModule $vnet
   "$BINDIR"/vmware-networks --start >> $VNETLIB_LOG 2>&1
   chmod a+rw /dev/vmnet*
}
```

### Run the GUI
Navigate to the folder where you downloaded res and activate the virtualenv container
```
cd res
```
##### Linux
```
source venv\bin\activate
```
##### Windows
```
venv\Scripts\activate
```
##### Both
Start the GUI
```
python main.py
```
A sample RES file is included in the samples folder. In the GUI, right-click in the left pane and select to Import the file.

### Run Engine Tests
A driver program is included that will demonstrate several of the functions provided by RES.

Import the sample res file in the samples folder.

In the terminal, activate the virtualenv container
```
cd res
(Windows)
venv\Scripts\activate
(Linux)
source venv\bin\activate
```
Run the Engine Tests:
```
cd src/main/python/
python TestEngine.py
```

### Troubleshooting

Please contribute!
