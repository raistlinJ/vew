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
from threading import RLock

class VBoxManage(VMManage):
    def __init__(self, initializeVMManage=True):
        logging.info("VBoxManage.__init__(): instantiated")
        VMManage.__init__(self)
        self.cf = SystemConfigIO()
        self.vmanage_path = self.cf.getConfig()['VBOX']['VMANAGE_PATH']
        # A lock for acces/updates to self.vms
        self.lock = RLock()
        self.vms = {}
        self.tempVMs = {}
        if initializeVMManage:
            self.refreshAllVMInfo()
            result = self.getManagerStatus()["writeStatus"]
            while result != self.MANAGER_IDLE:
            #waiting for manager to finish query...
                result = self.getManagerStatus()["writeStatus"]
                time.sleep(.1)

    def configureVMNet(self, vmName, netNum, netName):
        logging.info("VBoxManage: configureVMNet(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        exists = False
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("configureVMNet(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
                return -1
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runConfigureVMNet, args=(vmName, netNum, netName))
            t.start()
            return 0
        finally:
            self.lock.release()

    def configureVMNets(self, vmName, internalNets):
        logging.info("VBoxManageWin: configureVMNets(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        exists = False
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("configureVMNets(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
                return -1
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runConfigureVMNets, args=(vmName, internalNets))
            t.start()
            return 0
        finally:
            self.lock.release()

    def runConfigureVMNets(self, vmName, internalNets):
        try:
            logging.debug("VBoxManage: runConfigureVMNets(): instantiated")
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runConfigureVMNets(): adding 1 "+ str(self.writeStatus))            
            cloneNetNum = 1
            logging.debug("runConfigureVMNets(): Processing internal net names: " + str(internalNets))
            vmUUID = ""
            try:
                self.lock.acquire()
                vmUUID = str(self.vms[vmName].UUID)
            finally:
                self.lock.release()
            for internalnet in internalNets:
                vmConfigVMCmd = self.vmanage_path + " modifyvm " + vmUUID + " --nic" + str(cloneNetNum) + " intnet " + " --intnet" + str(cloneNetNum) + " " + str(internalnet) + " --cableconnected"  + str(cloneNetNum) + " on "
                logging.info("runConfigureVMNets(): Running " + vmConfigVMCmd)
                result = subprocess.check_output(shlex.split(vmConfigVMCmd, posix=self.POSIX), encoding='utf-8', text=True)
                logging.info("Command Output: "+ str(result))
                cloneNetNum += 1            
           
            logging.debug("runConfigureVMNets(): Thread completed")
        except Exception:
            logging.error("runConfigureVMNets() Error: " + " cmd: " + vmConfigVMCmd)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runConfigureVMNets(): sub 1 "+ str(self.writeStatus))

    def guestCommands(self, vmName, cmds, delay=0):
        logging.debug("VBoxManageWin: guestCommands(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        exists = False
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("guestCommands(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
                return -1
            self.guestThreadStatus += 1
            t = threading.Thread(target=self.runGuestCommands, args=(vmName, cmds, delay))
            t.start()
            return 0
        finally:
            self.lock.release()

    def runGuestCommands(self, vmName, cmds, delay):
        try:
            logging.debug("runGuestCommands(): adding 1 "+ str(self.writeStatus))
            cmd = "N/A"
            #if a delay was specified... wait
            time.sleep(int(delay))
            for cmd in cmds:
                vmCmd = self.vmanage_path + " guestcontrol " + str(self.vms[vmName].UUID) + " " + cmd
                logging.info("runGuestCommands(): Running " + vmCmd)
                p = Popen(shlex.split(vmCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
                while True:
                    out = p.stdout.readline()
                    if out == '' and p.poll() != None:
                        break
                    if out.strip() != '':
                        logging.info("Command Output: " + out)
                p.wait()

            logging.debug("runGuestCommands(): Thread completed")
        except Exception:
            logging.error("runGuestCommands() Error: " + " cmd: " + cmd)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.guestThreadStatus -= 1
            logging.debug("runGuestCommands(): sub thread 1 "+ str(self.writeStatus))

    def refreshAllVMInfo(self):
        logging.info("VBoxManage: refreshAllVMInfo(): instantiated")
        logging.debug("getListVMS() Starting List VMs thread")
        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runVMSInfo)
        t.start()
        
    def refreshVMInfo(self, vmName):
        logging.info("VBoxManage: refreshVMInfo(): instantiated: " + str(vmName))
        logging.debug("refreshVMInfo() refresh VMs thread")
        #check to make sure the vm is known, if not should refresh or check name:
        exists = False
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("refreshVMInfo(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMInfo, args=(vmName,))
            t.start()
            return 0
        finally:
            self.lock.release()
    
    def runVMSInfo(self):
        logging.debug("VBoxManageWin: runVMSInfo(): instantiated")
        try:
            vmListCmd = self.vmanage_path + " list vms"
            logging.info("runVMSInfo(): Collecting VM Names using cmd: " + vmListCmd)
            #clear out the current set
            self.tempVMs = {}
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runVMSInfo(): adding 1 "+ str(self.writeStatus))
            p = Popen(shlex.split(vmListCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.debug("Command Output: " + str(out))
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
                    self.tempVMs[vm.name] = vm
            p.wait()
            logging.debug("runVMSInfo(): Thread 1 completed: " + vmListCmd)
            logging.debug("runVMSInfo(): Found # VMS: " + str(len(self.tempVMs)))

            #for each vm, get the machine readable info
            logging.debug("runVMSInfo(): collecting VM extended info")
            vmNum = 1
            vmShowInfoCmd = ""
            for aVM in self.tempVMs:
                logging.debug("runVMSInfo(): collecting # " + str(vmNum) + " of " + str(len(self.tempVMs)) + " : " + str(aVM))
                vmShowInfoCmd = self.vmanage_path + " showvminfo " + str(self.tempVMs[aVM].UUID) + " --machinereadable"
                logging.info("runVMSInfo(): Running " + vmShowInfoCmd)
                p = Popen(shlex.split(vmShowInfoCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
                while True:
                    out = p.stdout.readline()
                    if out == '' and p.poll() != None:
                        break
                    if out.strip() != '':
                        logging.debug("Command Output: " + str(out))
                        #match example: nic1="none"
                        res = re.match("nic[0-9]+=", out)
                        if res:
                            # logging.debug("Found nic: " + out + " added to " + self.tempVMs[aVM].name)
                            out = out.strip()
                            nicNum = out.split("=")[0][3:]
                            nicType = out.split("=")[1]
                            self.tempVMs[aVM].adaptorInfo[nicNum] = nicType
                        res = re.match("groups=", out)
                        if res:
                            # logging.debug("Found groups: " + out + " added to " + self.tempVMs[aVM].name)
                            self.tempVMs[aVM].groups = out.strip()
                        res = re.match("VMState=", out)
                        if res:
                            # logging.debug("Found vmState: " + out + " added to " + self.tempVMs[aVM].name)
                            state = out.strip().split("\"")[1].split("\"")[0]
                            self.tempVMs[aVM].state = state
                        res = re.match("CurrentSnapshotUUID=", out)
                        if res:
                            # logging.debug("Found snaps: " + out + " added to " + self.tempVMs[aVM].latestSnapUUID)
                            latestSnap = out.strip().split("\"")[1].split("\"")[0]
                            self.tempVMs[aVM].latestSnapUUID = latestSnap
                p.wait()
                vmNum = vmNum + 1
            try:
                self.lock.acquire()
                self.vms = self.tempVMs
            finally:
                self.lock.release()
            logging.debug("runVMSInfo(): Thread 2 completed: " + vmShowInfoCmd)
        except Exception:
            logging.error("Error in runVMSInfo(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runVMSInfo(): sub 1 "+ str(self.writeStatus))

    def runVMInfo(self, vmName):
        logging.debug("VBoxManage: runVMInfo(): instantiated")
        try:
            #run vboxmanage to get vm listing
            #Make sure this one isn't cleared before use too...
            vmListCmd = self.vmanage_path + " list vms"
            logging.info("runVMInfo(): Collecting VM Names using cmd: " + vmListCmd)
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runVMInfo(): adding 1 "+ str(self.writeStatus))
            p = Popen(shlex.split(vmListCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.debug("Command Output: " + str(out))
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
                    self.tempVMs[vm.name] = vm
            p.wait()
            logging.debug("runVMInfo(): Thread 1 completed: " + vmListCmd)
            logging.debug("runVMInfo(): Found # VMS: " + str(len(self.tempVMs)))

            if vmName not in self.tempVMs:
                logging.error("runVMInfo(): VM was not found/registered: " + vmName)
                return

            #get the machine readable info
            logging.debug("runVMInfo(): collecting VM extended info")
            vmShowInfoCmd = ""
            vmShowInfoCmd = self.vmanage_path + " showvminfo " + str(self.tempVMs[vmName].UUID) + " --machinereadable"
            logging.info("runVMInfo(): Running " + vmShowInfoCmd)
            p = Popen(shlex.split(vmShowInfoCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.debug("Command Output: " + str(out))
                    #match example: nic1="none"
                    res = re.match("nic[0-9]+=", out)
                    if res:
                        out = out.strip()
                        nicNum = out.split("=")[0][3:]
                        nicType = out.split("=")[1]
                        self.tempVMs[vmName].adaptorInfo[nicNum] = nicType
                    res = re.match("groups=", out)
                    if res:
                        # logging.debug("Found groups: " + out + " added to " + self.tempVMs[vmName].name)
                        self.tempVMs[vmName].groups = out.strip()
                    res = re.match("VMState=", out)
                    if res:
                        # logging.debug("Found vmState: " + out + " added to " + self.tempVMs[vmName].name)
                        state = out.strip().split("\"")[1].split("\"")[0]
                        self.tempVMs[vmName].state = state
                    res = re.match("CurrentSnapshotUUID=", out)
                    if res:
                        # logging.debug("Found snaps: " + out + " added to " + self.tempVMs[vmName].latestSnapUUID)
                        latestSnap = out.strip().split("\"")[1].split("\"")[0]
                        self.tempVMs[vmName].latestSnapUUID = latestSnap
            p.wait()
            try:
                #Set self.vms to our temporary -- did it this way to save time
                self.lock.acquire()
                logging.debug("VM: " + str(vmName) + "\r\nself.vms: " + str(self.vms) + "\r\nself.tempVMs: " + str(self.tempVMs))
                self.vms[vmName] = self.tempVMs[vmName]
            finally:
                self.lock.release()

            logging.debug("runVMInfo(): Thread 2 completed: " + vmShowInfoCmd)
        except Exception:
            logging.error("Error in runVMInfo(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runVMInfo(): sub 1 "+ str(self.writeStatus))

    def runConfigureVMNet(self, vmName, netNum, netName):
        try:
            logging.debug("VBoxManage: runConfigureVMNet(): instantiated")
            self.readStatus = VMManage.MANAGER_READING
            vmUUID = ""
            try:
                self.lock.acquire()
                vmUUID = str(self.vms[vmName].UUID)
            finally:
                self.lock.release()
                
            logging.debug("runConfigureVMNet(): adding 1 "+ str(self.writeStatus))
            vmConfigVMCmd = self.vmanage_path + " modifyvm " + vmUUID + " --nic" + str(netNum) + " intnet " + " --intnet" + str(netNum) + " " + str(netName) + " --cableconnected"  + str(netNum) + " on "
            logging.info("runConfigureVMNet(): Running " + vmConfigVMCmd)
            result = subprocess.check_output(shlex.split(vmConfigVMCmd, posix=self.POSIX), encoding='utf-8', text=True)
            logging.info("Command Output: "+ str(result))

            logging.debug("runConfigureVMNet(): Thread completed")
        except Exception:
            logging.error("runConfigureVMNet() Error: " + " cmd: " + vmConfigVMCmd)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runConfigureVMNet(): sub 1 "+ str(self.writeStatus))

    def runVMCmd(self, cmd):
        logging.debug("VBoxManageWin: runVMCmd(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runVMCmd(): adding 1 "+ str(self.writeStatus))
            vmCmd = self.vmanage_path + " " + cmd
            logging.info("runVMCmd(): Running " + vmCmd)
            p = Popen(shlex.split(vmCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out != '':
                    logging.info("Command Output: " + out)
            p.wait()
            
            logging.debug("runVMCmd(): Thread completed")
        except Exception:
            logging.error("runVMCmd() Error: " + " cmd: " + cmd)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runVMCmd(): sub 1 "+ str(self.writeStatus))

    def getVMStatus(self, vmName):
        logging.debug("VBoxManage: getVMStatus(): instantiated " + vmName)
        exists = False
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("getVMStatus(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
                return -1
            resVM = self.vms[vmName]
            #Don't want to rely on python objects in case we go with 3rd party clients in the future
            return {"vmName" : resVM.name, "vmUUID" : resVM.UUID, "setupStatus" : resVM.setupStatus, "vmState" : resVM.state, "adaptorInfo" : resVM.adaptorInfo, "groups" : resVM.groups, "latestSnapUUID": resVM.latestSnapUUID}
        finally:
            self.lock.release()        
        
    def getManagerStatus(self):
        logging.debug("VBoxManage: getManagerStatus(): instantiated")
        vmStatus = {}
        try:
            self.lock.acquire()
            for vmName in self.vms:
                resVM = self.vms[vmName]
                vmStatus[resVM.name] = {"vmUUID" : resVM.UUID, "setupStatus" : resVM.setupStatus, "vmState" : resVM.state, "adaptorInfo" : resVM.adaptorInfo, "groups" : resVM.groups}
        finally:
            self.lock.release()
        
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus, "vmstatus" : vmStatus}

    def importVM(self, filepath):
        logging.debug("VBoxManage: importVM(): instantiated")
        cmd = "import \"" + filepath + "\" --options keepallmacs"
        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runVMCmd, args=(cmd,))
        t.start()
        return 0  

    def snapshotVM(self, vmName):
        logging.debug("VBoxManage: snapshotVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("snapshotVM(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
                return -1
            cmd = " snapshot " + str(self.vms[vmName].UUID) + " take snapshot"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0
        finally:
            self.lock.release()

    def exportVM(self, vmName, filepath):
        logging.debug("VBoxManage: exportVM(): instantiated")
        #first remove any quotes that may have been entered before (because we will add some after we add the file and extension)
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("exportVM(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
                return -1
            filepath = filepath.replace("\"","")
            exportfilename = os.path.join(filepath,vmName+".ova")
            cmd = "export " + self.vms[vmName].UUID + " -o \"" + exportfilename# + "\" --iso"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0
        finally:
            self.lock.release()

    def startVM(self, vmName):
        logging.debug("VBoxManage: startVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("startVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = "startvm " + str(self.vms[vmName].UUID) + " --type headless"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0
        finally:
            self.lock.release()

    def pauseVM(self, vmName):
        logging.debug("VBoxManage: pauseVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("pauseVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = "controlvm " + str(self.vms[vmName].UUID) + " pause"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0
        finally:
            self.lock.release()

    def suspendVM(self, vmName):
        logging.debug("VBoxManage: suspendVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("suspendVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = "controlvm " + str(self.vms[vmName].UUID) + " savestate"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0
        finally:
            self.lock.release()

    def stopVM(self, vmName):
        logging.debug("VBoxManage: stopVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("stopVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = "controlvm " + str(self.vms[vmName].UUID) + " poweroff"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0
        finally:
            self.lock.release()

    def removeVM(self, vmName):
        logging.debug("VBoxManage: removeVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("removeVM(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
                return -1
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runRemoveVM, args=(vmName, str(self.vms[vmName].UUID)))
            t.start()
            return 0
        finally:
            self.lock.release()

    def runRemoveVM(self, vmName, vmUUID):
        logging.debug("VBoxManage: runRemoveVM(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runRemoveVM(): adding 1 "+ str(self.writeStatus))
            vmCmd = self.vmanage_path + " unregistervm " + vmUUID + " --delete"
            logging.info("runRemoveVM(): Running " + vmCmd)
            success = False
            p = Popen(shlex.split(vmCmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stderr.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.info("Command Output: " + out)
                    if "100%" in out:
                        success = True
            p.wait()
            if success:
                try:
                    self.lock.acquire()
                    del self.vms[vmName]
                finally:
                    self.lock.release()

            logging.debug("runRemoveVM(): Thread completed")
        except Exception:
            logging.error("runRemoveVM() Error: " + " vmCmd: " + vmCmd)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runRemoveVM(): sub 1 "+ str(self.writeStatus))

    def cloneVMConfigAll(self, vmName, cloneName, cloneSnapshots, linkedClones, groupName, internalNets, vrdpPort, refreshVMInfo=False):
        logging.debug("VBoxManage: cloneVMConfigAll(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("cloneVMConfigAll(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
        finally:
            self.lock.release()

        if refreshVMInfo == True:
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            #runVMInfo obtains it's own lock
            self.runVMInfo(vmName)
        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runCloneVMConfigAll, args=(vmName, cloneName, cloneSnapshots, linkedClones, groupName, internalNets, vrdpPort))
        t.start()
        return 0

    def runCloneVMConfigAll(self, vmName, cloneName, cloneSnapshots, linkedClones, groupName, internalNets, vrdpPort):
        logging.debug("VBoxManage: runCloneVMConfigAll(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runCloneVMConfigAll(): adding 1 "+ str(self.writeStatus))
            #first clone
            #Check that vm does exist
            try:
                self.lock.acquire()
                exists = vmName in self.vms
                if not exists:
                    logging.error("runCloneVMConfigAll(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
                    return
            finally:
                self.lock.release()
            # clone the VM
            self.writeStatus += 1
            self.runCloneVM(vmName, cloneName, cloneSnapshots, linkedClones, groupName)
            
            #netsetup
            try:
                self.lock.acquire()
                exists = cloneName in self.vms
                if not exists:
                    logging.error("runCloneVMConfigAll(): " + cloneName + " not found in list of known vms: \r\n" + str(cloneName))
                    return
                else:
                    cloneUUID = str(self.vms[cloneName].UUID)
            finally:
                self.lock.release()

            self.writeStatus += 1
            self.runConfigureVMNets(cloneName, internalNets)

            #vrdp setup (if applicable)
            if vrdpPort != None:
                self.writeStatus += 1
                self.runEnableVRDP(cloneName, vrdpPort)
            
            #create snap
            snapcmd = self.vmanage_path + " snapshot " + cloneUUID + " take snapshot"
            logging.info("runCloneVMConfigAll(): Running " + snapcmd)
            p = Popen(shlex.split(snapcmd, posix=self.POSIX), stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.info("runCloneVMConfigAll(): snapproc out: " + out)
            p.wait()
            logging.debug("runCloneVMConfigAll(): Thread completed")

        except Exception:
            logging.error("runCloneVMConfigAll(): Error in runCloneVMConfigAll(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runCloneVMConfigAll(): sub 1 "+ str(self.writeStatus))

    def cloneVM(self, vmName, cloneName, cloneSnapshots, linkedClones, groupName, refreshVMInfo=False):
        logging.debug("VBoxManage: cloneVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("cloneVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
        finally:
            self.lock.release()

        if refreshVMInfo == True:
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            #runVMInfo obtains it's own lock
            self.runVMInfo(vmName)
        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runCloneVM, args=(vmName, cloneName, cloneSnapshots, linkedClones, groupName))
        t.start()
        return 0

    def runCloneVM(self, vmName, cloneName, cloneSnapshots, linkedClones, groupName):
        logging.debug("VBoxManage: runCloneVM(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runCloneVM(): adding 1 "+ str(self.writeStatus))
            #First check that the clone doesn't exist:
            try:
                self.lock.acquire()
                exists = cloneName in self.vms
                if exists:
                    logging.error("runCloneVM(): A VM with the clone name already exists and is registered... skipping " + str(cloneName))
                    return
                else:
                    vmUUID = str(self.vms[vmName].UUID)
                    vmLatestSnapUUID = str(self.vms[vmName].latestSnapUUID)
            finally:
                self.lock.release()
            ###Only time cloneName is used instead of UUID, because it doesn't yet exist..."
            tmpCloneName = cloneName
            if " " in tmpCloneName and not tmpCloneName.startswith("\"") and not tmpCloneName.endswith("\""):
                tmpCloneName = "\"" + str(tmpCloneName) + "\""
            #Call runVMCommand
            cloneCmd = self.vmanage_path + " clonevm " + vmUUID + " --register" + " --options=keepallmacs"
            #NOTE, the following logic is not in error. Linked clone can only be created from a snapshot.
            if cloneSnapshots == 'true':
                #linked Clones option requires a cloneSnapshotUUID to be specified
                if linkedClones == 'true':
                    logging.debug("runCloneVM(): using linked clones")
                    cloneCmd += " --options "
                    cloneCmd += " link "
                    cloneCmd += " --snapshot " + vmLatestSnapUUID
                else:
                    cloneCmd += " --mode "
                    cloneCmd += " all "
            #cloneCmd += " --options keepallmacs "                
            cloneCmd += " --name "
            cloneCmd += str(tmpCloneName)
            logging.info("runCloneVM(): executing: " + str(cloneCmd))
            result = subprocess.check_output(shlex.split(cloneCmd, posix=self.POSIX), encoding='utf-8', text=True)
            logging.info("Command Output: "+ str(result))

            #groupCmd = [self.vmanage_path, "modifyvm", tmpCloneName, "--groups", groupName]
            groupCmd = self.vmanage_path + " modifyvm " + str(tmpCloneName) + " --groups " + str(groupName)
            logging.debug("runCloneVM(): placing into group: " + str(groupName))
            logging.info("runCloneVM(): executing: " + str(groupCmd))
            result = subprocess.check_output(shlex.split(groupCmd, posix=self.POSIX), encoding='utf-8',text=True)
            logging.info("Command Output: "+ str(result))

            logging.debug("runCloneVM(): Clone Created: " + str(tmpCloneName) + " and placed into group: " + groupName)
            #since we added a VM, now we have to add it to the known list
            logging.debug("runCloneVM(): Adding: " + str(tmpCloneName) + " to known VMs")
            self.writeStatus += 1
            self.runVMInfo(tmpCloneName)

        except Exception:
            logging.error("runCloneVM(): Error in runCloneVM(): An error occured; it could be due to a missing snapshot for the VM")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runCloneVM(): sub 1 "+ str(self.writeStatus))

    def enableVRDPVM(self, vmName, vrdpPort):
        logging.debug("VBoxManage: enabledVRDP(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("enabledVRDP(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runEnableVRDP, args=(vmName, vrdpPort))
            t.start()
            return 0
        finally:
            self.lock.release()

    def runEnableVRDP(self, vmName, vrdpPort):
        logging.debug("VBoxManage: runEnabledVRDP(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runEnableVRDP(): adding 1 "+ str(self.writeStatus))
            #vrdpCmd = [self.vmanage_path, "modifyvm", vmName, "--vrde", "on", "--vrdeport", str(vrdpPort)]
            vrdpCmd = self.vmanage_path + " modifyvm " + str(vmName) + " --vrde " + " on " + " --vrdeport " + str(vrdpPort)
            logging.debug("runEnableVRDP(): setting up vrdp for " + vmName)
            logging.info("runEnableVRDP(): executing: "+ str(vrdpCmd))
            result = subprocess.check_output(shlex.split(vrdpCmd, posix=self.POSIX), encoding='utf-8', text=True)
            logging.info("Command Output: "+ str(result))
            #now these settings will help against the issue when users 
            #can't reconnect after an abrupt disconnect
            #https://www.virtualbox.org/ticket/2963
            vrdpCmd = self.vmanage_path + " modifyvm " + str(vmName) + " --vrdemulticon " + " on " #" --vrdereusecon " + " on " + " --vrdemulticon " + " off"
            logging.debug("runEnableVRDP(): Setting disconnect on new connection for " + vmName)
            logging.info("runEnableVRDP(): executing: " + str(vrdpCmd))
            result = subprocess.check_output(shlex.split(vrdpCmd, posix=self.POSIX), encoding='utf-8', text=True)
            logging.info("Command Output: "+ str(result))
            logging.debug("runEnableVRDP(): completed")
        except Exception:
            logging.error("runEnableVRDP(): Error in runEnableVRDP(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runEnableVRDP(): sub 1 "+ str(self.writeStatus))

    def restoreLatestSnapVM(self, vmName):
        logging.debug("VBoxManage: restoreLatestSnapVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("restoreLatestSnapVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = "snapshot " + str(self.vms[vmName].UUID) + " restorecurrent"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            return 0
        finally:
            self.lock.release()
