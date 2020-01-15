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
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_CREATING
        #call vmManage to make clones as specified in config file; wait and query the vmManage status, and then set the complete status
        jsondata = self.eco.getExperimentXMLFileData(configname)
        vmSet = jsondata["xml"]["testbed-setup"]["vm-set"]
        pathToVirtualBox = jsondata["xml"]["vbox-setup"]["path-to-vboxmanage"]
        numClones = int(vmSet["num-clones"])
        cloneSnapshots = vmSet["clone-snapshots"]
        linkedClones = vmSet["linked-clones"]
        baseGroupname = vmSet["base-groupname"]
        baseOutname = vmSet["base-outname"]
        vrdpBaseport = vmSet["vrdp-baseport"]

        logging.debug("path: " + str(pathToVirtualBox) + " numClones: " + str(numClones) + " linked: " + str(linkedClones) + " baseGroup: " + str(baseGroupname) + " baseOut: " + str(baseOutname) + "vrdpBase: " + str(vrdpBaseport))

        for vm in vmSet["vm"]: 
            vmName = vm["name"]
            internalnetNames = []
            logging.debug("runCreateExperiment(): working with vm: " + str(vmName))

            #Create clones as shown in the cit-gen create_workshop python script (preserving internal networks, etc.)
            if self.vmManage.getVMStatus(vmName) == None:
                logging.error("VM Name: " + str(vmName) + " does not exist; skipping...")
                continue
            #get names for clones
            myBaseOutname = baseOutname
            for i in range(1, numClones + 1):
                cloneVMName = vmName + myBaseOutname + str(i)
                cloneGroupName = "/" + baseGroupname + "/Unit" + str(i)
                internalnets = vm["internalnet-basename"]

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
                if isinstance(internalnets, list) == False:
                    internalnets = [internalnets]
                for internalnet in internalnets:
                    cloneNetName = str(internalnet) + str(myBaseOutname) + str(i)
                    self.vmManage.configureVMNet(cloneVMName, cloneNetNum, cloneNetName)
                    while self.vmManage.getManagerStatus()["readStatus"] != self.vmManage.MANAGER_IDLE:
                        logging.info("runCreateExperiment(): waiting for manager to finish query...")
                        time.sleep(1)
                    cloneNetNum += 1

                while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                    #waiting for vmmanager start vm to finish reading/writing...
                    logging.debug("runCreateExperiment(): waiting for vmmanager start vm to finish reading/writing...")
                    time.sleep(1)
                # vrdp setup
                vrdpEnabled = vm["vrdp-enabled"]
                if vrdpEnabled != None and vrdpEnabled == 'true':
                    #set interface to vrde
                    logging.debug("runCreateExperiment(): setting up vrdp for " + cloneVMName)
                    self.vmManage.enableVRDPVM(cloneVMName, str(vrdpBaseport))
                    while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                        #waiting for vmmanager start vm to finish reading/writing...
                        time.sleep(1)
                    vrdpBaseport = str(int(vrdpBaseport) + 1)                            
                # finally create a snapshot after the vm is setup
                self.vmManage.snapshotVM(cloneVMName)
                while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                    #waiting for vmmanager start vm to finish reading/writing...
                    time.sleep(1)
                logging.debug("runCreateExperiment(): finished setting up clone: " + cloneVMName)
        self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE                
        logging.debug("runCreateExperiment(): Complete...")

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
        # jsondata = self.eco.getExperimentXMLFileData(configname)
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

    def getExperimentVMNames(self, experimentname):
        logging.debug("getExperimentVMNames(): instantiated")
        jsondata = self.eco.getExperimentXMLFileData(experimentname)
        vms = jsondata["xml"]["testbed-setup"]["vm-set"]
        vmNames = []
        #TODO: may have to check if this is a list or a single item
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
    e = ExperimentManageVBox()

    e.createExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(1)
        logging.debug("Waiting for experiment create to complete...")

    # logging.info("Starting Experiment")
    # e.startExperiment("sample")
    # logging.debug("Experiment start complete.")    

    # #####---Stop Experiment Test#####
    # time.sleep(30)
    # logging.info("Stopping Experiment")
    # e.stopExperiment("sample")
    # logging.debug("Experiment stop complete.")    
