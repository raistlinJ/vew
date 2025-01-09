from subprocess import Popen, PIPE
from sys import argv, platform
import logging
import shlex
import threading
import time

class ChallengesManage:
    CHALLENGES_MANAGE_COMPLETE = 0
    CHALLENGES_MANAGE_CREATING = 1
    CHALLENGES_MANAGE_REMOVING = 2
    CHALLENGES_MANAGE_OPENING = 3
    CHALLENGES_MANAGE_REFRESHING = 5
    CHALLENGES_MANAGE_IDLE = 0
    
    CHALLENGES_MANAGE_UNKNOWN = 10 
   
    CHALLENGES_MANAGE_STATUS_TIMEOUT_VAL = -1
   
    POSIX = False
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        POSIX = True
      
    def __init__(self):
        self.readStatus = ChallengesManage.CHALLENGES_MANAGE_UNKNOWN
        self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_UNKNOWN

    #abstractmethod
    def createChallengess(self, configname):
        raise NotImplementedError()

    #abstractmethod
    def removeChallengess(self, configname):
        raise NotImplementedError()

    #abstractmethod
    def openChallenges(self, configname, experimentid, vmid):
        raise NotImplementedError()

    #abstractmethod
    def getChallengesManageStatus(self):
        raise NotImplementedError()

    