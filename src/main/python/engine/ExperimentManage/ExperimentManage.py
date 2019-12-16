#!/usr/bin/env python

from subprocess import Popen, PIPE
from sys import argv, platform
import logging
import shlex
import threading
from time import sleep

class ExperimentManager:
    EXPERIMENT_MANAGE_COMPLETE = 0
    EXPERIMENT_MANAGE_SETUP = 7
    EXPERIMENT_MANAGE_STARTING = 8
    EXPERIMENT_MANAGE_STOPPING = 8
    EXPERIMENT_MANAGE_IDLE = 9
    
    EXPERIMENT_MANAGE_UNKNOWN = 10 
   
    EXPERIMENT_MANAGE_STATUS_TIMEOUT_VAL = -1
   
    POSIX = False
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        POSIX = True
      
    def __init__(self):
        pass

    #abstractmethod
    def setupExperiment(self, configfilename):
        raise NotImplementedError()

    #abstractmethod
    def startExperiment(self, configfilename):
        raise NotImplementedError()

    #abstractmethod
    def stopExperiment(self, configfilename):
        raise NotImplementedError()

    #abstractmethod
    def removeExperiment(self, configfilename):
        raise NotImplementedError()