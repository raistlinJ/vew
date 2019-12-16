#!/usr/bin/env python

from subprocess import Popen, PIPE
from sys import argv, platform
import logging
import shlex
import threading
from time import sleep

class ConnectionManager:
    CONNECTION_MANAGE_COMPLETE = 0
    CONNECTION_MANAGE_CREATING = 7
    CONNECTION_MANAGE_REMOVING = 8
    CONNECTION_MANAGE_IDLE = 9
    
    CONNECTION_MANAGE_UNKNOWN = 10 
   
    CONNECTION_MANAGE_STATUS_TIMEOUT_VAL = -1
   
    POSIX = False
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        POSIX = True
      
    def __init__(self):
        pass

    #abstractmethod
    def createConnections(self, configfilename):
        raise NotImplementedError()

    #abstractmethod
    def removeConnections(self, configfilename):
        raise NotImplementedError()

    #abstractmethod
    def viewConnections(self, configfilename, experimentNum, vmNum):
        raise NotImplementedError()

    #abstractmethod
    def getConnectionManagerStatus(self):
        raise NotImplementedError()

    