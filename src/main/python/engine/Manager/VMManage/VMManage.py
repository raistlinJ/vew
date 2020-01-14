from subprocess import Popen, PIPE
from sys import argv, platform
import logging
import shlex
import threading
from time import sleep

class VMManage:
    VM_SETUP_COMPLETE = 0
    VM_SETUP_NONE = 1
    VM_SETUP_UNKNOWN = -1
       
    MANAGER_READING = 2
    MANAGER_IDLE = 3
    MANAGER_WRITING = 4
    
    MANAGER_UNKNOWN = 10 
   
    MANAGER_STATUS_TIMEOUT_VAL = 11
   
    POSIX = False
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        POSIX = True
      
    def __init__(self):
        self.vms = {} #dict of VM()
        self.readStatus = VMManage.MANAGER_UNKNOWN
        self.writeStatus = VMManage.MANAGER_UNKNOWN

    #abstractmethod
    def getManagerStatus(self):
        raise NotImplementedError()
    
    #abstractmethod
    def getVMStatus(self, vmName):
        raise NotImplementedError()

    #abstractmethod
    def refreshAllVMInfo(self):
        raise NotImplementedError()

    #abstractmethod
    def refreshVMInfo(self):
        raise NotImplementedError()

    #abstractmethod
    def startVM(self, vmName):
        raise NotImplementedError()

    #abstractmethod
    def suspendVM(self, vmName):
        raise NotImplementedError()

    #abstractmethod
    def stopVM(self, vmName):
        raise NotImplementedError()

#TODO:
#    def runVMCommand(self, VMName, commandString):
#        raise NotImplementedError()

    def importVM(self, filepath):
        raise NotImplementedError()

    def snapshotVM(self, vmName):
        raise NotImplementedError()

    def exportVM(self, vmName, filepath):
        raise NotImplementedError()

#TODO:
#    def cloneVM(self, vmName, cloneName):
#        raise NotImplementedError()

#TODO:
#    def removeVM(self, vmName):
#        raise NotImplementedError()
