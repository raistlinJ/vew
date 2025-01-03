from subprocess import Popen, PIPE
from sys import argv, platform
import logging
import shlex
import threading
import time

class PackageManage:
    PACKAGE_MANAGE_COMPLETE = 0
    PACKAGE_MANAGE_IMPORTING = 1
    PACKAGE_MANAGE_EXPORTING = 2
    PACKAGE_MANAGE_IDLE = 3
    
    PACKAGE_MANAGE_UNKNOWN = 10 
   
    PACKAGE_MANAGE_STATUS_TIMEOUT_VAL = -1
   
    POSIX = False
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        POSIX = True
      
    def __init__(self):
        self.readStatus = PackageManage.PACKAGE_MANAGE_UNKNOWN
        self.writeStatus = PackageManage.PACKAGE_MANAGE_UNKNOWN

    #abstractmethod
    def importPackage(self, resfilename, runVagrantProvisionScript):
        raise NotImplementedError()

    #abstractmethod
    #TODO -- eventually, should be able to package multiple config files into a single res file
    def exportPackage(self, experimentname, exportpath):
        raise NotImplementedError()

    #abstractmethod
    def getPackageManageStatus(self):
        raise NotImplementedError()