from subprocess import Popen, PIPE
import subprocess
import sys
from sys import argv, platform
import traceback
import logging
import shlex
import threading
from time import sleep
from engine.Manager.VMManage.VMManage import VMManage
from engine.Manager.VMManage.VM import VM
import os
import re
import configparser
from engine.Configuration.SystemConfigIO import SystemConfigIO

class VBoxManageWin(VMManage):
    def __init__(self, inializeVMManage=False):
        logging.info("VBoxManageWin.__init__(): instantiated")
        VMManage.__init__(self)
        self.cf = SystemConfigIO()
        self.vbox_path = self.cf.getConfig()['VBOX_WIN']['VBOX_PATH']
        if inializeVMManage:
            self.refreshAllVMInfo()

    def configureVM(self, vmName, srcIPAddress, dstIPAddress, srcPort, dstPort, adaptorNum):
        logging.info("configureVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        if vmName not in self.vms:
            logging.error("configureVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
            return -1
        t = threading.Thread(target=self.runConfigureVM, args=(vmName, srcIPAddress, dstIPAddress, srcPort, dstPort, adaptorNum))
        t.start()
        return 0   

    def refreshAllVMInfo(self):
        logging.info("refreshAllVMInfo(): instantiated")

        logging.debug("getListVMS() Starting List VMs thread")
        t = threading.Thread(target=self.runVMSInfo)
        t.start()
        
    def refreshVMInfo(self, vmName):
        logging.info("refreshVMInfo(): instantiated: " + str(vmName))
        logging.debug("refreshVMInfo() refresh VMs thread")
        #check to make sure the vm is known, if not should refresh or check name:
        if vmName not in self.vms:
            logging.error("refreshVMInfo(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
            return -1
        t = threading.Thread(target=self.runVMInfo, args=(vmName,))
        t.start()
        return 0
        
    def runVMSInfo(self):
        logging.debug("runVMSInfo(): instantiated")
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        #run vboxmanage to get vm listing
        self.readStatus = VMManage.MANAGER_READING
        #clear out the current set
        self.vms = {}
        vmListCmd = self.vbox_path + " list vms"
        logging.debug("runVMSInfo(): Collecting VM Names using cmd: " + vmListCmd)
        try:
            p = Popen(vmListCmd, stdout=PIPE, stderr=PIPE, startupinfo=startupinfo, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out != '':
                    logging.debug("runVMSInfo(): stdout Line: " + out)
                    logging.debug("runVMSInfo(): split Line: " + str(out.split("{")))
                    splitOut = out.split("{")
                    vm = VM()
                    tmpname = splitOut[0].strip()
                    #has to be at least one character and every name has a start and end quote
                    if len(tmpname) > 2:
                        vm.name = splitOut[0].strip()[1:-1]
                    else: 
                        break
                    vm.UUID = splitOut[1].split("}")[0].strip()
                    logging.debug("UUID: " + vm.UUID)
                    self.vms[vm.name] = vm
            p.wait()
            logging.info("runVMSInfo(): Thread 1 completed: " + vmListCmd)
            logging.info("Found # VMS: " + str(len(self.vms)))

            #for each vm, get the machine readable info
            logging.debug("runVMSInfo(): collecting VM extended info")
            vmNum = 1
            vmShowInfoCmd = ""
            for aVM in self.vms:
                logging.debug("runVMSInfo(): collecting # " + str(vmNum) + " of " + str(len(self.vms)))
                vmShowInfoCmd = self.vbox_path + " showvminfo " + str(self.vms[aVM].UUID) + "" + " --machinereadable"
                logging.debug("runVMSInfo(): Running " + vmShowInfoCmd)
                p = Popen(vmShowInfoCmd, stdout=PIPE, stderr=PIPE, startupinfo=startupinfo, encoding="utf-8")
                while True:
                    out = p.stdout.readline()
                    if out == '' and p.poll() != None:
                        break
                    if out != '':
                        logging.debug("runVMSInfo(): proc output: " + out)
                        #match example: nic1="none"
                        res = re.match("nic[0-9]+=", out)
                        if res:
                            logging.debug("Found nic: " + out + " added to " + self.vms[aVM].name)
                            out = out.strip()
                            nicNum = out.split("=")[0][3:]
                            nicType = out.split("=")[1]
                            self.vms[aVM].adaptorInfo[nicNum] = nicType
                        res = re.match("groups=", out)
                        if res:
                            logging.debug("Found groups: " + out + " added to " + self.vms[aVM].name)
                            self.vms[aVM].groups = out.strip()
                        res = re.match("VMState=", out)
                        if res:
                            logging.debug("Found vmState: " + out + " added to " + self.vms[aVM].name)
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
            logging.info("runVMSInfo(): Thread 2 completed: " + vmShowInfoCmd)
        except Exception:
            logging.error("Error in runVMSInfo(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.readStatus = VMManage.MANAGER_IDLE

    def runVMInfo(self, aVM):
        logging.debug("runVMSInfo(): instantiated")
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.readStatus = VMManage.MANAGER_READING
        vmShowInfoCmd = self.vbox_path + " showvminfo " + self.vms[aVM].UUID + "" + " --machinereadable"
        logging.debug("runVMSInfo(): Running " + vmShowInfoCmd)
        p = Popen(vmShowInfoCmd, stdout=PIPE, stderr=PIPE, startupinfo=startupinfo, encoding="utf-8")
        while True:
            out = p.stdout.readline()
            if out == '' and p.poll() != None:
                break
            if out != '':
                #match example: nic1="none"
                res = re.match("nic[0-9]+=", out)
                if res:
                    logging.debug("Found nic: " + out + " added to " + self.vms[aVM].name)
                    out = out.strip()
                    nicNum = out.split("=")[0][3:]
                    nicType = out.split("=")[1]
                    self.vms[aVM].adaptorInfo[nicNum] = nicType
                res = re.match("groups=", out)
                if res:
                    logging.debug("Found groups: " + out + " added to " + self.vms[aVM].name)
                    self.vms[aVM].groups = out.strip()
                res = re.match("VMState=", out)
                if res:
                    logging.debug("Found vmState: " + out + " added to " + self.vms[aVM].name)
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

    def runConfigureVM(self, vmName, srcIPAddress, dstIPAddress, srcPort, dstPort, adaptorNum):
        try:
            logging.debug("runConfigureVM(): instantiated")
            self.writeStatus = VMManage.MANAGER_WRITING
            vmConfigVMCmd = self.vbox_path + " modifyvm " + str(self.vms[vmName].UUID) + " --nic" + str(adaptorNum) + " generic" + " --nicgenericdrv1 UDPTunnel " + "--cableconnected" + str(adaptorNum) + " on --nicproperty" + str(adaptorNum) + " sport=" + str(srcPort) + " --nicproperty" + str(adaptorNum) + " dport=" + str(dstPort) + " --nicproperty" + str(adaptorNum) + " dest=" + str(dstIPAddress)
            logging.debug("runConfigureVM(): Running " + vmConfigVMCmd)
            subprocess.check_output(vmConfigVMCmd)
            
            self.writeStatus = VMManage.MANAGER_IDLE
            logging.debug("runConfigure(): Thread completed")
        except Exception:
            logging.error("runConfigureVM() Error: " + " cmd: " + vmConfigVMCmd)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.readStatus = VMManage.MANAGER_IDLE

    def runVMCmd(self, cmd):
        logging.debug("runVMCmd(): instantiated")
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.writeStatus = VMManage.MANAGER_WRITING
        self.readStatus = VMManage.MANAGER_READING
        vmCmd = self.vbox_path + " " + cmd
        logging.debug("runVMCmd(): Running " + vmCmd)
        p = Popen(vmCmd, stdout=PIPE, stderr=PIPE, startupinfo=startupinfo, encoding="utf-8")
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

    def getVMStatus(self, vmName):
        logging.debug("getVMStatus(): instantiated " + vmName)
        #TODO: need to make this thread safe
        if vmName not in self.vms:
            logging.error("getVMStatus(): vmName does not exist: " + vmName)
            return None
        resVM = self.vms[vmName]
        #Don't want to rely on python objects in case we go with 3rd party clients in the future
        return {"vmName" : resVM.name, "vmUUID" : resVM.UUID, "setupStatus" : resVM.setupStatus, "vmState" : resVM.state, "adaptorInfo" : resVM.adaptorInfo, "groups" : resVM.groups}
        
    def getManagerStatus(self):
        logging.debug("getManagerStatus(): instantiated")
        if self.readStatus == VMManage.MANAGER_UNKNOWN:
            logging.error("No status available, you must run refreshAllVMInfo() to initialize the Manager")
        vmStatus = {}
        for vmName in self.vms:
            resVM = self.vms[vmName]
            vmStatus[resVM.name] = {"vmUUID" : resVM.UUID, "setupStatus" : resVM.setupStatus, "vmState" : resVM.state, "adaptorInfo" : resVM.adaptorInfo, "groups" : resVM.groups}
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus, "vmstatus" : vmStatus}

    def importVM(self, filepath):
        logging.debug("importVM(): instantiated")
        cmd = "import \"" + filepath + "\" --options keepallmacs"
        t = threading.Thread(target=self.runVMCmd, args=(cmd,))
        t.start()
        return 0  

    def snapshotVM(self, vmName):
        logging.debug("snapshotVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        if vmName not in self.vms:
            logging.error("snapshotVM(): " + filepath + " not found in list of known vms: \r\n" + str(self.vms))
            return -1
        cmd = " snapshot " + str(self.vms[vmName].UUID) + " take snapshot"
        t = threading.Thread(target=self.runVMCmd, args=(cmd,))
        t.start()
        return 0

    def exportVM(self, vmName, filepath):
        logging.debug("importVM(): instantiated")        
        cmd = "export " + self.vms[vmName].UUID + "\" -o \"" + filepath + "\" --iso"
        t = threading.Thread(target=self.runVMCmd, args=(cmd,))
        t.start()
        return 0

    def startVM(self, vmName):
        logging.debug("startVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        if vmName not in self.vms:
            logging.error("startVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
            return -1
        cmd = "startvm " + str(self.vms[vmName].UUID)
        t = threading.Thread(target=self.runVMCmd, args=(cmd,))
        t.start()
        return 0
        
    def suspendVM(self, vmName):
        logging.debug("suspendVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        if vmName not in self.vms:
            logging.error("suspendVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
            return -1
        cmd = "controlvm " + str(self.vms[vmName].UUID) + " savestate"
        t = threading.Thread(target=self.runVMCmd, args=(cmd,))
        t.start()
        return 0
        
    def stopVM(self, vmName):
        logging.debug("stopVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        if vmName not in self.vms:
            logging.error("stopVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
            return -1
        cmd = "controlvm " + str(self.vms[vmName].UUID) + " poweroff"
        t = threading.Thread(target=self.runVMCmd, args=(cmd,))
        t.start()
        return 0
        
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Starting Program")
    logging.info("Instantiating VBoxManageWin")
    
    testvmname = "default c"
    
    vbm = VBoxManageWin()
    
    logging.info("Status without refresh: ")
    vbm.getManagerStatus()
    
    logging.info("Refreshing VM Info - BEFORE")
    for vm in vbm.vms:
        logging.info("VM Info:\r\n" + str(vm.name))
    vbm.refreshAllVMInfo()
    
    while vbm.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        sleep(1)
    logging.info("Refreshing VMs Info - AFTER")

    #get vm info from objects
    for vm in vbm.vms:
        logging.info("VM Info:\r\nName: " + str(vbm.vms[vm].name) + "\r\nState: " + str(vbm.vms[vm].state) + "\r\n" + "Groups: " + str(vbm.vms[vm].groups + "\r\n"))
        for adaptor in vbm.vms[vm].adaptorInfo:
            logging.info("adaptor: " + str(adaptor) + " Type: " + vbm.vms[vm].adaptorInfo[adaptor] + "\r\n")
    
    logging.info("Refreshing single VM Info--")
    logging.info("Result: " + str(vbm.refreshVMInfo(testvmname)))

    while vbm.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        sleep(1)
    
    logging.info("Status for " + testvmname)
    logging.info(vbm.getVMStatus(testvmname))

    #runConfigureVM(self, vmName, srcIPAddress, dstIPAddress, srcPort, dstPort, adaptorNum)
    vbm.configureVM(testvmname, "", "127.0.0.1", 100, 100, 1)

    while vbm.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        sleep(1)
    
    logging.info("Result: " + str(vbm.refreshVMInfo(testvmname)))
    while vbm.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        sleep(1)
    
    logging.info("Status for " + testvmname)
    logging.info(vbm.getVMStatus(testvmname))
    
    logging.info("----Testing VM commands-------")
    logging.info("----Start-------")
    vbm.startVM(testvmname)
    while vbm.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        sleep(1)
    logging.info("----Waiting 5 seconds to save state-------")
    sleep(5)

    vbm.suspendVM(testvmname)
    while vbm.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        sleep(1)
    logging.info("----Waiting 5 seconds to resume -------")
    sleep(5)
    
    vbm.startVM(testvmname)
    while vbm.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        sleep(1)
    logging.info("----Waiting 5 seconds to stop-------")
    sleep(5)

    vbm.stopVM(testvmname)
    while vbm.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        sleep(1)

    while vbm.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        sleep(1)

    sleep(10)
    logging.info("Final Manager Status: " + str(vbm.getManagerStatus()))

    logging.info("Completed Exiting...")
