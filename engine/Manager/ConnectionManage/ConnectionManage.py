from subprocess import Popen, PIPE
from sys import argv, platform
import logging
import shlex
import threading
import time

class ConnectionManage:
    CONNECTION_MANAGE_COMPLETE = 0
    CONNECTION_MANAGE_CREATING = 1
    CONNECTION_MANAGE_REMOVING = 2
    CONNECTION_MANAGE_OPENING = 3
    CONNECTION_MANAGE_REFRESHING = 5
    CONNECTION_MANAGE_IDLE = 0
    
    CONNECTION_MANAGE_UNKNOWN = 10 
   
    CONNECTION_MANAGE_STATUS_TIMEOUT_VAL = -1
   
    POSIX = False
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        POSIX = True
      
    def __init__(self):
        self.readStatus = ConnectionManage.CONNECTION_MANAGE_UNKNOWN
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_UNKNOWN

    #abstractmethod
    def createConnections(self, configname):
        raise NotImplementedError()

    #abstractmethod
    def removeConnections(self, configname):
        raise NotImplementedError()

    #abstractmethod
    def openConnection(self, configname, experimentid, vmid):
        raise NotImplementedError()

    #abstractmethod
    def getConnectionManageStatus(self):
        raise NotImplementedError()

    