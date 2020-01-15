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
from engine.Manager.VMManage.VBoxManageWin import VBoxManageWin
        
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Starting Program")
    logging.info("Instantiating VBoxManageWin")
    
    testvmname = "defaulta"
    
    vbm = VBoxManageWin()
    
    logging.info("Status without refresh: ")
    vbm.getManagerStatus()
    
    logging.info("Refreshing VM Info")
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

    logging.info("Testing clone -- creating 1 clone of " + str(testvmname))
    vbm.cloneVM(testvmname, cloneName=str(testvmname + "1"), cloneSnapshots="true", linkedClones="true", groupName="Test Group")
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("testing clone waiting for manager to finish query..." + str(vbm.getManagerStatus()["writeStatus"]))
        sleep(1)
    
    logging.info("Refreshing after clone since we added a new VM")
    vbm.refreshAllVMInfo()
    while vbm.getManagerStatus()["readStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        sleep(1)
    logging.info("Refreshing VMs Info - AFTER")

    logging.info("Testing set interface 1 on clone -- " + str(testvmname + "1"))
    vbm.configureVMNet(vmName=str(testvmname + "1"), netNum="1", netName="testintnet1")
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        sleep(1)

    logging.info("Testing set interface 2 on clone -- " + str(testvmname + "1"))
    vbm.configureVMNet(vmName=str(testvmname + "1"), netNum="2", netName="testintnet2")
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        sleep(1)

    logging.info("Testing enable VRDP on clone -- " + str(testvmname + "1") + " port 1001")
    vbm.enableVRDPVM(str(testvmname + "1"), "1001")
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        sleep(1)

    logging.info("Testing snapshot after clone -- " + str(testvmname + "1"))
    vbm.snapshotVM(str(testvmname + "1"))
    while vbm.getManagerStatus()["writeStatus"] != VMManage.MANAGER_IDLE:
        logging.info("waiting for manager to finish query...")
        sleep(1)
    
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
