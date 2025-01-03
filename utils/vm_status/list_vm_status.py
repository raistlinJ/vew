#!/usr/bin/env bash

import paramiko
import sys, traceback
import logging
from engine.Engine import Engine
from engine.Manager.VMManage.VM import VM
from engine.Manager.VMManage.VMManage import VMManage
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
import re
import time

vmanagePath = "VBoxManage"
writeStatus = 0
readStatus = 0

def retrieveVMs_UUID(loggedssh, vmnames = []):
    if vmnames == []:
        return []
    writeStatus = 0
    readStatus = 0
    tempVMs = {}
    for vmname in vmnames:
        tempVMs[vmname] = None

    logging.debug("VBoxManageWin: runVMInfo(): instantiated")
    try:
        #run vboxmanage to get vm listing
        #Make sure this one isn't cleared before use too...
        vmListCmd = vmanagePath + " list vms"
        logging.debug("runVMInfo(): Collecting VM Names using cmd: " + vmListCmd)
#        readStatus = VMManage.MANAGER_READING
        # logging.debug("runVMInfo(): adding 1 "+ str(writeStatus))
        stdin, stdout, stderr = loggedssh.exec_command(vmListCmd)
        for out in stdout:
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
            if vm.name in vmnames:
                tempVMs[vm.name] = vm.UUID

        logging.debug("runVMInfo(): Found # VMS: " + str(len(tempVMs)))
        return tempVMs
    except Exception:
        logging.error("Error in runVMInfo(): An error occured ")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    finally:
        # readStatus = VMManage.MANAGER_IDLE
        writeStatus -= 1
        logging.debug("runVMInfo(): sub 1 "+ str(writeStatus))

def retrieveVMs(loggedssh, vmuuids = []):
    #get the machine readable info
    logging.debug("runVMInfo(): collecting VM extended info")
    writeStatus = 0
    readStatus = 0
    if vmuuids == []:
        return []
    vms = []
    try:
        vmShowInfoCmd = ""
        for vmuuid in vmuuids:
            vm = VM()
            vm.name = "NOT_FOUND"
            vm.state = "UNAVAILABLE"
            vm.uuid = vmuuid  
            vmShowInfoCmd = vmanagePath + " showvminfo " + str(vm.uuid) + " --machinereadable"
            logging.debug("runVMInfo(): Running " + vmShowInfoCmd)
            #p = Popen(vmShowInfoCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
            stdin, stdout, stderr = loggedssh.exec_command(vmShowInfoCmd)
            for out in stdout.readlines():
                res = re.match("name=", out)
                if res:
                    vm.name = out.strip().split("\"")[1].split("\"")[0]
                res = re.match("nic[0-9]+=", out)
                if res:
                    out = out.strip()
                    nicNum = out.split("=")[0][3:]
                    nicType = out.split("=")[1]
                    vm.adaptorInfo[nicNum] = nicType
                res = re.match("groups=", out)
                if res:
                    vm.groups = out.strip()
                res = re.match("VMState=", out)
                if res:
                    state = out.strip().split("\"")[1].split("\"")[0]
                    vm.state = state
                res = re.match("CurrentSnapshotUUID=", out)
                if res:
                    latestSnap = out.strip().split("\"")[1].split("\"")[0]
                    vm.latestSnapUUID = latestSnap

                logging.debug("runVMInfo(): Thread 2 completed: " + vmShowInfoCmd)
            vms.append(vm)
        return vms

    except Exception:
        logging.error("Error in runVMInfo(): An error occured ")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    finally:
        # readStatus = VMManage.MANAGER_IDLE
        writeStatus -= 1
        logging.debug("runVMInfo(): sub 1 "+ str(writeStatus))

if __name__=='__main__':
    username = sys.argv[1]
    password = sys.argv[2]
    host = sys.argv[3]
    period = 0
    if len(sys.argv) > 6:
        period = int(sys.argv[5])
    if len(sys.argv) == 7:
        logging_level = sys.argv[6]
        
        if "debug" in logging_level.lower():
            logging.getLogger().setLevel(logging.DEBUG)
        elif "error" in logging_level.lower():
            logging.getLogger().setLevel(logging.ERROR)
        elif "info" in logging_level.lower():
            logging.getLogger().setLevel(logging.INFO)
    configname = sys.argv[4]
    e = ExperimentConfigIO.getInstance()
    data, numclones = e.getExperimentVMRolledOut(configname)
    
    configvms = []
    for vmlist in data.values():
        logging.debug("VM_LIST: " + str(vmlist))
        for vm_rolled_out in vmlist:
            configvms.append(vm_rolled_out["name"])
            logging.debug("CONFIG VMS: " + str(configvms))
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, password=password)

        logging.info("Retrieving UUIDs for : " + str(len(configvms)) + " VMs...")
        vmUUIDs = retrieveVMs_UUID(client, configvms)
        #Print out missing VMs here...
        validUUIDs = []
        invalidVMNames = []
        for vmUUID in vmUUIDs:
            if vmUUIDs[vmUUID] == None:
                invalidVMNames.append(vmUUID)
            else:
                validUUIDs.append(vmUUID)
        for vmname in invalidVMNames:
            logging.error("******VM Not Found: " + vmname)

        while True:
            logging.info("SERVER: " + str(host))
            logging.info("Retrieving info for : " + str(len(validUUIDs)) + " VMs...")
            vms = retrieveVMs(client, validUUIDs)
            for vm in vms:
                if vm.state != "running":
                    logging.error("******VM: " + vm.name + " STATE " + vm.state)
                else:   
                    logging.info("VM: " + vm.name + " STATE " + vm.state)
            print(".", end='', flush=True)
            time.sleep(period)
    except Exception:
        logging.error("Error in runVMInfo(): An error occured ")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    finally:
        client.close()
        logging.debug("Closing ssh connection")
