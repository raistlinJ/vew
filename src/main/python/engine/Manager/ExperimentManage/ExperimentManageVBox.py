import logging
import time
import sys, traceback
import threading
import json
from engine.Manager.ExperimentManage.ExperimentManage import ExperimentManage
from engine.Manager.VMManage.VMManage import VMManage
from engine.Manager.VMManage.VBoxManage import VBoxManage
from engine.Manager.VMManage.VBoxManageWin import VBoxManageWin
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO

class ExperimentManageVBox(ExperimentManage):
    def __init__(self, initializeVMManage = True):
        logging.debug("ExperimentManageVBox(): instantiated")
        ExperimentManage.__init__(self)
        #Create an instance of vmManage
        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            self.vmManage = VBoxManage()
        else:
            self.vmManage = VBoxManageWin()
        if initializeVMManage:
            self.vmManage.refreshAllVMInfo()
        self.eco = ExperimentConfigIO()
        #TODO: need to add an interface for updating status... probably in the engine main interface
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
        #TODO: 
        # jsondata = self.eco.getExperimentXMLFileData(configfilename)
        # vms = jsondata["xml"]["testbed-setup"]["vm-set"]
        # for name in vms["vm"]: 
        #     Create clones as shown in the cit-gen create_workshop python script (preserving internal networks, etc.)   
        #     self.vmManage.cloneVM(name["name"])

        while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
            #waiting for vmmanager start vm to finish reading/writing...
            time.sleep(1)
        logging.debug("vmmanager create experiment complete...")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def startExperiment(self, configname):
        logging.debug("startExperiment(): instantiated")
        t = threading.Thread(target=self.runStartExperiment, args=(configname,))
        t.start()
        return 0

    def runStartExperiment(self, configname):
        logging.debug("runStartExperiment(): instantiated")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_STARTING
        #call vmManage to start clones as specified in config file; wait and query the vmManage status, and then set the complete status
        jsondata = self.eco.getExperimentXMLFileData(configname)
        vms = jsondata["xml"]["testbed-setup"]["vm-set"]
        for name in vms["vm"]:    
            self.vmManage.startVM(name["name"])
            while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                #waiting for vmmanager start vm to finish reading/writing...
                time.sleep(1)
        logging.debug("vmmanager start experiment complete...")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def stopExperiment(self, configname):
        logging.debug("stopExperiment(): instantiated")
        t = threading.Thread(target=self.runStopExperiment, args=(configname,))
        t.start()
        return 0

    def runStopExperiment(self, configname):
        logging.debug("runStopExperiment(): instantiated")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_STOPPING
        #call vmManage to stop clones as specified in config file; wait and query the vmManage status, and then set the complete status
        jsondata = self.eco.getExperimentXMLFileData(configname)
        vms = jsondata["xml"]["testbed-setup"]["vm-set"]
        for name in vms["vm"]:    
            self.vmManage.stopVM(name["name"])
            while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                #waiting for manager to finish reading/writing...
                time.sleep(1)
        logging.debug("vmmanager stop experiment complete...")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def removeExperiment(self, configname):
        logging.debug("removeExperiment(): instantiated")
        t = threading.Thread(target=self.runRemoveExperiment, args=(configname,))
        t.start()
        return 0
        
    def runRemoveExperiment(self, configname):
        logging.debug("runRemoveExperiment(): instantiated")
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_REMOVING
        #call vmManage to remove clones as specified in config file; wait and query the vmManage status, and then set the complete status
        #TODO: 
        # jsondata = self.eco.getExperimentXMLFileData(configfilename)
        # vms = jsondata["xml"]["testbed-setup"]["vm-set"]
        # for name in vms["vm"]:  
        #     #only remove the clones, not the original vms!  
        #     self.vmManage.removeVM(name["name"])

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

    logging.info("Starting Experiment")
    e.startExperiment("sample")
    logging.debug("Experiment start complete.")    

    #####---Stop Experiment Test#####
    time.sleep(30)
    logging.info("Stopping Experiment")
    e.stopExperiment("sample")
    logging.debug("Experiment stop complete.")    
