import logging
import shlex
import argparse
import sys
import time
from engine.Manager.VMManage.VMManage import VMManage
from engine.Manager.ConnectionManage.ConnectionManageGuacRDP import ConnectionManageGuacRDP
from engine.Manager.PackageManage.PackageManageVBox import PackageManageVBox
from engine.Manager.ExperimentManage.ExperimentManageVBox import ExperimentManageVBox
from engine.Engine import Engine
import threading

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    #logging.basicConfig(filename='example.log',level=logging.DEBUG)
    logging.debug("Starting Program")
###Base Engine tests
    logging.debug("Instantiating Engine")
    e = Engine()
    logging.debug("engine object: " + str(e))

    logging.debug("Calling Engine.getInstance()")
    e = Engine.getInstance()
    logging.debug("engine object: " + str(e))

###Engine tests
    res = e.execute("engine status ")

###VMManage tests
    #Check status without refresh
    logging.debug("VM-Manage Status of defaulta without refresh" + str(res))
    res = e.execute("vm-manage vmstatus defaulta")
    res = e.execute("vm-manage mgrstatus")
    logging.debug("Returned: " + str(res))
    while res["writeStatus"] != VMManage.MANAGER_IDLE:
        time.sleep(.1)
        logging.debug("Waiting for vmstatus to complete...")
        res = e.execute("vm-manage mgrstatus")
        logging.debug("Returned: " + str(res))
    logging.debug("VM-Manage vmstatus complete.")
    
    #Refresh
    time.sleep(5)
    res = e.execute("vm-manage refresh")    
    res = e.execute("vm-manage mgrstatus")
    logging.debug("Returned: " + str(res))
    while res["writeStatus"] != VMManage.MANAGER_IDLE:
        time.sleep(.1)
        logging.debug("Waiting for vmrefresh to complete...")
        res = e.execute("vm-manage mgrstatus")
        logging.debug("Returned: " + str(res))
    logging.debug("VM-Manage vmstatus complete.")

    #Check status after refresh
    time.sleep(5)
    res = e.execute("vm-manage vmstatus defaulta")
    logging.debug("VM-Manage Status of defaulta: " + str(res))
    res = e.execute("vm-manage mgrstatus")
    logging.debug("Returned: " + str(res))
    while res["writeStatus"] != VMManage.MANAGER_IDLE:
        time.sleep(.1)
        logging.debug("Waiting for vmstatus to complete...")
        res = e.execute("vm-manage mgrstatus")
        logging.debug("Returned: " + str(res))
    logging.debug("VM-Manage vmstatus complete.")

###Packager tests
    ###import
    time.sleep(5)
    logging.debug("Importing RES file: " + str("samples\sample.res"))
    e.execute("packager import \"samples\sample.res\"")
    res = e.execute("packager status")
    logging.debug("Returned: " + str(res))
    while res["writeStatus"] != PackageManageVBox.PACKAGE_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for package import to complete...")
        res = e.execute("packager status")
        logging.debug("Returned: " + str(res))
    logging.debug("Package import complete.")

    #Refresh
    time.sleep(5)
    res = e.execute("vm-manage refresh")    
    res = e.execute("vm-manage mgrstatus")
    logging.debug("Returned: " + str(res))
    while res["writeStatus"] != VMManage.MANAGER_IDLE:
        time.sleep(.1)
        logging.debug("Waiting for vmrefresh to complete...")
        res = e.execute("vm-manage mgrstatus")
        logging.debug("Returned: " + str(res))
    logging.debug("VM-Manage vmstatus complete.")

    ###export
    time.sleep(5)
    logging.debug("Exporting experiment named: sample to " + "\"exported\sample with space\"")
    e.execute("packager export sample \"exported\sample with space\"")
    res = e.execute("packager status")
    while res["writeStatus"] != PackageManageVBox.PACKAGE_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for package export to complete...")
        res = e.execute("packager status")
    logging.debug("Package export complete.")    

###Experiment tests
    #####---Create Experiment Test#####
    logging.info("Creating Experiment")
    e.execute("experiment create sample")
    res = e.execute("experiment status")
    logging.debug("Waiting for experiment create to complete...")
    while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment create to complete...")
        res = e.execute("experiment status")
    logging.debug("Experiment create complete.")    

    #####---Start Experiment Test#####
    ##Note that any guestcontrol operations will require guest additions to be installed on the VM
    logging.info("Starting Experiment")
    e.execute("experiment start sample")
    res = e.execute("experiment status")
    logging.debug("Waiting for experiment start to complete...")
    while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment start to complete...")
        res = e.execute("experiment status")
    logging.debug("Experiment start complete.")    

    #####---Stop Experiment Test#####
    time.sleep(15)
    logging.info("Stopping Experiment")
    e.execute("experiment stop sample")
    res = e.execute("experiment status")
    logging.debug("Waiting for experiment stop to complete...")
    while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment stop to complete...")
        res = e.execute("experiment status")
    logging.debug("Experiment stop complete.")    

    #####---Restore Experiment Test#####
    time.sleep(5)
    logging.info("Restore Experiment")
    e.execute("experiment restore sample")
    res = e.execute("experiment status")
    logging.debug("Waiting for experiment restore to complete...")
    while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment restore to complete...")
        res = e.execute("experiment status")
    logging.debug("Experiment restore complete.")    

    #####---Remove Experiment Test#####
    time.sleep(5)
    logging.info("Remove Experiment")
    e.execute("experiment remove sample")
    res = e.execute("experiment status")
    logging.debug("Waiting for experiment remove to complete...")
    while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment remove to complete...")
        res = e.execute("experiment status")
    logging.debug("Experiment remove complete.")    

###Connection tests
    e.execute("conns status")
    #####---Connection Create Test#####
    #"sample", "192.168.99.100:8080", "guacadmin", "guacadmin", "/guacamole", "http", maxConnections="1", maxConnectionsPerUser="1", width="1400", height="1050", bitdepth="16"
    e.execute("conns create sample 192.168.99.100:8080 guacadmin guacadmin /guacamole http 1 1 1400 1050 16")
    logging.debug("Waiting for connection create to complete...")
    while e.execute("conns status")["writeStatus"] != ConnectionManageGuacRDP.CONNECTION_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for connection create to complete...")
        res = e.execute("conns status")
    logging.debug("Connection create complete.")

    #####---Connection Remove Test#####
    e.execute("conns remove sample 192.168.99.100:8080 guacadmin guacadmin /guacamole http")
    logging.debug("Waiting for connection remove to complete...")
    while e.execute("conns status")["writeStatus"] != ConnectionManageGuacRDP.CONNECTION_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for connection remove to complete...")
        res = e.execute("conns status")
    logging.debug("Connection remove complete.")

    #####---Connection Clear All Test#####
    e.execute("conns clear 192.168.99.100:8080 guacadmin guacadmin /guacamole http")
    logging.debug("Waiting for connection clear all to complete...")
    while e.execute("conns status")["writeStatus"] != ConnectionManageGuacRDP.CONNECTION_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for connection clear all to complete...")
        res = e.execute("conns status")
    logging.debug("Connection create complete.")

    # time.sleep(10) #alternative, check status until connection manager is complete and idle
    e.execute("conns status")
    e.execute("conns remove sample")
    
    # time.sleep(10) #alternative, check status until connection manager is complete and idle
    e.execute("conns status")
    e.execute("conns open sample 1 1")

    time.sleep(3) #allow some time for observation
    #quit
