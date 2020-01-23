from subprocess import Popen, PIPE
import subprocess
from sys import argv, platform
import sys, traceback
import logging
import shlex
import threading
import sys
import time
from engine.Manager.VMManage.VMManage import VMManage
from engine.Manager.VMManage.VM import VM
import re
import configparser
import os
from engine.Configuration.SystemConfigIO import SystemConfigIO

class VBoxManage(VMManage):
    def __init__(self, initializeVMManage=False):
        logging.info("VBoxManage.__init__(): instantiated")
        VMManage.__init__(self)
        self.cf = SystemConfigIO()
        self.vbox_path = self.cf.getConfig()['VBOX']['VBOX_PATH']
        if initializeVMManage:
            self.refreshAllVMInfo()
            while self.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE:
            #waiting for manager to finish query...
                time.sleep(1)

    def configureVMNet(self, vmName, netNum, netName):
        logging.info("VBoxManage: configureVM(): instantiated")
        
        if VMManage.POSIX:
            #check to make sure the vm is known, if not should refresh or check name:
            if vmName not in self.vms:
                logging.error("configureVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            t = threading.Thread(target=self.runConfigureVMNet, args=(vmName, netNum, netName))
            t.start()
            return 0
        else:
            logging.error("Platform is not linux or linux2")
            print("Sorry your platform is not supported")
            return -1     

    def refreshAllVMInfo(self):
        logging.info("VBoxManage: refreshAllVMInfo(): instantiated")
        
        if VMManage.POSIX:
            logging.debug("getListVMS() Starting List VMs thread")
            t = threading.Thread(target=self.runVMSInfo)
            t.start()
        else:
            logging.error("Platform is not linux or linux2")
            print("Sorry your platform is not supported")
            return -1
        
    def refreshVMInfo(self, vmName):
        logging.info("VBoxManage: refreshVMInfo(): instantiated: " + str(vmName))
        
        if VMManage.POSIX:
            logging.debug("refreshVMInfo() refresh VMs thread")
            #check to make sure the vm is known, if not should refresh or check name:
            if vmName not in self.vms:
                logging.error("refreshVMInfo(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            t = threading.Thread(target=self.runVMInfo, args=(vmName,))
            t.start()
            return 0
        else:
            logging.error("Platform is not linux or linux2")
            print("Sorry your platform is not supported")   
            return -1    
    
    def runVMSInfo(self):
        logging.debug("VBoxManage: runVMSInfo(): instantiated")
        #run vboxmanage to get vm listing
        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus = VMManage.MANAGER_READING
        #clear out the current set
        self.vms = {}
        vmListCmd = self.vbox_path + " list vms"
        logging.debug("runVMSInfo(): Collecting VM Names using cmd: " + vmListCmd)
        if sys.platform == "linux" or sys.platform == "linux2":
            vmListCmd = "timeout " + str(VMManage.MANAGER_STATUS_TIMEOUT_VAL) + " " + vmListCmd
        else:
            logging.error("runVMSInfo(): This is not a linux system. Skipping: " + str(vmListCmd))
            return -1
        try:
            p = Popen(shlex.split(vmListCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out != '':
                    # logging.debug("runVMSInfo(): stdout Line: " + out)
                    # logging.debug("runVMSInfo(): split Line: " + str(out.split("{")))
                    splitOut = out.split("{")
                    vm = VM()
                    tmpname = splitOut[0].strip()
                    #has to be at least one character and every name has a start and end quote
                    if len(tmpname) > 2:
                        vm.name = splitOut[0].strip()[1:-1]
                    else: 
                        break
                    vm.UUID = splitOut[1].split("}")[0].strip()
                    # logging.debug("UUID: " + vm.UUID)
                    self.vms[vm.name] = vm
            p.wait()
            logging.debug("runVMSInfo(): Thread 1 completed: " + vmListCmd)
            logging.debug("Found # VMS: " + str(len(self.vms)))

            #for each vm, get the machine readable info
            logging.debug("runVMSInfo(): collecting VM extended info")
            vmNum = 1
            vmShowInfoCmd = ""
            for aVM in self.vms:
                logging.debug("runVMSInfo(): collecting # " + str(vmNum) + " of " + str(len(self.vms)))
                vmShowInfoCmd = self.vbox_path + " showvminfo \"" + str(self.vms[aVM].UUID) + "\"" + " --machinereadable"
                if sys.platform == "linux" or sys.platform == "linux2":
                    vmShowInfoCmd = "timeout " + str(VMManage.MANAGER_STATUS_TIMEOUT_VAL) + " " + vmShowInfoCmd
                logging.debug("runVMSInfo(): Running " + vmShowInfoCmd)
                p = Popen(shlex.split(vmShowInfoCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
                while True:
                    out = p.stdout.readline()
                    if out == '' and p.poll() != None:
                        break
                    if out != '':
                        #match example: nic1="none"
                        res = re.match("nic[0-9]+=", out)
                        if res:
                            # logging.debug("Found nic: " + out + " added to " + self.vms[aVM].name)
                            out = out.strip()
                            nicNum = out.split("=")[0][3:]
                            nicType = out.split("=")[1]
                            self.vms[aVM].adaptorInfo[nicNum] = nicType
                        res = re.match("groups=", out)
                        if res:
                            # logging.debug("Found groups: " + out + " added to " + self.vms[aVM].name)
                            self.vms[aVM].groups = out.strip()
                        res = re.match("VMState=", out)
                        if res:
                            # logging.debug("Found vmState: " + out + " added to " + self.vms[aVM].name)
                            state = out.strip().split("\"")[1].split("\"")[0]
                            if state == "running":
                                self.vms[aVM].state = VM.VM_STATE_RUNNING
                            elif state == "poweroff":
                                self.vms[aVM].state = VM.VM_STATE_OFF
                            else:
                                self.vms[aVM].state = VM.VM_STATE_OTHER

                p.wait()
                vmNum = vmNum + 1
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus = VMManage.MANAGER_IDLE
            logging.info("runVMSInfo(): Thread 2 completed: " + vmShowInfoCmd)
        except Exception:
            logging.error("Error in runVMSInfo(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus = VMManage.MANAGER_IDLE
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus = VMManage.MANAGER_IDLE

    def runVMInfo(self, aVM):
        logging.debug("VBoxManage: runVMSInfo(): instantiated")
        self.readStatus = VMManage.MANAGER_READING

        vmShowInfoCmd = self.vbox_path + " showvminfo \"" + self.vms[aVM].UUID + "\"" + " --machinereadable"
        if sys.platform == "linux" or sys.platform == "linux2":
            vmShowInfoCmd = "timeout " + str(VMManage.MANAGER_STATUS_TIMEOUT_VAL) + " " + vmShowInfoCmd
        logging.debug("runVMSInfo(): Running " + vmShowInfoCmd)
        p = Popen(shlex.split(vmShowInfoCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
        while True:
            out = p.stdout.readline()
            if out == '' and p.poll() != None:
                break
            if out != '':
                #match example: nic1="none"
                res = re.match("nic[0-9]+=", out)
                if res:
                    # logging.debug("Found nic: " + out + " added to " + self.vms[aVM].name)
                    out = out.strip()
                    nicNum = out.split("=")[0][3:]
                    nicType = out.split("=")[1]
                    self.vms[aVM].adaptorInfo[nicNum] = nicType
                res = re.match("groups=", out)
                if res:
                    # logging.debug("Found groups: " + out + " added to " + self.vms[aVM].name)
                    self.vms[aVM].groups = out.strip()
                res = re.match("VMState=", out)
                if res:
                    # logging.debug("Found vmState: " + out + " added to " + self.vms[aVM].name)
                    state = out.strip().split("\"")[1].split("\"")[0].strip()
                    if state == "running":
                        self.vms[aVM].state = VM.VM_STATE_RUNNING
                    elif state == "poweroff":
                        self.vms[aVM].state = VM.VM_STATE_OFF
                    else:
                        self.vms[aVM].state = VM.VM_STATE_OTHER
        p.wait()
        self.readStatus = VMManage.MANAGER_IDLE
        logging.debug("runVMInfo(): Thread completed")

    def runConfigureVMNet(self, vmName, netNum, netName):
        vmConfigVMCmd = ""
        try:
            logging.debug("VBoxManage: runConfigureVMNet(): instantiated")
            self.writeStatus = VMManage.MANAGER_WRITING
            vmConfigVMCmd = self.vbox_path + " modifyvm " + str(self.vms[vmName].UUID) + " --nic" + str(netNum) + " intnet " + " --intnet" + str(netNum) + " " + str(netName) + " --cableconnected"  + str(netNum) + " on "
            logging.debug("runConfigureVM(): Running " + vmConfigVMCmd)
            subprocess.check_output(shlex.split(vmConfigVMCmd, posix=self.POSIX), encoding='utf-8')

            self.writeStatus = VMManage.MANAGER_IDLE
            logging.debug("runConfigureVMNet(): Thread completed")
        except Exception:
            logging.error("runConfigureVMNet() Error: " + " cmd: " + vmConfigVMCmd)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = VMManage.MANAGER_IDLE

    def runVMCmd(self, cmd):
        logging.debug("VBoxManage: runVMCmd(): instantiated")
        try:
            self.writeStatus = VMManage.MANAGER_WRITING
            self.readStatus = VMManage.MANAGER_READING
            vmCmd = self.vbox_path + " " + cmd
            if sys.platform == "linux" or sys.platform == "linux2":
                vmCmd = "timeout " + str(VMManage.MANAGER_STATUS_TIMEOUT_VAL) + " " + vmCmd
            logging.debug("runVMCmd(): Running " + vmCmd)
            p = Popen(shlex.split(vmCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out != '':
                    logging.debug("output line: " + out)
            p.wait()
            
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus = VMManage.MANAGER_IDLE
            logging.debug("runVMCmd(): Thread completed")
        except Exception:
            logging.error("runVMCmd() Error: " + " cmd: " + cmd)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus = VMManage.MANAGER_IDLE
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus = VMManage.MANAGER_IDLE

    def getVMStatus(self, vmName):
        logging.debug("VBoxManage: getVMStatus(): instantiated " + vmName)
        #TODO: need to make this thread safe
        if vmName not in self.vms:
            logging.error("getVMStatus(): vmName does not exist: " + vmName)
            return None
        resVM = self.vms[vmName]
        #Don't want to rely on python objects in case we go with 3rd party clients in the future
        return {"vmName" : resVM.name, "vmUUID" : resVM.UUID, "setupStatus" : resVM.setupStatus, "vmState" : resVM.state, "adaptorInfo" : resVM.adaptorInfo, "groups" : resVM.groups}
        
    def getManagerStatus(self):
        logging.debug("VBoxManage: getManagerStatus(): instantiated")
        if self.readStatus == VMManage.MANAGER_UNKNOWN:
            logging.error("No status available, you must run refreshAllVMInfo() to initialize the Manager")
        vmStatus = {}
        for vmName in self.vms:
            resVM = self.vms[vmName]
            vmStatus[resVM.name] = {"vmUUID" : resVM.UUID, "setupStatus" : resVM.setupStatus, "vmState" : resVM.state, "adaptorInfo" : resVM.adaptorInfo, "groups" : resVM.groups}
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus, "vmstatus" : vmStatus}

    def importVM(self, filepath):
        logging.debug("VBoxManage: importVM(): instantiated")
        cmd = "import \"" + filepath + "\" --options keepallmacs"
        t = threading.Thread(target=self.runVMCmd, args=(cmd,))
        t.start()
        return 0  

    def snapshotVM(self, vmName):
        logging.debug("VBoxManage: snapshotVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        if vmName not in self.vms:
            logging.error("snapshotVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
            return -1
        cmd = " snapshot " + str(self.vms[vmName].UUID) + " take snapshot"
        t = threading.Thread(target=self.runVMCmd, args=(cmd,))
        t.start()
        return 0

    def exportVM(self, vmName, filepath):
        logging.debug("VBoxManage: importVM(): instantiated")
        #first remove any quotes that may have been entered before (because we will add some after we add the file and extension)
        if vmName not in self.vms:
            logging.error("exportVM(): vmName does not exist. Skipping... " + vmName)
            return None
        filepath = filepath.replace("\"","")
        exportfilename = os.path.join(filepath,vmName+".ova")
        cmd = "export " + self.vms[vmName].UUID + " -o \"" + exportfilename + "\" --iso"
        t = threading.Thread(target=self.runVMCmd, args=(cmd,))
        t.start()
        return 0

    def startVM(self, vmName):
        logging.debug("VBoxManage: startVM(): instantiated")
        if VMManage.POSIX:
            #check to make sure the vm is known, if not should refresh or check name:
            if vmName not in self.vms:
                logging.error("startVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = "startvm " + str(self.vms[vmName].UUID) + " --type headless"
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0
        else:
            logging.error("Platform is not linux or linux2")
            print("Sorry your platform is not supported")
            return -1

    def suspendVM(self, vmName):
        logging.debug("VBoxManage: suspendVM(): instantiated")
        if VMManage.POSIX:
            #check to make sure the vm is known, if not should refresh or check name:
            if vmName not in self.vms:
                logging.error("suspendVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = "controlvm " + str(self.vms[vmName].UUID) + " savestate"
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0
        else:
            logging.error("Platform is not linux or linux2")
            print("Sorry your platform is not supported")
            return -1

    def stopVM(self, vmName):
        logging.debug("VBoxManage: stopVM(): instantiated")
        if VMManage.POSIX:
            #check to make sure the vm is known, if not should refresh or check name:
            if vmName not in self.vms:
                logging.error("stopVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = "controlvm " + str(self.vms[vmName].UUID) + " poweroff"
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0

    def removeVM(self, vmName):
        logging.debug("VBoxManage: removeVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        if VMManage.POSIX:
            if vmName not in self.vms:
                logging.error("removeVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = "unregistervm " + str(self.vms[vmName].UUID) + " --delete"
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0

    def cloneVM(self, vmName, cloneName, cloneSnapshots, linkedClones, groupName):
        logging.debug("VBoxManage: cloneVM(): instantiated")
        if VMManage.POSIX:
            #check to make sure the vm is known, if not should refresh or check name:
            if vmName not in self.vms:
                logging.error("cloneVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            t = threading.Thread(target=self.runCloneVM, args=(vmName, cloneName, cloneSnapshots, linkedClones, groupName))
            t.start()
            return 0

    def runCloneVM(self, vmName, cloneName, cloneSnapshots, linkedClones, groupName):
        logging.debug("VBoxManage: runCloneVM(): instantiated")
        self.writeStatus = VMManage.MANAGER_WRITING
        self.readStatus = VMManage.MANAGER_READING
        try:
            #First check that the clone doesn't exist:
            if cloneName in self.vms:
                logging.error("runCloneVM(): A VM with the clone name already exists and is registered... skipping " + str(cloneName))
                self.readStatus = VMManage.MANAGER_IDLE
                self.writeStatus = VMManage.MANAGER_IDLE
                return
            #Call runVMCommand
            #cloneCmd = [self.vbox_path, "clonevm", self.vms[vmName].UUID, "--register"]
            cloneCmd = self.vbox_path + " clonevm " + str(self.vms[vmName].UUID) + " --register"
            #NOTE, the following logic is not in error. Linked clone can only be created from a snapshot.
            if cloneSnapshots == 'true':
                if linkedClones == 'true':
                    try:
                        logging.debug("runCloneVM(): using linked clones")
                        # get the name of the newest snapshot
                        #getSnapCmd = [self.vbox_path, "snapshot", self.vms[vmName].UUID, "list", "--machinereadable"]
                        getSnapCmd = self.vbox_path + " snapshot " + str(self.vms[vmName].UUID) + " list " + " --machinereadable"
                        logging.error("runCloneVM(): getting snaps; executing: " + str(getSnapCmd))
                        snapList = subprocess.check_output(shlex.split(getSnapCmd, posix=self.POSIX), encoding='utf-8')
                        latestSnapUUID = snapList.split("CurrentSnapshotUUID=\"")[1].split("\"")[0]
                        cloneCmd += " --snapshot "
                        cloneCmd += latestSnapUUID
                        cloneCmd += " --options "
                        cloneCmd += " link "
                    except Exception:
                        logging.error("runCloneVM(): Error in runCloneVM(): An error occured ")
                        logging.error("runCloneVM(): Using the link clone option requires that VMs contain a snapshot. No snapshot found for vm: " + vmName)
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_exception(exc_type, exc_value, exc_traceback)
                        self.writeStatus = VMManage.MANAGER_IDLE
                        self.readStatus = VMManage.MANAGER_IDLE
                        return
                else:
                    cloneCmd += " --mode "
                    cloneCmd += " all "
                
            cloneCmd += " --name "
            cloneCmd += str(cloneName)
            logging.debug("runCloneVM(): executing: " + str(cloneCmd))
            result = subprocess.check_output(shlex.split(cloneCmd, posix=self.POSIX), encoding='utf-8')

            #since we added a VM, now we have to refresh the VM status            

            #groupCmd = [self.vbox_path, "modifyvm", cloneName, "--groups", groupName]
            groupCmd = self.vbox_path + " modifyvm " + str(cloneName) + " --groups \"" + str(groupName)+"\""
            logging.debug("runCloneVM(): placing into group: " + str(groupName))
            logging.error("runCloneVM(): executing: " + str(groupCmd))
            result = subprocess.check_output(shlex.split(groupCmd, posix=self.POSIX), encoding='utf-8')

            logging.debug("runCloneVM(): Clone Created: " + str(cloneName) + " and placed into group: " + groupName)
            self.writeStatus = VMManage.MANAGER_IDLE
            self.readStatus = VMManage.MANAGER_IDLE
        except Exception:
            logging.error("runCloneVM(): Error in runCloneVM(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = VMManage.MANAGER_IDLE
            self.readStatus = VMManage.MANAGER_IDLE
            return
        finally:
            self.writeStatus = VMManage.MANAGER_IDLE
            self.readStatus = VMManage.MANAGER_IDLE  

    def enableVRDPVM(self, vmName, vrdpPort):
        logging.debug("VBoxManage: enabledVRDP(): instantiated")
        if VMManage.POSIX:
            #check to make sure the vm is known, if not should refresh or check name:
            if vmName not in self.vms:
                logging.error("enabledVRDP(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            t = threading.Thread(target=self.runEnableVRDP, args=(vmName, vrdpPort))
            t.start()
            return 0
        else:
            return -1

    def runEnableVRDP(self, vmName, vrdpPort):
        logging.debug("VBoxManage: runEnabledVRDP(): instantiated")
        self.writeStatus = VMManage.MANAGER_WRITING
        self.readStatus = VMManage.MANAGER_READING
        try:
            #vrdpCmd = [self.vbox_path, "modifyvm", vmName, "--vrde", "on", "--vrdeport", str(vrdpPort)]
            vrdpCmd = self.vbox_path + " modifyvm " + str(vmName) + " --vrde " + " on " + " --vrdeport " + str(vrdpPort)
            logging.debug("runEnabledVRDP(): setting up vrdp for " + vmName)
            logging.debug("runEnabledVRDP(): executing: "+ str(vrdpCmd))
            result = subprocess.check_output(shlex.split(vrdpCmd, posix=self.POSIX), encoding='utf-8')
            #now these settings will help against the issue when users 
            #can't reconnect after an abrupt disconnect
            #https://www.virtualbox.org/ticket/2963
            vrdpCmd = self.vbox_path + " modifyvm " + str(vmName) + " --vrdereusecon " + " on " + " --vrdemulticon " + " off"
            logging.debug("runEnabledVRDP(): Setting disconnect on new connection for " + vmName)
            logging.debug("runEnabledVRDP(): executing: " + str(vrdpCmd))
            result = subprocess.check_output(shlex.split(vrdpCmd, posix=self.POSIX), encoding='utf-8')            
            logging.debug("runEnabledVRDP(): completed")
            self.writeStatus = VMManage.MANAGER_IDLE
            self.readStatus = VMManage.MANAGER_IDLE
        except Exception:
                logging.error("runEnabledVRDP(): Error in runEnableVRDP(): An error occured ")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                self.writeStatus = VMManage.MANAGER_IDLE
                self.readStatus = VMManage.MANAGER_IDLE
                return
        finally:
                self.writeStatus = VMManage.MANAGER_IDLE
                self.readStatus = VMManage.MANAGER_IDLE

    def restoreLatestSnapVM(self, vmName):
        logging.debug("VBoxManage: restoreLatestSnapVM(): instantiated")
        if VMManage.POSIX:
            #check to make sure the vm is known, if not should refresh or check name:
            if vmName not in self.vms:
                logging.error("restoreLatestSnapVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1

            cmd = "snapshot " + str(self.vms[vmName].UUID) + " restorecurrent"
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0
        return -1
