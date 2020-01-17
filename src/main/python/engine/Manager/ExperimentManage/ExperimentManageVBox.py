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
            while self.vmManage.getManagerStatus()["readStatus"] != self.vmManage.MANAGER_IDLE:
            #waiting for manager to finish query...
                time.sleep(1)
        self.eco = ExperimentConfigIO()

    #abstractmethod
    def createExperiment(self, configname):
        logging.debug("createExperiment(): instantiated")
        t = threading.Thread(target=self.runCreateExperiment, args=(configname,))
        t.start()
        return 0

    def runCreateExperiment(self, configname):
        logging.debug("runCreateExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_CREATING
            #call vmManage to make clones as specified in config file; wait and query the vmManage status, and then set the complete status
            self.vmManage.refreshAllVMInfo()
            while self.vmManage.getManagerStatus()["readStatus"] != self.vmManage.MANAGER_IDLE:
            #waiting for manager to finish query...
                time.sleep(1)
            clonevmjson = self.eco.getExperimentVMRolledOut(configname)

            for vm in clonevmjson.keys(): 
                vmName = vm

                logging.debug("runCreateExperiment(): working with vm: " + str(vmName))

                #Create clones as shown in the cit-gen create_workshop python script (preserving internal networks, etc.)
                if self.vmManage.getVMStatus(vmName) == None:
                    logging.error("VM Name: " + str(vmName) + " does not exist; skipping...")
                    continue
                #get names for clones
                for cloneinfo in clonevmjson[vm]:
                #for i in range(1, numClones + 1):
                    cloneVMName = cloneinfo["name"]
                    cloneGroupName = cloneinfo["group-name"]
                    internalnets = cloneinfo["networks"]
                    cloneSnapshots = cloneinfo["clone-snapshots"]
                    linkedClones = cloneinfo["linked-clones"]

                    logging.debug("vmName: " + str(vmName) + " cloneVMName: " + str(cloneVMName) + " cloneSnaps: " + str(cloneSnapshots) + " linked: " + str(linkedClones) + " cloneGroupName: " + str(cloneGroupName))
                    self.vmManage.cloneVM(vmName, cloneVMName, cloneSnapshots, linkedClones, cloneGroupName)
                    while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                        #waiting for vmmanager start vm to finish reading/writing...
                        logging.debug("runCreateExperiment(): waiting for vmmanager start vm to finish reading/writing...")
                        time.sleep(1)
                    # We added a VM, so we have to call refresh
                    logging.info("Refreshing after clone since we added a new VM")
                    self.vmManage.refreshAllVMInfo()
                    while self.vmManage.getManagerStatus()["readStatus"] != self.vmManage.MANAGER_IDLE:
                        logging.info("runCreateExperiment(): waiting for manager to finish query...")
                        time.sleep(1)
                    logging.info("Refreshing VMs Info - AFTER")
                    
                    # intnet setup
                    cloneNetNum = 1
                    logging.debug("Internal net names: " + str(internalnets))
                    for internalnet in internalnets:
                        self.vmManage.configureVMNet(cloneVMName, cloneNetNum, internalnet)
                        while self.vmManage.getManagerStatus()["readStatus"] != self.vmManage.MANAGER_IDLE:
                            logging.info("runCreateExperiment(): waiting for vmmanager to finish query...")
                            time.sleep(1)
                        cloneNetNum += 1

                    while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                        #waiting for vmmanager start vm to finish reading/writing...
                        logging.debug("runCreateExperiment(): waiting for vmmanager to finish reading/writing...")
                        time.sleep(1)
                    # vrdp setup
                    if "vrdpPort" in cloneinfo:
                        #set interface to vrde
                        logging.debug("runCreateExperiment(): setting up vrdp for " + cloneVMName)
                        self.vmManage.enableVRDPVM(cloneVMName, str(cloneinfo["vrdpPort"]))
                        while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                            #waiting for vmmanager start vm to finish reading/writing...
                            time.sleep(1)

                    # finally create a snapshot after the vm is setup
                    self.vmManage.snapshotVM(cloneVMName)
                    while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                        #waiting for vmmanager start vm to finish reading/writing...
                        time.sleep(1)
                    logging.debug("runCreateExperiment(): finished setting up clone: " + cloneVMName)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            logging.debug("runCreateExperiment(): Complete...")
        except Exception:
            logging.error("runCloneVM(): Error in runCreateExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def startExperiment(self, configname):
        logging.debug("startExperiment(): instantiated")
        t = threading.Thread(target=self.runStartExperiment, args=(configname,))
        t.start()
        return 0

    def runStartExperiment(self, configname):
        logging.debug("runStartExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_STARTING
            #call vmManage to start clones as specified in config file; wait and query the vmManage status, and then set the complete status
            clonevmjson = self.eco.getExperimentVMRolledOut(configname)
            for vm in clonevmjson.keys(): 
                vmName = vm
                logging.debug("runStartExperiment(): working with vm: " + str(vmName))
                #get names for clones and start them
                for cloneinfo in clonevmjson[vm]:
                    cloneVMName = cloneinfo["name"]
                    #Check if clone exists and then run it if it does
                    if self.vmManage.getVMStatus(vmName) == None:
                        logging.error("runStartExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                        continue
                    logging.debug("runStartExperiment(): Starting: " + str(vmName))
                    self.vmManage.startVM(cloneVMName)
                    while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                        #waiting for vmmanager start vm to finish reading/writing...
                        time.sleep(1)
            logging.debug("runStartExperiment(): Complete...")
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
        except Exception:
            logging.error("runStartExperiment(): Error in runStartExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def stopExperiment(self, configname):
        logging.debug("stopExperiment(): instantiated")
        t = threading.Thread(target=self.runStopExperiment, args=(configname,))
        t.start()
        return 0

    def runStopExperiment(self, configname):
        logging.debug("runStopExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_STOPPING
            #call vmManage to stop clones as specified in config file; wait and query the vmManage status, and then set the complete status
            clonevmjson = self.eco.getExperimentVMRolledOut(configname)
            for vm in clonevmjson.keys(): 
                vmName = vm
                logging.debug("runStopExperiment(): working with vm: " + str(vmName))
                #get names for clones and stop them
                for cloneinfo in clonevmjson[vm]:
                    cloneVMName = cloneinfo["name"]
                    #Check if clone exists and then run it if it does
                    if self.vmManage.getVMStatus(vmName) == None:
                        logging.error("runStopExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                        continue
                    logging.error("runStopExperiment(): Stopping: " + str(vmName))
                    self.vmManage.stopVM(cloneVMName)
                    while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                        #waiting for vmmanager stop vm to finish reading/writing...
                        time.sleep(1)
            logging.debug("runStopExperiment(): Complete...")
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
        except Exception:
            logging.error("runStopExperiment(): Error in runStopExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def removeExperiment(self, configname):
        logging.debug("removeExperiment(): instantiated")
        t = threading.Thread(target=self.runRemoveExperiment, args=(configname,))
        t.start()
        return 0
        
    def runRemoveExperiment(self, configname):
        logging.debug("runRemoveExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_REMOVING
            #call vmManage to remove clones as specified in config file; wait and query the vmManage status, and then set the complete status
            clonevmjson = self.eco.getExperimentVMRolledOut(configname)
            for vm in clonevmjson.keys(): 
                vmName = vm
                logging.debug("runRemoveExperiment(): working with vm: " + str(vmName))
                #get names for clones and remove them
                for cloneinfo in clonevmjson[vm]:
                    cloneVMName = cloneinfo["name"]
                    #Check if clone exists and then run it if it does
                    if self.vmManage.getVMStatus(vmName) == None:
                        logging.error("runRemoveExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                        continue
                    logging.error("runRemoveExperiment(): Removing: " + str(vmName))
                    self.vmManage.removeVM(cloneVMName)
                    while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                        #waiting for vmmanager stop vm to finish reading/writing...
                        time.sleep(1)
            logging.debug("runRemoveExperiment(): Complete...")
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
        except Exception:
            logging.error("runRemoveExperiment(): Error in runRemoveExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def restoreExperiment(self, configname):
        logging.debug("restoreExperimentStates(): instantiated")
        t = threading.Thread(target=self.runRestoreExperiment, args=(configname,))
        t.start()
        return 0    

    def runRestoreExperiment(self, configname):
        logging.debug("runRestoreExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_RESTORING
            #call vmManage to restore clones as specified in config file; wait and query the vmManage status, and then set the complete status
            clonevmjson = self.eco.getExperimentVMRolledOut(configname)
            for vm in clonevmjson.keys(): 
                vmName = vm
                logging.debug("runRestoreExperiment(): working with vm: " + str(vmName))
                #get names for clones and restore them
                for cloneinfo in clonevmjson[vm]:
                    cloneVMName = cloneinfo["name"]
                    #Check if clone exists and then run it if it does
                    if self.vmManage.getVMStatus(vmName) == None:
                        logging.error("runRestoreExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                        continue
                    logging.debug("runRestoreExperiment(): Restoring latest for : " + str(cloneVMName))
                    self.vmManage.restoreLatestSnapVM(cloneVMName)
                    while self.vmManage.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                        #waiting for vmmanager stop vm to finish reading/writing...
                        time.sleep(1)
            logging.debug("runRestoreExperiment(): Complete...")
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
        except Exception:
            logging.error("runRestoreExperiment(): Error in runRestoreExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    def getExperimentManageStatus(self):
        logging.debug("getExperimentManageStatus(): instantiated")
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus}

    def getExperimentVMNames(self, experimentname):
        logging.debug("getExperimentVMNames(): instantiated")
        jsondata = self.eco.getExperimentXMLFileData(experimentname)
        vms = jsondata["xml"]["testbed-setup"]["vm-set"]
        vmNames = []
        
        if isinstance(vms["vm"], list) == False:
            vms["vm"] = [vms["vm"]]
        for name in vms["vm"]:    
            vmNames.append(name["name"])
        return vmNames

    def getExperimentMaterialNames(self, experimentname):
        logging.debug("getExperimentMaterialNames(): instantiated")
        #TODO: implement this method

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    logging.debug("Instantiating Engine")
    e = ExperimentManageVBox(initializeVMManage=True)
    
    #####---Create Experiment Test#####
    logging.info("Creating Experiment")
    e.createExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(1)
        logging.debug("Waiting for experiment create to complete...")
    
    #####---Start Experiment Test#####
    logging.info("Starting Experiment")
    e.startExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(1)
        logging.debug("Waiting for experiment start to complete...")
    logging.debug("Experiment start complete.")    

    #####---Stop Experiment Test#####
    logging.info("Stopping Experiment")
    e.stopExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(1)
        logging.debug("Waiting for experiment stop to complete...")
    logging.debug("Experiment stop complete.")    
   
    #####---Restore Experiment Test#####
    logging.info("Stopping Experiment")
    e.restoreExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(1)
        logging.debug("Waiting for experiment stop to complete...")
    logging.debug("Experiment stop complete.")

    #####---Remove Experiment Test#####
    logging.info("Creating Experiment")
    e.removeExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(1)
        logging.debug("Waiting for experiment create to complete...")
