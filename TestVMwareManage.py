from subprocess import Popen, PIPE
import subprocess
import sys
from sys import argv, platform
import traceback
import logging
import shlex
import threading
import time
from engine.Manager.VMManage.VMManage import VMManage
from engine.Manager.VMManage.VM import VM
import os
import re
import configparser
from engine.Configuration.SystemConfigIO import SystemConfigIO
from engine.Manager.VMManage.VMwareManage import VMwareManage
        
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Starting Program")
    logging.info("Instantiating VMwareManageWin")
    s = SystemConfigIO()
    vmpath = s.getConfig()["VMWARE"]["VMANAGE_VM_PATH"]

    testvmname = os.path.join(vmpath,"defaulta/defaulta.vmx")
    
    vbm = VMwareManage()
    
    logging.info("Status without refresh: ")
    vbm.getManagerStatus()
    
    logging.info("Refreshing VM Info")
    for vm in vbm.vms:
        logging.info("VM Info:\r\n" + str(vm))
    vbm.refreshAllVMInfo()   
    result = vbm.getManagerStatus()["writeStatus"]
    while result != vbm.MANAGER_IDLE:
    #waiting for manager to finish query...
        result = vbm.getManagerStatus()["writeStatus"]
        time.sleep(.1)
    logging.info("Refreshing VMs Info - AFTER")

    #get vm info from objects
    for vm in vbm.vms:
        logging.info("VM Info:\r\nName: " + str(vbm.vms[vm].name) + "\r\nState: " + str(vbm.vms[vm].state) + "\r\n" + "Groups: " + str(vbm.vms[vm].groups) + "\r\n" + "latestSnap: " + str(vbm.vms[vm].latestSnapUUID) + "\r\n")
        for adaptor in vbm.vms[vm].adaptorInfo:
            logging.info("adaptor: " + str(adaptor) + " Type: " + str(vbm.vms[vm].adaptorInfo[adaptor]) + "\r\n")
    
    logging.info("Refreshing single VM Info--")
    logging.info("Result: " + str(vbm.refreshVMInfo(testvmname)))

    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        time.sleep(.1)
    
    logging.info("Status for " + testvmname)
    logging.info(vbm.getVMStatus(testvmname))

    logging.info("Testing clone -- creating 1 clone of " + str(testvmname))
    groupName = "sampleGroup"
    tmpCloneName = os.path.join(vmpath,groupName,(os.path.basename(testvmname)[:-4]+"1.vmx"))  
    
    vbm.cloneVM(testvmname, cloneName=str(tmpCloneName), cloneSnapshots="true", linkedClones="true", groupName=groupName)
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("testing clone waiting for manager to finish query..." + str(vbm.getManagerStatus()["writeStatus"]))
        time.sleep(.1)
    
    logging.info("Refreshing after clone since we added a new VM")
    vbm.refreshAllVMInfo()
    result = vbm.getManagerStatus()["writeStatus"]
    while result != vbm.MANAGER_IDLE:
    #waiting for manager to finish query...
        result = vbm.getManagerStatus()["writeStatus"]
        time.sleep(.1)
    logging.info("Refreshing VMs Info - AFTER")

    #get vm info from objects
    for vm in vbm.vms:
        logging.info("VM Info:\r\nName: " + str(vbm.vms[vm].name) + "\r\nState: " + str(vbm.vms[vm].state) + "\r\n" + "Groups: " + str(vbm.vms[vm].groups) + "\r\n" + "latestSnap: " + str(vbm.vms[vm].latestSnapUUID) + "\r\n")
        for adaptor in vbm.vms[vm].adaptorInfo:
            logging.info("adaptor: " + str(adaptor) + " Type: " + str(vbm.vms[vm].adaptorInfo[adaptor]) + "\r\n")

    logging.info("Testing set interface 1 on clone -- " + tmpCloneName)
    vbm.configureVMNet(vmName=tmpCloneName, netNum="1", netName="testintnet1")
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        time.sleep(.1)

    logging.info("Testing set interface 2 on clone -- " + tmpCloneName)
    vbm.configureVMNet(vmName=tmpCloneName, netNum="2", netName="testintnet2")
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        time.sleep(.1)

    logging.info("Testing enable VRDP on clone -- " + tmpCloneName + " port 1001")
    vbm.enableVRDPVM(tmpCloneName, "1001")
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        time.sleep(.1)

    logging.info("Testing snapshot after clone -- " + tmpCloneName)
    vbm.snapshotVM(tmpCloneName)
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        time.sleep(.1)

    logging.info("Testing remove -- removing 1 clone of " + str(testvmname))
    groupName = "sampleGroup"
    tmpCloneName = os.path.join(vmpath,groupName,(os.path.basename(testvmname)[:-4]+"1.vmx"))  
    
    vbm.removeVM(tmpCloneName)
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("testing clone waiting for manager to finish query..." + str(vbm.getManagerStatus()["writeStatus"]))
        time.sleep(.1)

    logging.info("----Testing VM commands-------")
    logging.info("----Start-------")
    vbm.startVM(testvmname)
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        time.sleep(.1)
    logging.info("----Waiting 5 seconds to pause -------")
    time.sleep(5)

    vbm.pauseVM(testvmname)
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        time.sleep(.1)
    logging.info("----Waiting 5 seconds to resume -------")
    time.sleep(5)

    vbm.snapshotVM(testvmname)
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        time.sleep(.1)
    logging.info("----Waiting 5 seconds to snapshot -------")
    time.sleep(5)

    vbm.unpauseVM(testvmname)
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        time.sleep(.1)
    logging.info("----Waiting 5 seconds to save state-------")
    time.sleep(5)

    vbm.suspendVM(testvmname)
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        time.sleep(.1)
    logging.info("----Waiting 5 seconds to resume -------")
    time.sleep(5)
    
    vbm.startVM(testvmname)
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        time.sleep(.1)
    logging.info("----Waiting 5 seconds to stop-------")
    time.sleep(5)
# ##Test guestCommands -- only works when guest additions is installed
#     # cmd1 = "run --exe \"/bin/bash\" --username researchdev --password toor --wait-stdout --wait-stderr -- -l -c \"echo toor | sudo -S /usr/bin/find /etc/ | tee /tmp/out.txt | cat && sleep 10 && cat /tmp/out.txt\""
#     # cmd2 = "copyfrom --username researchdev --password toor --verbose --follow -R /tmp/ \"C:\\Users\\Desktop\\tmp2\""

#     # guestCmds = [cmd1,cmd2]

#     # vbm.guestCommands(testvmname, guestCmds)
#     # while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
#     #     logging.info("waiting for manager to finish reading/writing...")
#     #     time.sleep(.1)
#     # logging.info("----Waiting 15 seconds to stop-------")
#     # time.sleep(15)
# ##Test guestCommands -- only works when guest additions is installed

    vbm.stopVM(testvmname)
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        time.sleep(.1)

    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE and vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish reading/writing...")
        time.sleep(.1)

    time.sleep(10)
    logging.info("Final Manager Status: " + str(vbm.getManagerStatus()))

    logging.info("Completed Exiting...")
