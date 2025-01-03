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
from engine.Configuration.VMwareConfigIO import VMwareConfigIO
from threading import RLock

class VMwareManageWin(VMManage):
    def __init__(self, initializeVMManage=True):
        logging.debug("VMwareManageWin.__init__(): instantiated")
        VMManage.__init__(self)
        self.cf = SystemConfigIO()
        self.vc = VMwareConfigIO()
        self.vms_filename = self.cf.getConfig()['VMWARE']['VMANAGE_VM_PATH']
        self.preferences_filename = self.cf.getConfig()['VMWARE']['VMWARE_PREFSFILE_PATH']
        self.vms_all = self.vc.refresh_vmpath_to_dict(self.vms_filename)
        self.prefs_all = self.vc.refresh_inventory_to_dict(self.preferences_filename)
        self.vmcli = self.cf.getConfig()['VMWARE']['VMANAGE_CLI_PATH']
        self.vmrun = self.cf.getConfig()['VMWARE']['VMANAGE_RUN_PATH']
        self.vmovf = self.cf.getConfig()['VMWARE']['VMANAGE_OVF_PATH']
            
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

    # helper function to perform sort
    def num_sort(self, istring):
        return list(map(int, re.findall(r'\d+', istring)))[0]

    def configureVMNet(self, vmName, netNum, netName):
        logging.debug("VMwareManageWin: configureVMNet(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        exists = False
        try:
            self.lock.acquire()
            exists = vmName in self.vms
        finally:
            self.lock.release()

        if not exists:
            logging.error("configureVMNet(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
            return -1
        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runConfigureVMNet, args=(vmName, netNum, netName))
        t.start()
        t.join()
        return 0

    def configureVMNets(self, vmName, internalNets):
        logging.debug("VMwareManageWin: configureVMNets(): instantiated")
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
            t.join()
            return 0
        finally:
            self.lock.release()

    def runConfigureVMNets(self, vmName, internalNets):
        logging.debug("runConfigureVMNets(): instantiated")
        exists = False
        try:
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
                self.readStatus = VMManage.MANAGER_READING
                self.writeStatus += 1
                self.runConfigureVMNet(vmName, cloneNetNum, internalnet)
                cloneNetNum += 1            
           
            logging.debug("runConfigureVMNets(): Thread completed")
        except Exception:
            logging.error("runConfigureVMNets() Error")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runConfigureVMNets(): sub 1 "+ str(self.writeStatus))

    def guestCommands(self, vmName, cmds, delay=0):
        logging.debug("VMwareManageWin: guestCommands(): instantiated")
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
            t.join()
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
                p = Popen(vmCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
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
        logging.debug("VMwareManageWin: refreshAllVMInfo(): instantiated")
        logging.debug("getListVMS() Starting List VMs thread")
        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runVMSInfo)
        t.start()
        t.join()
        
    def refreshVMInfo(self, vmName):
        logging.debug("VMwareManageWin: refreshVMInfo(): instantiated: " + str(vmName))
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
            t.join()
            return 0
        finally:
            self.lock.release()
    
    def runVMSInfo(self):
        logging.debug("VMwareManageWin: runVMSInfo(): instantiated")
        try:
            logging.debug("runVMSInfo(): Collecting VM Names from log")
            #clear out the current set
            self.tempVMs = {}
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runVMSInfo(): adding 1 "+ str(self.writeStatus))
            self.vms_all = self.vc.refresh_vmpath_to_dict(self.vms_filename)
            for vm in self.vms_all.keys():
                self.tempVMs[vm] = VM()
                self.tempVMs[vm].name = vm
                self.tempVMs[vm].UUID = vm
            logging.debug("runVMSInfo(): Thread 1 completed: got vmlist")
            logging.debug("runVMSInfo(): Found # VMS: " + str(len(self.tempVMs)))

            #for each vm, get the machine readable info
            logging.debug("runVMSInfo(): collecting VM extended info")
            vmNum = 1
            vmShowInfoCmd = ""
            for aVM in self.tempVMs:
                logging.debug("runVMSInfo(): collecting # " + str(vmNum) + " of " + str(len(self.tempVMs)) + " : " + str(aVM))
                #Need to get ethernet type for each nic num, group/folder, vmstate, and latest snapshot uid

                #NICs: 
                vmnics = self.vc.get_vmnics(aVM)
                nn = 1
                self.tempVMs[aVM].adaptorInfo[nn] = vmnics
                self.tempVMs[aVM].groups = self.vc.get_vmgroups_name(aVM)

                vmStateCmd = "\""+self.vmcli + "\" " + "\""+str(self.tempVMs[aVM].name) + "\" Power query"
                logging.info("runVMSInfo(): Running " + vmStateCmd)
                p = Popen(vmStateCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
                while True:
                    out = p.stdout.readline()
                    if out == '' and p.poll() != None:
                        break
                    if out.strip() != '':
                        logging.info("Command Output: " + str(out))
                        res = re.match("PowerState:", out)
                        if res:
                            # logging.debug("Found vmState: " + out + " added to " + self.tempVMs[aVM].name)
                            state = out.strip().split(" ")[1].strip()
                            self.tempVMs[aVM].state = state
                p.wait()

                vmStateCmd = "\""+self.vmcli + "\" " + "\""+str(self.tempVMs[aVM].name) + "\" Snapshot query"
                logging.info("runVMSInfo(): Running " + vmStateCmd)
                p = Popen(vmStateCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
                while True:
                    out = p.stdout.readline()
                    if out == '' and p.poll() != None:
                        break
                    if out.strip() != '':
                        logging.debug("Command Output: " + str(out))
                        res = re.match("currentUID", out)
                        if res:
                            # logging.debug("Found snaps: " + out + " added to " + self.tempVMs[aVM].latestSnapUUID)
                            latestSnap = out.strip().split(" ")[1].strip()
                            self.tempVMs[aVM].latestSnapUUID = latestSnap

                p.wait()
                vmNum = vmNum + 1
            try:
                self.lock.acquire()
                self.vms = self.tempVMs
            finally:
                self.lock.release()
            logging.debug("runVMSInfo(): Thread 2 completed.")
        except Exception:
            logging.error("Error in runVMSInfo(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runVMSInfo(): sub 1 "+ str(self.writeStatus))

    def runVMInfo(self, vmName):
        logging.debug("VMwareManageWin: runVMInfo(): instantiated")
        try:
            logging.debug("runVMSInfo(): Collecting VM Names from log")
            #clear out the current set
            self.tempVMs = {}
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runVMSInfo(): adding 1 "+ str(self.writeStatus))
            self.vms_all = self.vc.refresh_vmpath_to_dict(self.vms_filename)
            for vm in self.vms_all.keys():
                self.tempVMs[vm] = VM()
                self.tempVMs[vm].name = vm
                self.tempVMs[vm].UUID = vm
            logging.debug("runVMSInfo(): Thread 1 completed: got vmlist")
            logging.debug("runVMSInfo(): Found # VMS: " + str(len(self.tempVMs)))

            if vmName not in self.tempVMs:
                logging.error("runVMInfo(): VM was not found/registered: " + vmName)
                return

            #get the machine readable info
            logging.debug("runVMInfo(): collecting VM extended info")
            #Need to get ethernet type for each nic num, group/folder, vmstate, and latest snapshot uid
            #NICs: 
            vmnics = self.vc.get_vmnics(vmName)
            nn = 1
            self.tempVMs[vmName].adaptorInfo[nn] = vmnics
            self.tempVMs[vmName].groups = self.vc.get_vmgroups_name(vmName)

            vmStateCmd = "\""+self.vmcli + "\" " + "\""+str(self.tempVMs[vmName].name) + "\" Power query"
            logging.info("runVMSInfo(): Running " + vmStateCmd)
            p = Popen(vmStateCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.debug("Command Output: " + str(out))
                    res = re.match("PowerState:", out)
                    if res:
                        # logging.debug("Found vmState: " + out + " added to " + self.tempVMs[aVM].name)
                        state = out.strip().split(" ")[1].strip()
                        self.tempVMs[vmName].state = state
            p.wait()

            vmStateCmd = "\""+self.vmcli + "\" " + "\""+str(self.tempVMs[vmName].name) + "\" Snapshot query"
            logging.info("runVMSInfo(): Running " + vmStateCmd)
            p = Popen(vmStateCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.debug("Command Output: " + str(out))
                    res = re.match("currentUID", out)
                    if res:
                        # logging.debug("Found snaps: " + out + " added to " + self.tempVMs[aVM].latestSnapUUID)
                        latestSnap = out.strip().split(" ")[1].strip()
                        self.tempVMs[vmName].latestSnapUUID = latestSnap

                p.wait()
            try:
                #Set self.vms to our temporary -- did it this way to save time
                self.lock.acquire()
                logging.debug("VM: " + str(vmName) + "\r\nself.vms: " + str(self.vms) + "\r\nself.tempVMs: " + str(self.tempVMs))
                self.vms[vmName] = self.tempVMs[vmName]
            finally:
                self.lock.release()

            logging.debug("runVMInfo(): Thread 2 completed.")
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
            self.lock.acquire()
            logging.debug("VMwareManageWin: runConfigureVMNet(): instantiated")
            self.prefs_all = self.vc.refresh_inventory_to_dict(self.preferences_filename)
            #Open the preferences.ini file and get number of pvns
            if 'namedPVNs.count' not in self.prefs_all['pref']:
                pvn_count = "0"
                # first get all names/id pairs
                pvns_names = []
                pvns_ids = []
            else:
                pvn_count = self.prefs_all['pref']['namedPVNs.count']
                # first get all names/id pairs
                pvns_names = self.vc.get_matching_keys(self.prefs_all['pref'],'namedPVNs[0-9]+.name')
                pvns_ids = self.vc.get_matching_keys(self.prefs_all['pref'],'namedPVNs[0-9]+.pvnID')
            #check if netName exists

            pvn_names_ids = {}
            if len(pvns_names) != len(pvns_ids):
                logging.error("preferences.ini is corrupt; pvn names size is not equal to pvn id size")
                exit(-1)
            for x in range(len(pvns_names)):
                pvn_names_ids[self.prefs_all['pref'][pvns_names[x]]] = self.prefs_all['pref'][pvns_ids[x]]
            #if netName exists, return the pvnID
            my_pvnid = ""
            if netName in pvn_names_ids:
                my_pvnid = pvn_names_ids[netName]
            else:
            #if not, then create an entry, update pvn_count and write it to the file
            # pref.namedPVNs1.name = "h1234"
            # pref.namedPVNs1.pvnID = "52 d5 e5 b1 c2 75 bf 12-08 d1 86 b1 51 a8 8d f1"
                self.prefs_all['pref']['namedPVNs.count'] = str(int(pvn_count)+1)
                hex_pvn_count = str(hex(int(pvn_count))).split("x")[1][-2:]
                my_pvnid = "00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 " + hex_pvn_count
                self.prefs_all['pref']['namedPVNs'+pvn_count+'.pvnID'] = my_pvnid
                self.prefs_all['pref']['namedPVNs'+pvn_count+'.name'] = netName
                            
                #write the new config with updated count and new pvn info
                self.vc.write_dict2dot_file(self.prefs_all,self.preferences_filename)
            
            #set netNum to pvnID and type to pvn
            self.readStatus = VMManage.MANAGER_READING
            vmUUID = ""
            vmUUID = str(self.vms[vmName].UUID)

            logging.debug("runConfigureVMNet(): adding 1 "+ str(self.writeStatus))
            #adjust netnum for compatibility:
            netNum = "ethernet" + str(int(netNum)-1)
            vmConfigVMCmd = "\""+self.vmcli+ "\"" + " \"" + vmUUID + "\" Ethernet SetPvnTypeBacking " + str(netNum) + " \"" + my_pvnid +"\""
            logging.info("runConfigureVMNet(): Running " + vmConfigVMCmd)
            result = subprocess.check_output(vmConfigVMCmd, encoding='utf-8', text=True)
            logging.info("Command Output: "+ str(result))

            vmConfigVMCmd = "\""+self.vmcli+ "\"" + " \"" + vmUUID + "\" Ethernet SetConnectionType " + str(netNum) + " pvn"
            logging.info("runConfigureVMNet(): Running " + vmConfigVMCmd)
            result = subprocess.check_output(vmConfigVMCmd, encoding='utf-8', text=True)
            logging.info("Command Output: "+ str(result))
            #Now refresh the preferences file for future accesses
            self.prefs_all = self.vc.refresh_inventory_to_dict(self.preferences_filename)
            logging.debug("runConfigureVMNet(): Thread completed")
        except Exception:
            logging.error("runConfigureVMNet() Error: " + " cmd: " + vmConfigVMCmd)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.lock.release()
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runConfigureVMNet(): sub 1 "+ str(self.writeStatus))

    def runVMCmd_cli(self, cmd):
        logging.debug("VMwareManageWin: runVMCmd(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runVMCmd(): adding 1 "+ str(self.writeStatus))
            vmCmd = "\""+self.vmcli + "\" " + cmd
            logging.info("runVMCmd(): Running " + vmCmd)
            p = Popen(vmCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
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

    def runVMCmd_ovf(self, cmd):
        logging.debug("VMwareManageWin: runVMCmd(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runVMCmd(): adding 1 "+ str(self.writeStatus))
            vmCmd = "\""+self.vmovf + "\" " + cmd
            logging.info("runVMCmd(): Running " + vmCmd)
            p = Popen(vmCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
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

    def runVMCmd(self, cmd):
        logging.debug("VMwareManageWin: runVMCmd(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runVMCmd(): adding 1 "+ str(self.writeStatus))
            vmCmd = "\""+self.vmrun + "\" " + cmd
            logging.info("runVMCmd(): Running " + vmCmd)
            p = Popen(vmCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
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
        logging.debug("VMwareManageWin: getVMStatus(): instantiated " + vmName)
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
        logging.debug("VMwareManageWin: getManagerStatus(): instantiated")
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
        logging.debug("VMwareManageWin: importVM(): instantiated")
        experimentname = os.path.basename(os.path.dirname(os.path.dirname(filepath)))
        cmd = "\"" + filepath + "\" \"" + os.path.join(self.vms_filename,experimentname) + "\""
        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runVMCmd_ovf, args=(cmd,))
        t.start()
        t.join()
        return 0  

    def snapshotVM(self, vmName):
        logging.debug("VMwareManageWin: snapshotVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("snapshotVM(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
                return -1
            cmd = "\"" + str(self.vms[vmName].UUID) + "\" Snapshot Take ressnapshot"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd_cli, args=(cmd,))
            t.start()
            t.join()
            return 0
        finally:
            self.lock.release()

    def exportVM(self, vmName, filepath):
        logging.debug("VMwareManageWin: exportVM(): instantiated")
        #first remove any quotes that may have been entered before (because we will add some after we add the file and extension)
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("exportVM(): " + vmName + " not found in list of known vms: \r\n" + str(vmName))
                return -1
            filepath = filepath.replace("\"","")
            exportfilename = os.path.join(filepath,os.path.basename(vmName)[:-4]+".ova")
            cmd = "\"" + self.vms[vmName].UUID + "\" \"" + exportfilename + "\""# + "\" --iso"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd_ovf, args=(cmd,))
            t.start()
            t.join()
            return 0
        finally:
            self.lock.release()

    def startVM(self, vmName):
        logging.debug("VMwareManageWin: startVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("startVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = " \"" + str(vmName) + "\" Power Start"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            t.join()
            return 0
        finally:
            self.lock.release()

    def pauseVM(self, vmName):
        logging.debug("VMwareManageWin: pauseVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("pauseVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = " -T ws pause " + str(self.vms[vmName].UUID) + ""
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            t.join()
            return 0
        finally:
            self.lock.release()

    def unpauseVM(self, vmName):
        logging.debug("VMwareManageWin: unpauseVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("unpauseVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = " -T ws unpause " + str(self.vms[vmName].UUID) + ""
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            t.join()
            return 0
        finally:
            self.lock.release()

    def suspendVM(self, vmName):
        logging.debug("VMwareManageWin: suspendVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("suspendVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = " -T ws suspend " + str(self.vms[vmName].UUID) + " hard"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            t.join()
            return 0
        finally:
            self.lock.release()

    def stopVM(self, vmName):
        logging.debug("VMwareManageWin: stopVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            exists = vmName in self.vms
            if not exists:
                logging.error("stopVM(): " + vmName + " not found in list of known vms: \r\n" + str(self.vms))
                return -1
            cmd = "-T ws stop " + str(self.vms[vmName].UUID) + " hard"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            t.join()
            return 0
        finally:
            self.lock.release()

    def removeVM(self, vmName):
        logging.debug("VMwareManageWin: removeVM(): instantiated")
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
            t.join()
            return 0
        finally:
            self.lock.release()

    def runRemoveVM(self, vmName, vmUUID):
        logging.debug("VMwareManageWin: runRemoveVM(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runRemoveVM(): adding 1 "+ str(self.writeStatus))
            vmCmd = "\"" + self.vmrun + "\" -T ws deleteVM \"" + vmUUID + "\""
            logging.info("runRemoveVM(): Running " + vmCmd)
            
            p = Popen(vmCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stderr.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.info("Command Output: " + out)
            p.wait()
            
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
        logging.debug("VMwareManageWin: cloneVMConfigAll(): instantiated")
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
        t.join()
        return 0

    def runCloneVMConfigAll(self, vmName, cloneName, cloneSnapshots, linkedClones, groupName, internalNets, vrdpPort):
        logging.debug("VMwareManageWin: runCloneVMConfigAll(): instantiated")
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
            snapcmd = "\""+ self.vmcli + "\" \"" + cloneUUID + "\" Snapshot Take ressnapshot"
            logging.info("runCloneVMConfigAll(): Running " + snapcmd)
            p = Popen(snapcmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.debug("runCloneVMConfigAll(): snapproc out: " + out)
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
        logging.debug("VMwareManageWin: cloneVM(): instantiated")
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
        t.join()
        return 0

    # def writeCloneVM_Config(self, vmName, cloneName, groupName):
    #     logging.debug("VMwareManageWin: writeCloneVM_Config(): instantiated")
    #     try:
    #         #get list of VMs and groups
    #         ###get vmlists
    #         self.lock.acquire()
    #         self.vm_inventory_all = self.vc.refresh_inventory_to_dict(self.inventory_filename)
    #         vmlists = self.vc.get_matching_keys(self.vm_inventory_all, "vmlist*")
    #         #get vm and group display names
    #         vms_names = self.vc.get_vmlist_disp2num()
    #         groups_names = self.vc.get_vmgroup_disp2num()

    #         tmpVMName_vmlist = vms_names[vmName]
    #         # 1. look at all vms
    #         #  if the vm is already there, print error and return
    #         #  otherwise, get highest ItemID (vmlist#)
    #         ###GROUP ID/CREATION###
    #         #Get the vmlist# associated with the existing group
    #         if groupName in groups_names:
    #             group_vmlist = groups_names[groupName]
    #             parent_id =  re.findall(r'\d+', group_vmlist)[0]
    #         else:
    #             #otherwise create the group
    #             vmlists.sort(key=self.num_sort)
    #             current_high = re.findall(r'\d+', vmlists[-1])[0]
    #             current_high = str(int(current_high)+1)

    #             new_groupentry_header = "vmlist"+(current_high)
    #             self.vm_inventory_all[new_groupentry_header] = {}
    #             self.vm_inventory_all[new_groupentry_header]['config'] = 'folder'+str(current_high)
    #             self.vm_inventory_all[new_groupentry_header]['Type'] = '2'
    #             self.vm_inventory_all[new_groupentry_header]['DisplayName'] = groupName
    #             self.vm_inventory_all[new_groupentry_header]['ParentID'] = '0'
    #             self.vm_inventory_all[new_groupentry_header]['ItemID'] = str(current_high)
    #             #my_list[new_groupentry_header]['SeqID'] = '0'
    #             self.vm_inventory_all[new_groupentry_header]['IsFavorite'] = 'FALSE'
    #             #my_list[new_groupentry_header]['UUID'] = tmpGroupName
    #             self.vm_inventory_all[new_groupentry_header]['Expanded'] = 'TRUE'
    #             parent_id = current_high

    #         ###VM CLONE CREATION
    #         vmlists = self.vc.get_matching_keys(self.vm_inventory_all, "vmlist*")
    #         vmlists.sort(key=self.num_sort)
    #         current_high = re.findall(r'\d+', vmlists[-1])[0]
    #         current_high = str(int(current_high)+1)
            
    #         new_vmentry_header = "vmlist"+(current_high)
    #         self.vm_inventory_all[new_vmentry_header] = self.vm_inventory_all[tmpVMName_vmlist].copy()
    #         self.vm_inventory_all[new_vmentry_header]['config'] = cloneName
    #         self.vm_inventory_all[new_vmentry_header]['DisplayName'] = os.path.basename(cloneName)[:-4]
    #         self.vm_inventory_all[new_vmentry_header]['ItemID'] = current_high
    #         self.vm_inventory_all[new_vmentry_header]['ParentID'] = parent_id
    #         self.vm_inventory_all[new_vmentry_header]['IsClone'] = 'TRUE'

    #         oresult = [""]
    #         self.vc.dict_to_dot(self.vm_inventory_all, oresult)
    #         #self.vc.write_dict2dot_file(self.vm_inventory_all)
    #     except Exception:
    #         logging.error("writeCloneVM_Config(): Error in writeCloneVM_Config(): An error occured when trying to write config file for the VM")
    #         exc_type, exc_value, exc_traceback = sys.exc_info()
    #         traceback.print_exception(exc_type, exc_value, exc_traceback)
    #     finally:
    #         self.lock.release()

    def runCloneVM(self, vmName, cloneName, cloneSnapshots, linkedClones, groupName):
        logging.debug("VMwareManageWin: runCloneVM(): instantiated")
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
            if os.path.exists(tmpCloneName):
                logging.warning("CLONE ALREADY EXISTS, skipping: " + str(tmpCloneName))
            else:    
                cloneCmd = "\"" + self.vmrun + "\" clone \"" + vmName + "\" \"" + tmpCloneName + "\""
                #NOTE, the following logic is not in error. Linked clone can only be created from a snapshot.
                if cloneSnapshots == 'true':
                    #linked Clones option requires a cloneSnapshotUUID to be specified
                    if linkedClones == 'true' and vmLatestSnapUUID != "":
                        logging.debug("runCloneVM(): using linked clones")
                        cloneCmd += " linked "
                        #cloneCmd += " -snapshot=" + vmLatestSnapUUID
                    else:
                        cloneCmd += " full"
                #cloneCmd += " --options keepallmacs "                
                cloneCmd += " -cloneName="
                cloneCmd += "\"" + str(os.path.basename(tmpCloneName.replace("\"",""))[:-4]) + "\""
                logging.info("runCloneVM(): executing: " + str(cloneCmd))
                result = subprocess.check_output(cloneCmd, encoding='utf-8', text=True)
                logging.info("Command Output: "+ str(result))
                #also have to disable vmxstats for the clones or else we can't run more than 1 at once:
                cloneCmd = "\"" + self.vmcli + "\" " + "\"" + tmpCloneName + "\" " + "ConfigParams  SetEntry vmxstats.filename \"\""
                logging.info("runCloneVM(): executing: " + str(cloneCmd))
                result = subprocess.check_output(cloneCmd, encoding='utf-8', text=True)
                logging.info("Command Output: "+ str(result))
                # self.writeCloneVM_Config(vmName, cloneName, groupName)
                self.writeStatus += 1
                self.runVMInfo(tmpCloneName)

        except Exception:
            logging.error("runCloneVM(): Error in runCloneVM(): An error occured when trying to clone the VM")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runCloneVM(): sub 1 "+ str(self.writeStatus))

    def enableVRDPVM(self, vmName, vrdpPort):
        logging.debug("VMwareManageWin: enabledVRDP(): instantiated")
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
            t.join()
            return 0
        finally:
            self.lock.release()

    def runEnableVRDP(self, vmName, vrdpPort):
        logging.debug("VMwareManageWin: runEnableVRDP(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runEnableVRDP(): adding 1 "+ str(self.writeStatus))
            #vrdpCmd = [self.vmanage_path, "modifyvm", vmName, "--vrde", "on", "--vrdeport", str(vrdpPort)]
            vrdpCmd = "\""+self.vmcli + "\" \"" + str(vmName) + "\" ConfigParams SetEntry RemoteDisplay.vnc.Enabled TRUE"
            logging.debug("runEnableVRDP(): Enabling VNC for " + vmName)
            logging.info("runEnableVRDP(): executing: "+ str(vrdpCmd))
            result = subprocess.check_output(vrdpCmd, encoding='utf-8', text=True)
            logging.info("Command Output: "+ str(result))

            vrdpCmd = "\""+self.vmcli + "\" \"" + str(vmName) + "\" ConfigParams SetEntry RemoteDisplay.vnc.port " + str(vrdpPort)
            logging.debug("runEnableVRDP(): Enabling VNC for " + vmName)
            logging.info("runEnableVRDP(): executing: "+ str(vrdpCmd))
            result = subprocess.check_output(vrdpCmd, encoding='utf-8', text=True)
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
        logging.debug("VMwareManage: restoreLatestSnapVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            latestSnap = ""
            #TODO for now revert to snapshot 1; fill fix by quering latest and then getting uid that way...
            vmStateCmd = "\""+self.vmcli + "\" " + "\""+str(vmName) + "\" Snapshot query"
            logging.info("runVMSInfo(): Running " + vmStateCmd)
            p = Popen(vmStateCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.info("Command Output: " + str(out))
                    res = re.match("currentUID", out)
                    if res:
                        # logging.debug("Found snaps: " + out + " added to " + self.tempVMs[aVM].latestSnapUUID)
                        latestSnap = out.strip().split(" ")[1].strip()

            if latestSnap != "":
                cmd = "\"" + str(vmName) + "\" Snapshot Revert " + latestSnap
                self.readStatus = VMManage.MANAGER_READING
                self.writeStatus += 1
                t = threading.Thread(target=self.runVMCmd_cli, args=(cmd,))
                t.start()
                t.join()
            return 0
        finally:
            self.lock.release()
