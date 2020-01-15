from subprocess import Popen, PIPE
from sys import argv, platform
import logging
import shlex
import threading
from time import sleep

class ExperimentManage:
    EXPERIMENT_MANAGE_COMPLETE = 0
    EXPERIMENT_MANAGE_CREATING = 1
    EXPERIMENT_MANAGE_STARTING = 2
    EXPERIMENT_MANAGE_STOPPING = 3
    EXPERIMENT_MANAGE_REMOVING = 4
    EXPERIMENT_MANAGE_IDLE = 5
    
    EXPERIMENT_MANAGE_UNKNOWN = 10 
   
    EXPERIMENT_MANAGE_STATUS_TIMEOUT_VAL = -1
   
    POSIX = False
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        POSIX = True
      
    def __init__(self):
        self.readStatus = ExperimentManage.EXPERIMENT_MANAGE_UNKNOWN
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_UNKNOWN

    #abstractmethod
    def createExperiment(self, configname):
        raise NotImplementedError()

    #abstractmethod
    def startExperiment(self, configname):
        raise NotImplementedError()

    #abstractmethod
    def stopExperiment(self, configname):
        raise NotImplementedError()

    #abstractmethod
    def removeExperiment(self, configname):
        raise NotImplementedError()

    def getExperimentManageStatus(self):
        raise NotImplementedError()