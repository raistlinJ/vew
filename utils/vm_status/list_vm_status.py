#!/usr/bin/env bash

import paramiko
import sys, traceback
import logging
from engine.Engine import Engine
from engine.Manager.VMManage.VM import VM
import re

vmanage_path = "VBoxManage"
writeStatus = 0
readStatus = 0

def getVMStatus(loggedssh, vmName):
    writeStatus = 0
    readStatus = 0
    tempVMs = {}

    logging.debug("VBoxManageWin: runVMInfo(): instantiated")
    try:
        #run vboxmanage to get vm listing
        #Make sure this one isn't cleared before use too...
        vmListCmd = vmanage_path + " list vms"
        logging.debug("runVMInfo(): Collecting VM Names using cmd: " + vmListCmd)
#        readStatus = VMManage.MANAGER_READING
        # logging.debug("runVMInfo(): adding 1 "+ str(writeStatus))
        stdin, stdout, stderr = loggedssh.exec_command(vmListCmd)
        for line in stdout:
            splitOut = line.split("{")
            vm = VM()
            tmpname = splitOut[0].strip()
            #has to be at least one character and every name has a start and end quote
            if len(tmpname) > 2:
                vm.name = splitOut[0].strip()[1:-1]
            else: 
                break
            vm.UUID = splitOut[1].split("}")[0].strip()
            # logging.debug("UUID: " + vm.UUID)
            tempVMs[vm.name] = vm

        logging.debug("runVMInfo(): Found # VMS: " + str(len(tempVMs)))

        if vmName not in tempVMs:
            logging.error("runVMInfo(): VM was not found/registered: " + vmName)
            return

        #get the machine readable info
        logging.debug("runVMInfo(): collecting VM extended info")
        vmShowInfoCmd = ""
        vmShowInfoCmd = vmanage_path + " showvminfo " + str(tempVMs[vmName].UUID) + " --machinereadable"
        logging.debug("runVMInfo(): Running " + vmShowInfoCmd)
        #p = Popen(vmShowInfoCmd, stdout=PIPE, stderr=PIPE, encoding="utf-8")
        stdin, stdout, stderr = loggedssh.exec_command(vmShowInfoCmd)
        for line in stdout.readlines():
            #match example: nic1="none"
            res = re.match("nic[0-9]+=", out)
            if res:
                out = out.strip()
                nicNum = out.split("=")[0][3:]
                nicType = out.split("=")[1]
                tempVMs[vmName].adaptorInfo[nicNum] = nicType
            res = re.match("groups=", out)
            if res:
                # logging.debug("Found groups: " + out + " added to " + tempVMs[vmName].name)
                tempVMs[vmName].groups = out.strip()
            res = re.match("VMState=", out)
            if res:
                # logging.debug("Found vmState: " + out + " added to " + tempVMs[vmName].name)
                state = out.strip().split("\"")[1].split("\"")[0]
                tempVMs[vmName].state = state
            res = re.match("CurrentSnapshotUUID=", out)
            if res:
                # logging.debug("Found snaps: " + out + " added to " + tempVMs[vmName].latestSnapUUID)
                latestSnap = out.strip().split("\"")[1].split("\"")[0]
                tempVMs[vmName].latestSnapUUID = latestSnap

        logging.debug("runVMInfo(): Thread 2 completed: " + vmShowInfoCmd)

        return tempVMs
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

    client = paramiko.SSHClient()
    #client.get_host_keys().add('ssh.example.com', 'ssh-rsa', key)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    vmData = getVMStatus(client, "SideQuests")
    for vm in vmData:
        print("VM: " + str(vm))
    client.close()
