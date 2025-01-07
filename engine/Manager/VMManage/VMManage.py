from subprocess import Popen, PIPE
from sys import argv, platform
import logging
import shlex
import threading
import time

class VMManage:
    MANAGER_IDLE = 0
    MANAGER_WRITING = 1
    MANAGER_READING = 2
    MANAGER_STATUS_TIMEOUT_VAL = 11

    VM_SETUP_COMPLETE = 0
    VM_SETUP_NONE = 1
    VM_SETUP_UNKNOWN = -2
          
    POSIX = False
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        POSIX = True
      
    def __init__(self):
        self.vms = {} #dict of VM()
        self.readStatus = VMManage.MANAGER_IDLE
        self.writeStatus = VMManage.MANAGER_IDLE
        self.guestThreadStatus = VMManage.MANAGER_IDLE
        self.activeTaskCount = 0

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
    def pauseVM(self, vmName):
        raise NotImplementedError()

    #abstractmethod
    def snapshotVM(self, vmName):
        raise NotImplementedError()

    #abstractmethod
    def suspendVM(self, vmName):
        raise NotImplementedError()

    #abstractmethod
    def stopVM(self, vmName):
        raise NotImplementedError()

    def guestCommands(self, VMName, cmds):
        raise NotImplementedError()

    def importVM(self, filepath):
        raise NotImplementedError()

    def snapshotVM(self, vmName):
        raise NotImplementedError()

    def exportVM(self, vmName, filepath):
        raise NotImplementedError()

    def cloneVM(self, vmName, cloneName):
        raise NotImplementedError()

    def removeVM(self, vmName):
        raise NotImplementedError()
