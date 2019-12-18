import logging
import time
import sys, traceback
import threading
from engine.Manager.ExperimentManage.ExperimentManage import ExperimentManage
from engine.Manager.VMManage.VMManage import VMManage
from engine.Manager.VMManage.VBoxManage import VBoxManage
from engine.Manager.VMManage.VBoxManageWin import VBoxManageWin

class ExperimentManageVBox(ExperimentManage):
    def __init__(self):
        logging.debug("ExperimentManageVBox(): instantiated")
        ExperimentManage.__init__(self)
        #Create an instance of vmManage
        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            self.vmManage = VBoxManage()
        else:
            self.vmManage = VBoxManageWin()
        self.vmManage.refreshAllVMInfo()
        while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE:
            #waiting for manager to finish query...
            time.sleep(1)

    #abstractmethod
    def createExperiment(self, configfilename):
        logging.debug("createExperiment(): instantiated")
        t = threading.Thread(target=self.runCreateExperiment, args=(configfilename,))
        t.start()
        return 0

    def runCreateExperiment(self, configfilename):
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_CREATING
        #call vmManage to make clones as specified in config file; wait and query the vmManage status, and then set the complete status
        #TODO: self.vmManage.cloneVM("\"default\"")
        while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
            #waiting for vmmanager start vm to finish reading/writing...
            time.sleep(1)
        logging.debug("vmmanager create experiment complete...")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def startExperiment(self, configfilename):
        logging.debug("startExperiment(): instantiated")
        t = threading.Thread(target=self.runStartExperiment, args=(configfilename,))
        t.start()
        return 0

    def runStartExperiment(self, configfilename):
        logging.debug("runStartExperiment(): instantiated")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_STARTING
        #call vmManage to start clones as specified in config file; wait and query the vmManage status, and then set the complete status
        self.vmManage.startVM("\"default\"")
        while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
            #waiting for vmmanager start vm to finish reading/writing...
            time.sleep(1)
        logging.debug("vmmanager start experiment complete...")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def stopExperiment(self, configfilename):
        logging.debug("stopExperiment(): instantiated")
        t = threading.Thread(target=self.runStopExperiment, args=(configfilename,))
        t.start()
        return 0

    def runStopExperiment(self, configfilename):
        logging.debug("runStopExperiment(): instantiated")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_STOPPING
        #call vmManage to stop clones as specified in config file; wait and query the vmManage status, and then set the complete status
        self.vmManage.stopVM("\"default\"")
        while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
            #waiting for manager to finish reading/writing...
            time.sleep(1)
        logging.debug("vmmanager stop experiment complete...")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def removeExperiment(self, configfilename):
        logging.debug("removeExperiment(): instantiated")
        t = threading.Thread(target=self.runRemoveExperiment, args=(configfilename,))
        t.start()
        return 0
        
    def runRemoveExperiment(self, configfilename):
        logging.debug("runRemoveExperiment(): instantiated")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_REMOVING
        #call vmManage to remove clones as specified in config file; wait and query the vmManage status, and then set the complete status
        #TODO: self.vmManage.removeVM("\"default\"")
        while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
            #waiting for manager to finish reading/writing...
            time.sleep(1)
        logging.debug("vmmanager remove experiment complete...")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    def getExperimentManageStatus(self):
        logging.debug("getExperimentManageStatus(): instantiated")
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus}

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    logging.debug("Instantiating Engine")
    e = ExperimentManageVBox()

    logging.debug("starting experiment")
    e.startExperiment("")