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
    def __init__(self, initializeVMManage=False):
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

    # helper function to perform sort
    def num_sort(self, istring):
        return list(map(int, re.findall(r'\d+', istring)))[0]

    def configureVMNet(self, vmName, netNum, netName):
        logging.debug("VMwareManageWin: configureVMNet(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:

        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runConfigureVMNet, args=(vmName, netNum, netName))
        t.start()
        #t.join()
        return 0

    def configureVMNets(self, vmName, internalNets):
        logging.debug("VMwareManageWin: configureVMNets(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runConfigureVMNets, args=(vmName, internalNets))
            t.start()
            #t.join()
            return 0
        except Exception:
            logging.error("configureVMNets() Error: " + " vmName: " + vmName)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)

    def runConfigureVMNets(self, vmName, internalNets):
        logging.debug("runConfigureVMNets(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runConfigureVMNets(): adding 1 "+ str(self.writeStatus))
            cloneNetNum = 1
            logging.debug("runConfigureVMNets(): Processing internal net names: " + str(internalNets))
            
            for internalnet in internalNets:
                self.readStatus = VMManage.MANAGER_READING
                self.writeStatus += 1
                self.runConfigureVMNet(vmName, cloneNetNum, internalnet)
                cloneNetNum += 1            
           
            logging.debug("runConfigureVMNets(): Thread completed")
        except Exception:
            logging.error("runConfigureVMNets() Error for VM: " + vmName)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            self.readStatus = VMManage.MANAGER_IDLE
            self.writeStatus -= 1
            logging.debug("runConfigureVMNets(): sub 1 "+ str(self.writeStatus))

    def guestCommands(self, vmName, cmds, delay=0):
        logging.debug("VMwareManageWin: guestCommands(): instantiated")
        try:
            self.lock.acquire()
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
                vmCmd = self.vmrun + " " + cmd
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
        logging.info("VBoxManage: refreshAllVMInfo(): instantiated")
        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runVMSInfo)
        t.start()
        
    def refreshVMInfo(self, vmName):
        logging.debug("VMwareManageWin: refreshVMInfo(): instantiated: " + str(vmName))
        logging.debug("refreshVMInfo() refresh VMs thread")
        #check to make sure the vm is known, if not should refresh or check name:
        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runVMInfo, args=(vmName,))
        t.start()
        #t.join()

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
                        logging.debug("Command Output: " + str(out))
                        res = re.match("PowerState:", out)
                        if res:
                            # logging.debug("Found vmState: " + out + " added to " + self.tempVMs[aVM].name)
                            logging.debug("Command Output: " + out)
                            state = out.strip().split(" ")[1].strip()
                            self.tempVMs[aVM].state = state
                #p.wait()

                vmStateCmd = "\""+self.vmcli + "\" " + "\""+str(self.tempVMs[aVM].name) + "\" Snapshot query"
                logging.info("runVMSInfo(): Running " + vmStateCmd)
                p2 = Popen(vmStateCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
                while True:
                    out = p2.stdout.readline()
                    if out == '' and p2.poll() != None:
                        break
                    if out.strip() != '':
                        logging.debug("Command Output: " + str(out))
                        res = re.match("currentUID", out)
                        if res:
                            # logging.debug("Found snaps: " + out + " added to " + self.tempVMs[aVM].latestSnapUUID)
                            logging.info("Command Output: " + out)
                            latestSnap = out.strip().split(" ")[1].strip()
                            self.tempVMs[aVM].latestSnapUUID = latestSnap

                #p2.wait()
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
            #clear out the current set
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runVMSInfo(): adding 1 "+ str(self.writeStatus))
            
            if not os.path.exists(vmName):
                logging.warning("runVMInfo(): VM was not found: " + vmName)
                if vmName in self.vms:
                    logging.debug("runVMInfo(): VM was in vms, removing from dict: " + vmName)
                    del self.vms[vmName]
                return

            #get the machine readable info
            logging.debug("runVMInfo(): collecting VM extended info")
            #Need to get ethernet type for each nic num, group/folder, vmstate, and latest snapshot uid
            #NICs: 
            vmnics = self.vc.get_vmnics(vmName)
            nn = 1
            self.vms[vmName] = VM()
            self.vms[vmName].name = vmName
            self.vms[vmName].adaptorInfo[nn] = vmnics
            self.vms[vmName].groups = self.vc.get_vmgroups_name(vmName)

            vmStateCmd = "\""+self.vmcli + "\" " + "\""+str(self.vms[vmName].name) + "\" Power query"
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
                        # logging.debug("Found vmState: " + out + " added to " + self.vms[aVM].name)
                        logging.debug("Command Output: " + out)
                        state = out.strip().split(" ")[1].strip()
                        self.vms[vmName].state = state
            #p.wait()

            vmStateCmd = "\""+self.vmcli + "\" " + "\""+str(self.vms[vmName].name) + "\" Snapshot query"
            logging.info("runVMSInfo(): Running " + vmStateCmd)
            p2 = Popen(vmStateCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p2.stdout.readline()
                if out == '' and p2.poll() != None:
                    break
                if out.strip() != '':
                    logging.debug("Command Output: " + str(out))
                    res = re.match("currentUID", out)
                    if res:
                        # logging.debug("Found snaps: " + out + " added to " + self.vms[aVM].latestSnapUUID)
                        logging.info("Command Output: " + out)
                        latestSnap = out.strip().split(" ")[1].strip()
                        self.vms[vmName].latestSnapUUID = latestSnap

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
                pvn_count = "1"
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

            logging.debug("runConfigureVMNet(): adding 1 "+ str(self.writeStatus))
            #adjust netnum for compatibility:
            netNum = "ethernet" + str(int(netNum)-1)
            vmConfigVMCmd = "\""+self.vmcli+ "\"" + " \"" + vmName + "\" Ethernet SetPvnTypeBacking " + str(netNum) + " \"" + my_pvnid +"\""
            logging.info("runConfigureVMNet(): Running " + vmConfigVMCmd)
            result = subprocess.check_output(vmConfigVMCmd, encoding='utf-8', text=True)
            logging.info("Command Output: "+ str(result))

            vmConfigVMCmd = "\""+self.vmcli+ "\"" + " \"" + vmName + "\" Ethernet SetConnectionType " + str(netNum) + " pvn"
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
            logging.info("runVMCmd_ovf(): running command: " + str(vmCmd))
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
            p = Popen(vmCmd, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stderr.readline()
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
        try:
            self.lock.acquire()
            if vmName not in self.vms:
                logging.error("getVMStatus(): " + vmName + " not found: \r\n" + str(vmName))
                return -1
            resVM = self.vms[vmName]
            #Don't want to rely on python objects in case we go with 3rd party clients in the future
            return {"vmName" : resVM.name, "vmUUID" : resVM.name, "setupStatus" : resVM.setupStatus, "vmState" : resVM.state, "adaptorInfo" : resVM.adaptorInfo, "groups" : resVM.groups, "latestSnapUUID": resVM.latestSnapUUID}
        finally:
            self.lock.release()        
        
    def getManagerStatus(self):
        logging.debug("VMwareManageWin: getManagerStatus(): instantiated")
        vmStatus = {}
        try:
            self.lock.acquire()
            for vmName in self.vms:
                resVM = self.vms[vmName]
                vmStatus[resVM.name] = {"vmUUID" : resVM.name, "setupStatus" : resVM.setupStatus, "vmState" : resVM.state, "adaptorInfo" : resVM.adaptorInfo, "groups" : resVM.groups}
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
            cmd = "\"" + str(vmName) + "\" Snapshot Take ressnapshot"
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
            filepath = filepath.replace("\"","")
            exportfilename = os.path.join(filepath,os.path.basename(vmName)[:-4]+".ova")
            cmd = "\"" + vmName + "\" \"" + exportfilename + "\""
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
            cmd = " \"" + str(vmName) + "\" Power Start"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd_cli, args=(cmd,))
            t.start()
            #t.join()
            return 0
        finally:
            self.lock.release()

    def pauseVM(self, vmName):
        logging.debug("VMwareManageWin: pauseVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            cmd = " -T ws pause " + str(vmName)
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            #t.join()
            return 0
        finally:
            self.lock.release()

    def unpauseVM(self, vmName):
        logging.debug("VMwareManageWin: unpauseVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            cmd = " -T ws unpause " + str(vmName) + ""
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
            cmd = " -T ws suspend " + str(vmName) + " hard"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            #t.join()
            return 0
        finally:
            self.lock.release()

    def stopVM(self, vmName):
        logging.debug("VMwareManageWin: stopVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            cmd = "-T ws stop " + str(vmName) + " hard"
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runVMCmd, args=(cmd,))
            t.start()
            #t.join()
            return 0
        finally:
            self.lock.release()

    def removeVM(self, vmName):
        logging.debug("VMwareManageWin: removeVM(): instantiated")
        #check to make sure the vm is known, if not should refresh or check name:
        try:
            self.lock.acquire()
            self.readStatus = VMManage.MANAGER_READING
            self.writeStatus += 1
            t = threading.Thread(target=self.runRemoveVM, args=(vmName,))
            t.start()
            #t.join()
            return 0
        finally:
            self.lock.release()

    def runRemoveVM(self, vmName):
        logging.debug("VMwareManageWin: runRemoveVM(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runRemoveVM(): adding 1 "+ str(self.writeStatus))
            vmCmd = "\"" + self.vmrun + "\" -T ws deleteVM \"" + vmName + "\""
            logging.info("runRemoveVM(): Running " + vmCmd)
            
            p = Popen(vmCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stderr.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.info("Command Output: " + out)
            p.wait()
            
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

        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runCloneVMConfigAll, args=(vmName, cloneName, cloneSnapshots, linkedClones, groupName, internalNets, vrdpPort))
        t.start()
        #t.join()
        return 0

    def runCloneVMConfigAll(self, vmName, cloneName, cloneSnapshots, linkedClones, groupName, internalNets, vrdpPort):
        logging.debug("VMwareManageWin: runCloneVMConfigAll(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runCloneVMConfigAll(): adding 1 "+ str(self.writeStatus))
            #first clone
            # clone the VM
            self.writeStatus += 1
            self.runCloneVM(vmName, cloneName, cloneSnapshots, linkedClones, groupName)
            
            #netsetup

            self.writeStatus += 1
            self.runConfigureVMNets(cloneName, internalNets)

            #vrdp setup (if applicable)
            if vrdpPort != None:
                self.writeStatus += 1
                self.runEnableVRDP(cloneName, vrdpPort)
            
            #create snap
            snapcmd = "\""+ self.vmcli + "\" \"" + cloneName + "\" Snapshot Take ressnapshot"
            logging.info("runCloneVMConfigAll(): Running " + snapcmd)
            p = Popen(snapcmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    logging.info("Command Output: " + out)
                    logging.debug("runCloneVMConfigAll(): snapproc out: " + out)
            #p.wait()
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

        self.readStatus = VMManage.MANAGER_READING
        self.writeStatus += 1
        t = threading.Thread(target=self.runCloneVM, args=(vmName, cloneName, cloneSnapshots, linkedClones, groupName))
        t.start()
        #t.join()
        return 0

    def runCloneVM(self, vmName, cloneName, cloneSnapshots, linkedClones, groupName):
        logging.debug("VMwareManageWin: runCloneVM(): instantiated")
        try:
            self.readStatus = VMManage.MANAGER_READING
            logging.debug("runCloneVM(): adding 1 "+ str(self.writeStatus))
            #First check that the clone doesn't exist:
            vmLatestSnapUUID = "1"

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
            #query latest and then getting uid that way...
            vmStateCmd = "\""+self.vmcli + "\" " + "\""+str(vmName) + "\" Snapshot query"
            logging.info("restoreLatestSnapVM(): Running " + vmStateCmd)
            p = Popen(vmStateCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            while True:
                out = p.stdout.readline()
                if out == '' and p.poll() != None:
                    break
                if out.strip() != '':
                    res = re.match("currentUID", out)
                    if res:
                        logging.info("Command Output: " + str(out))
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
