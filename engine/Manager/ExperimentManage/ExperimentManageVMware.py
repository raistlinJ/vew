import logging
import time
import sys, traceback
import threading
import json
import os
from engine.Manager.ExperimentManage.ExperimentManage import ExperimentManage
from engine.Manager.VMManage.VMManage import VMManage
from engine.Manager.VMManage.VMwareManage import VMwareManage
from engine.Manager.VMManage.VMwareManageWin import VMwareManageWin
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO

class ExperimentManageVMware(ExperimentManage):
    def __init__(self, vmManage):
        logging.debug("ExperimentManageVMware(): instantiated")
        ExperimentManage.__init__(self)
        #Create an instance of vmManage
        self.vmManage = vmManage
        self.eco = ExperimentConfigIO.getInstance()
        self.vmstatus = {}


    #abstractmethod
    def createExperiment(self, configname, itype="", name=""):
        logging.debug("createExperiment(): instantiated")
        t = threading.Thread(target=self.runCreateExperiment, args=(configname, itype, name))
        t.start()
        #t.join()
        return 0

    def runCreateExperiment(self, configname, itype, name):
        logging.debug("runCreateExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_CREATING
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)
            status = self.vmManage.getManagerStatus()["writeStatus"]
            for i in range(1, numclones + 1):
                for vm in clonevmjson.keys():
                    vmName = vm
                    logging.debug("runCreateExperiment(): working with vm: " + str(vmName))
                    #Create clones preserving internal networks, etc.
                    if not os.path.exists(vmName):
                        logging.error("VM Name: " + str(vmName) + " does not exist; skipping...")
                        continue
                    refreshedVMName = False
                    #get names for clones
                    for cloneinfo in clonevmjson[vm]:
                        if cloneinfo["groupNum"] == str(i):
                            cloneVMName = cloneinfo["name"]
                            if cloneVMName not in validvmnames:
                                status = self.vmManage.getManagerStatus()["writeStatus"]
                                continue
                            cloneGroupName = cloneinfo["group-name"]
                            cloneSnapshots = cloneinfo["clone-snapshots"]
                            linkedClones = cloneinfo["linked-clones"]
                            internalnets = cloneinfo["networks"]

                            logging.debug("vmName: " + str(vmName) + " cloneVMName: " + str(cloneVMName) + " cloneSnaps: " + str(cloneSnapshots) + " linked: " + str(linkedClones) + " cloneGroupName: " + str(cloneGroupName))

                            # vrdp info
                            vrdpPort = None
                            if "vrdpPort" in cloneinfo:
                                #set interface to vrde
                                logging.debug("runCreateExperiment(): setting up vrdp for " + cloneVMName)
                                vrdpPort = str(cloneinfo["vrdpPort"])

                            # Clone; we want to refresh the vm info in case any new snapshots have been added, but only once
                            if refreshedVMName == False:
                                self.vmManage.cloneVMConfigAll(vmName, cloneVMName, cloneSnapshots, linkedClones, cloneGroupName, internalnets, vrdpPort, refreshVMInfo=True)
                                logging.info("vmname: " + vmName + " cloneVMName: " + cloneVMName )
                            else:
                                self.vmManage.cloneVMConfigAll(vmName, cloneVMName, cloneSnapshots, linkedClones, cloneGroupName, internalnets, vrdpPort, refreshVMInfo=False)
                                logging.info("vmname: " + vmName + " cloneVMName: " + cloneVMName )
                                refreshedVMName = True
                status = self.vmManage.getManagerStatus()["writeStatus"]
                while status != VMManage.MANAGER_IDLE:
                    #waiting for vmmanager clone vm to finish reading/writing...
                    logging.debug("runCreateExperiment(): waiting for vmmanager clone vm to finish reading/writing (cloning set)..." + str(status) + ":: " + str(i))
                    time.sleep(1)
                    status = self.vmManage.getManagerStatus()["writeStatus"]
                
                logging.debug("runCreateExperiment(): finished setting up " + str(numclones) + " clones")
                logging.debug("runCreateExperiment(): Complete...")
        except Exception:
            logging.error("runCloneVM(): Error in runCreateExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    def refreshExperimentVMInfo(self, configName):
        logging.debug("refreshExperimentVMInfo: refreshAllVMInfo(): instantiated")      
        t = threading.Thread(target=self.runRefreshExperimentVMInfo, args=(configName,))
        t.start()
        t.join()
        self.vmstatus = self.vmManage.getManagerStatus()["vmstatus"]

    def runRefreshExperimentVMInfo(self, configname):
        logging.debug("refreshExperimentVMInfo(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_REFRESHING
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, "", "", rolledoutjson)

            for vm in clonevmjson.keys():
                vmName = vm
                logging.debug("refreshExperimentVMInfo(): working with vm: " + str(vmName))
                #get names for clones
                for cloneinfo in clonevmjson[vm]:
                        cloneVMName = cloneinfo["name"]
                        if cloneVMName not in validvmnames:
                            continue
                        logging.debug("refreshExperimentVMInfo(): Refreshing: " + str(cloneVMName))
                        self.vmManage.refreshVMInfo(cloneVMName)
            while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                #waiting for vmmanager refresh vm to finish reading/writing...
                time.sleep(.1)
            logging.debug("refreshExperimentVMInfo(): Complete...")
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
        except Exception:
            logging.error("refreshExperimentVMInfo(): Error in refreshExperimentVMInfo(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def startExperiment(self, configname, itype="", name=""):
        logging.debug("startExperiment(): instantiated")
        t = threading.Thread(target=self.runStartExperiment, args=(configname,itype, name))
        t.start()
        t.join()
        return 0

    def runStartExperiment(self, configname, itype, name):
        logging.debug("runStartExperiment(): instantiated")
        try:
            #Will first clone the vms and then run their start commands if any
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_STARTING
            #call vmManage to start clones as specified in config file; wait and query the vmManage status, and then set the complete status
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)
            for i in range(1, numclones + 1):
                for vm in clonevmjson.keys(): 
                    vmName = vm
                    logging.debug("runStartExperiment(): working with vm: " + str(vmName))
                    #get names for clones and start them
                    for cloneinfo in clonevmjson[vm]:
                        if cloneinfo["groupNum"] == str(i):
                            cloneVMName = cloneinfo["name"]
                            if cloneVMName not in validvmnames:
                                continue
                            #Check if clone exists and then run it if it does
                            if not os.path.exists(cloneVMName):
                                logging.error("runStartExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                                continue
                            logging.debug("runStartExperiment(): Starting: " + str(vmName))
                            self.vmManage.startVM(cloneVMName)
            while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
            #waiting for vmmanager start vm to finish reading/writing...
                time.sleep(.1)
            #now that the VMs have started, we want to run the commands on each; no waiting needed
            for i in range(1, numclones + 1):
                for vm in clonevmjson.keys():
                    vmName = vm
                    logging.debug("runStartExperiment(): working with vm: " + str(vmName))
                    #get names for clones and start them
                    for cloneinfo in clonevmjson[vm]:
                        if cloneinfo["groupNum"] == str(i):
                            cloneVMName = cloneinfo["name"]
                            if cloneVMName not in validvmnames:
                                continue
                            #Check if clone exists and then run it if it does
                            if not os.path.exists(cloneVMName):
                                logging.error("runStartExperiment(): VM Name: " + str(cloneVMName) + " does not exist; skipping...")
                                continue
                            logging.debug("runStartExperiment(): command(s) setup on " + str(cloneVMName) )
                            #put all of the commands into a single list, based on sequence numbers:
                            if cloneinfo["startup-cmds"] != None:
                                startupCmds = cloneinfo["startup-cmds"]
                                startupDelay = cloneinfo["startup-cmds-delay"]
                                #format them into a list; based on execution order
                                orderedStartupCmds = []
                                for sequence in sorted(startupCmds):
                                    cmds = startupCmds[sequence]
                                    for mcmd in cmds:
                                        #from the tuple, just get the "exec" or command, not hypervisor
                                        #substitute out any template variables
                                        mcmd = (mcmd[0],mcmd[1].replace("{{RES_CloneName}}","\""+str(cloneVMName)+"\""))
                                        mcmd = (mcmd[0],mcmd[1].replace("{{RES_CloneNumber}}",str(i)))
                                        orderedStartupCmds.append(mcmd[1])
                                logging.debug("runStartExperiment(): sending command(s) for " + str(cloneVMName) + str(orderedStartupCmds))
                                self.vmManage.guestCommands(cloneVMName, orderedStartupCmds, startupDelay)
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

    def guestCmdsExperiment(self, configname, itype="", name=""):
        logging.debug("guestCmdsExperiment(): instantiated")
        t = threading.Thread(target=self.runGuestCmdsExperiment, args=(configname, itype, name))
        t.start()
        t.join()
        return 0

    def runGuestCmdsExperiment(self, configname, itype, name):
        logging.debug("runGuestCmdsExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMMANDING
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)
            for i in range(1, numclones + 1):
                for vm in clonevmjson.keys():
                    vmName = vm
                    logging.debug("runGuestCmdsExperiment(): working with vm: " + str(vmName))
                    #get names for clones and start them
                    for cloneinfo in clonevmjson[vm]:
                        if cloneinfo["groupNum"] == str(i):
                            cloneVMName = cloneinfo["name"]
                            if cloneVMName not in validvmnames:
                                continue
                            #Check if clone exists and then run it if it does
                            if not os.path.exists(cloneVMName):
                                logging.error("runGuestCmdsExperiment(): VM Name: " + str(cloneVMName) + " does not exist; skipping...")
                                continue
                            logging.debug("runGuestCmdsExperiment(): command(s) setup on " + str(cloneVMName) )
                            #put all of the commands into a single list, based on sequence numbers:
                            if cloneinfo["startup-cmds"] != None:
                                startupCmds = cloneinfo["startup-cmds"]
                                startupDelay = cloneinfo["startup-cmds-delay"]
                                #format them into a list; based on execution order
                                orderedStartupCmds = []
                                for sequence in sorted(startupCmds):
                                    cmds = startupCmds[sequence]
                                    for mcmd in cmds:
                                        #from the tuple, just get the "exec" or command, not hypervisor
                                        #substitute out any template variables
                                        mcmd = (mcmd[0],mcmd[1].replace("{{RES_CloneName}}","\""+str(cloneVMName)+"\""))
                                        mcmd = (mcmd[0],mcmd[1].replace("{{RES_CloneNumber}}",str(i)))
                                        orderedStartupCmds.append(mcmd[1])
                                logging.debug("runGuestCmdsExperiment(): sending command(s) for " + str(cloneVMName) + str(orderedStartupCmds))
                                self.vmManage.guestCommands(cloneVMName, orderedStartupCmds, startupDelay)
            while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                #waiting for vmmanager start vm to finish reading/writing...
                time.sleep(.1)
            logging.debug("runGuestCmdsExperiment(): Complete...")
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
        except Exception:
            logging.error("runGuestCmdsExperiment(): Error in runGuestCmdsExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    def guestStoredCmdsExperiment(self, configname, itype="", name=""):
        logging.debug("runGuestStoredCmdsExperiment(): instantiated")
        t = threading.Thread(target=self.runGuestStoredCmdsExperiment, args=(configname, itype, name))
        t.start()
        t.join()
        return 0

    def runGuestStoredCmdsExperiment(self, configname, itype, name):
        logging.debug("runGuestStoredCmdsExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMMANDING
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)
            for i in range(1, numclones + 1):
                for vm in clonevmjson.keys():
                    vmName = vm
                    logging.debug("runGuestStoredCmdsExperiment(): working with vm: " + str(vmName))
                    #get names for clones and start them
                    for cloneinfo in clonevmjson[vm]:
                        if cloneinfo["groupNum"] == str(i):
                            cloneVMName = cloneinfo["name"]
                            if cloneVMName not in validvmnames:
                                continue
                            #Check if clone exists and then run it if it does
                            if not os.path.exists(cloneVMName):
                                logging.error("runGuestStoredCmdsExperiment(): VM Name: " + str(cloneVMName) + " does not exist; skipping...")
                                continue
                            logging.debug("runGuestStoredCmdsExperiment(): command(s) setup on " + str(cloneVMName) )
                            #put all of the commands into a single list, based on sequence numbers:
                            if cloneinfo["stored-cmds"] != None:
                                storedCmds = cloneinfo["stored-cmds"]
                                storedDelay = cloneinfo["stored-cmds-delay"]
                                #format them into a list; based on execution order
                                orderedStoredCmds = []
                                for sequence in sorted(storedCmds):
                                    cmds = storedCmds[sequence]
                                    for mcmd in cmds:
                                        #from the tuple, just get the "exec" or command, not hypervisor
                                        #substitute out any template variables
                                        mcmd = (mcmd[0],mcmd[1].replace("{{RES_CloneName}}","\""+str(cloneVMName)+"\""))
                                        mcmd = (mcmd[0],mcmd[1].replace("{{RES_CloneNumber}}",str(i)))
                                        orderedStoredCmds.append(mcmd[1])
                                logging.debug("runGuestStoredCmdsExperiment(): sending command(s) for " + str(cloneVMName) + str(orderedStoredCmds))
                                self.vmManage.guestCommands(cloneVMName, orderedStoredCmds, storedDelay)
            while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                #waiting for vmmanager to finish reading/writing...
                time.sleep(.1)
            logging.debug("runGuestStoredCmdsExperiment(): Complete...")
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
        except Exception:
            logging.error("runGuestStoredCmdsExperiment(): Error in runGuestStoredCmdsExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def suspendExperiment(self, configname, itype="", name=""):
        logging.debug("suspendExperiment(): instantiated")
        t = threading.Thread(target=self.runSuspendExperiment, args=(configname, itype, name))
        t.start()
        t.join()
        return 0

    def runSuspendExperiment(self, configname, itype, name):
        logging.debug("runSuspendExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_SUSPENDING
            #call vmManage to suspend clones as specified in config file; wait and query the vmManage status, and then set the complete status
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)
            for i in range(1, numclones + 1):
                for vm in clonevmjson.keys(): 
                    vmName = vm
                    logging.debug("runSuspendExperiment(): working with vm: " + str(vmName))
                    #get names for clones and suspend them
                    for cloneinfo in clonevmjson[vm]:
                        if cloneinfo["groupNum"] == str(i):
                            cloneVMName = cloneinfo["name"]
                            if cloneVMName not in validvmnames:
                                continue
                            #Check if clone exists and then run it if it does
                            if not os.path.exists(vmName):
                                logging.error("runSuspendExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                                continue
                            logging.debug("runSuspendExperiment(): Suspending: " + str(vmName))
                            self.vmManage.suspendVM(cloneVMName)
                while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                    #waiting for vmmanager suspend vm to finish reading/writing...
                    time.sleep(.1)
            logging.debug("runSuspendingExperiment(): Complete...")
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
        except Exception:
            logging.error("runSuspendingExperiment(): Error in runSuspendingExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def pauseExperiment(self, configname, itype="", name=""):
        logging.debug("pauseExperiment(): instantiated")
        t = threading.Thread(target=self.runPauseExperiment, args=(configname, itype, name))
        t.start()
        t.join()
        return 0

    def runPauseExperiment(self, configname, itype, name):
        logging.debug("runPauseExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_PAUSING
            #call vmManage to pause clones as specified in config file; wait and query the vmManage status, and then set the complete status
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)
            for i in range(1, numclones + 1):
                for vm in clonevmjson.keys(): 
                    vmName = vm
                    logging.debug("runPauseExperiment(): working with vm: " + str(vmName))
                    #get names for clones and pausing them
                    for cloneinfo in clonevmjson[vm]:
                        if cloneinfo["groupNum"] == str(i):
                            cloneVMName = cloneinfo["name"]
                            if cloneVMName not in validvmnames:
                                continue                            
                            #Check if clone exists and then run it if it does
                            if not os.path.exists(cloneVMName):
                                logging.error("runPauseExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                                continue
                            logging.debug("runPauseExperiment(): Pausing: " + str(vmName))
                            self.vmManage.pauseVM(cloneVMName)
                while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                    #waiting for vmmanager pause vm to finish reading/writing...
                    time.sleep(.1)
            logging.debug("runPauseExperiment(): Complete...")
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
        except Exception:
            logging.error("runPauseExperiment(): Error in runPauseExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def snapshotExperiment(self, configname, itype="", name=""):
        logging.debug("snapshotExperiment(): instantiated")
        t = threading.Thread(target=self.runSnapshotExperiment, args=(configname, itype, name))
        t.start()
        t.join()
        return 0

    def runSnapshotExperiment(self, configname, itype, name):
        logging.debug("runSnapshotExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_SNAPSHOTTING
            #call vmManage to snapshot clones as specified in config file; wait and query the vmManage status, and then set the complete status
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)
            for i in range(1, numclones + 1):
                for vm in clonevmjson.keys(): 
                    vmName = vm
                    logging.debug("runSnapshotExperiment(): working with vm: " + str(vmName))
                    #get names for clones and pausing them
                    for cloneinfo in clonevmjson[vm]:
                        if cloneinfo["groupNum"] == str(i):
                            cloneVMName = cloneinfo["name"]
                            if cloneVMName not in validvmnames:
                                continue
                            #Check if clone exists and then run it if it does
                            if not os.path.exists(vmName):
                                logging.error("runSnapshotExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                                continue
                            logging.debug("runSnapshotExperiment(): Snapshotting: " + str(vmName))
                            self.vmManage.snapshotVM(cloneVMName)
                while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                    #waiting for vmmanager snapshot vm to finish reading/writing...
                    time.sleep(.1)
            logging.debug("runSnapshotExperiment(): Complete...")
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
        except Exception:
            logging.error("runSnapshotExperiment(): Error in runSnapshotExperiment(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_COMPLETE

    #abstractmethod
    def stopExperiment(self, configname, itype="", name=""):
        logging.debug("stopExperiment(): instantiated")
        t = threading.Thread(target=self.runStopExperiment, args=(configname, itype, name))
        t.start()
        t.join()
        return 0

    def runStopExperiment(self, configname, itype, name):
        logging.debug("runStopExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_STOPPING
            #call vmManage to stop clones as specified in config file; wait and query the vmManage status, and then set the complete status
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)
            for vm in clonevmjson.keys(): 
                vmName = vm
                logging.debug("runStopExperiment(): working with vm: " + str(vmName))
                #get names for clones and stop them
                for cloneinfo in clonevmjson[vm]:
                    cloneVMName = cloneinfo["name"]
                    if cloneVMName not in validvmnames:
                        continue
                    #Check if clone exists and then run it if it does
                    if not os.path.exists(vmName):
                        logging.error("runStopExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                        continue
                    logging.debug("runStopExperiment(): Stopping: " + str(vmName))
                    self.vmManage.stopVM(cloneVMName)
            while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                #waiting for vmmanager stop vm to finish reading/writing...
                time.sleep(.1)
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
    def removeExperiment(self, configname, itype="", name=""):
        logging.debug("removeExperiment(): instantiated")
        t = threading.Thread(target=self.runRemoveExperiment, args=(configname, itype, name))
        t.start()
        t.join()
        return 0
        
    def runRemoveExperiment(self, configname, itype, name):
        logging.debug("runRemoveExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_REMOVING
            #call vmManage to remove clones as specified in config file; wait and query the vmManage status, and then set the complete status
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)
            for vm in clonevmjson.keys(): 
                vmName = vm
                logging.debug("runRemoveExperiment(): working with vm: " + str(vmName))
                #get names for clones and remove them
                for cloneinfo in clonevmjson[vm]:
                    cloneVMName = cloneinfo["name"]
                    if cloneVMName not in validvmnames:
                        continue
                    #Check if clone exists and then remove it if it does
                    if not os.path.exists(cloneVMName):
                        logging.error("runRemoveExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                        continue
                    logging.debug("runRemoveExperiment(): Removing: " + str(cloneVMName))
                    self.vmManage.removeVM(cloneVMName)
            while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                #waiting for vmmanager stop vm to finish reading/writing...
                time.sleep(.1)
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
    def restoreExperiment(self, configname, itype="", name=""):
        logging.debug("restoreExperimentStates(): instantiated")
        t = threading.Thread(target=self.runRestoreExperiment, args=(configname, itype, name))
        t.start()
        t.join()
        return 0    

    def runRestoreExperiment(self, configname, itype, name):
        logging.debug("runRestoreExperiment(): instantiated")
        try:
            self.writeStatus = ExperimentManage.EXPERIMENT_MANAGE_RESTORING
            #call vmManage to restore clones as specified in config file; wait and query the vmManage status, and then set the complete status
            rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
            clonevmjson, numclones = rolledoutjson
            validvmnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)
            for vm in clonevmjson.keys(): 
                vmName = vm
                logging.debug("runRestoreExperiment(): working with vm: " + str(vmName))
                #get names for clones and restore them
                for cloneinfo in clonevmjson[vm]:
                    cloneVMName = cloneinfo["name"]
                    if cloneVMName not in validvmnames:
                        continue
                    #Check if clone exists and then run it if it does
                    if not os.path.exists(vmName):
                        logging.error("runRestoreExperiment(): VM Name: " + str(vmName) + " does not exist; skipping...")
                        continue
                    logging.debug("runRestoreExperiment(): Restoring latest for : " + str(cloneVMName))
                    self.vmManage.restoreLatestSnapVM(cloneVMName)
                    while self.vmManage.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
                        #waiting for vmmanager stop vm to finish reading/writing...
                        time.sleep(.1)
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
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus, "vmstatus" : self.vmstatus}

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
    vbm = VMwareManage()
    e = ExperimentManageVMware(vbm)
    ####---Create Experiment Test#####
    logging.info("Creating Experiment")
    e.createExperiment("sample")
    result = e.getExperimentManageStatus()["writeStatus"]
    while result != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment create to complete...")
        result = e.getExperimentManageStatus()["writeStatus"]
    
    #####---Start Experiment Test#####
    logging.info("Starting Experiment")
    e.startExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment start to complete...")
    logging.debug("Experiment start complete.")    

    #####---Pause Experiment Test#####
    logging.info("Pause Experiment")
    e.pauseExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment pause to complete...")
    logging.debug("Experiment pause complete.")

    #####---Snapshot Experiment Test#####
    logging.info("Snapshot Experiment")
    e.snapshotExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment snapshot to complete...")
    logging.debug("Experiment snapshot complete.")

    #####---Stop Experiment Test#####
    logging.info("Stopping Experiment")
    e.stopExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment stop to complete...")
    logging.debug("Experiment stop complete.")    

    #####---Suspend Experiment Test#####
    logging.info("Suspend Experiment")
    e.suspendExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment suspend to complete...")
    logging.debug("Experiment suspend complete.")    

    #####---Restore Experiment Test#####
    logging.info("Restoring Experiment")
    e.restoreExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment stop to complete...")
    logging.debug("Experiment stop complete.")

    # #####---Remove Experiment Test#####
    logging.info("Removing Experiment")
    e.removeExperiment("sample")
    result = e.getExperimentManageStatus()["writeStatus"]
    while result != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment create to complete...")
        result = e.getExperimentManageStatus()["writeStatus"]
