import logging
import shlex
import argparse
import sys
from time import sleep
from engine.Manager.VMManage.VMManage import VMManage
from engine.Manager.ConnectionManage.ConnectionManageGuacRDP import ConnectionManageGuacRDP
from engine.Manager.PackageManage.PackageManageVBox import PackageManageVBox
from engine.Manager.ExperimentManage.ExperimentManageVBox import ExperimentManageVBox
from engine.Engine import Engine
import threading

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.ERROR)
    #logging.basicConfig(filename='example.log',level=logging.DEBUG)
    logging.debug("Starting Program")
###Base Engine tests
    logging.debug("Instantiating Engine")
    e = Engine()
    logging.debug("engine object: " + str(e))

    logging.debug("Calling Engine.getInstance()")
    e = Engine.getInstance()
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
    while res["readStatus"] != VMManage.MANAGER_IDLE and res["readStatus"] != VMManage.MANAGER_UNKNOWN:
        sleep(1)
        logging.debug("Waiting for vmstatus to complete...")
        res = e.execute("vm-manage mgrstatus")
        logging.debug("Returned: " + str(res))
    logging.debug("VM-Manage vmstatus complete.")
    
    #Refresh
    sleep(5)
    res = e.execute("vm-manage refresh")    
    res = e.execute("vm-manage mgrstatus")
    logging.debug("Returned: " + str(res))
    while res["readStatus"] != VMManage.MANAGER_IDLE:
        sleep(1)
        logging.debug("Waiting for vmrefresh to complete...")
        res = e.execute("vm-manage mgrstatus")
        logging.debug("Returned: " + str(res))
    logging.debug("VM-Manage vmstatus complete.")

    #Check status after refresh
    sleep(5)
    res = e.execute("vm-manage vmstatus defaulta")
    logging.debug("VM-Manage Status of defaulta: " + str(res))
    res = e.execute("vm-manage mgrstatus")
    logging.debug("Returned: " + str(res))
    while res["readStatus"] != VMManage.MANAGER_IDLE:
        sleep(1)
        logging.debug("Waiting for vmstatus to complete...")
        res = e.execute("vm-manage mgrstatus")
        logging.debug("Returned: " + str(res))
    logging.debug("VM-Manage vmstatus complete.")

###Packager tests
    ###import
    sleep(5)
    logging.debug("Importing RES file: " + str("samples\sample.res"))
    e.execute("packager import \"samples\sample.res\"")
    res = e.execute("packager status")
    logging.debug("Returned: " + str(res))
    while res["writeStatus"] != PackageManageVBox.PACKAGE_MANAGE_COMPLETE:
        sleep(1)
        logging.debug("Waiting for package import to complete...")
        res = e.execute("packager status")
        logging.debug("Returned: " + str(res))
    logging.debug("Package import complete.")

    #Refresh
    sleep(5)
    res = e.execute("vm-manage refresh")    
    res = e.execute("vm-manage mgrstatus")
    logging.debug("Returned: " + str(res))
    while res["readStatus"] != VMManage.MANAGER_IDLE:
        sleep(1)
        logging.debug("Waiting for vmrefresh to complete...")
        res = e.execute("vm-manage mgrstatus")
        logging.debug("Returned: " + str(res))
    logging.debug("VM-Manage vmstatus complete.")

    ###export
    sleep(5)
    logging.debug("Exporting experiment named: sample to " + "\"exported\sample with space\"")
    e.execute("packager export sample \"exported\sample with space\"")
    res = e.execute("packager status")
    while res["writeStatus"] != PackageManageVBox.PACKAGE_MANAGE_COMPLETE:
        sleep(1)
        logging.debug("Waiting for package export to complete...")
        res = e.execute("packager status")
    logging.debug("Package export complete.")    
    
    #####---Create Experiment Test#####
    logging.info("Creating Experiment")
    e.execute("experiment create sample")
    res = e.execute("experiment status")
    logging.debug("Waiting for experiment create to complete...")
    while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
        sleep(1)
        logging.debug("Waiting for experiment create to complete...")
        res = e.execute("experiment status")
    logging.debug("Experiment create complete.")    

#     #####---Start Experiment Test#####
#     logging.info("Starting Experiment")
#     e.execute("experiment start sample")
#     res = e.execute("experiment status")
#     logging.debug("Waiting for experiment start to complete...")
#     while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
#         sleep(1)
#         logging.debug("Waiting for experiment start to complete...")
#         res = e.execute("experiment status")
#     logging.debug("Experiment start complete.")    

#     #####---Stop Experiment Test#####
#     sleep(5)
#     logging.info("Stopping Experiment")
#     e.execute("experiment stop sample")
#     res = e.execute("experiment status")
#     logging.debug("Waiting for experiment stop to complete...")
#     while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
#         sleep(1)
#         logging.debug("Waiting for experiment stop to complete...")
#         res = e.execute("experiment status")
#     logging.debug("Experiment stop complete.")    

# ###Connection tests
#     # sleep(60)#alternative, check status until packager is complete and idle
#     e.execute("conns status")
#     e.execute("conns create sample")

#     # sleep(10) #alternative, check status until connection manager is complete and idle
#     e.execute("conns status")
#     e.execute("conns remove sample")
    
#     # sleep(10) #alternative, check status until connection manager is complete and idle
#     e.execute("conns status")
#     e.execute("conns open sample 1 1")


#     #####---Remove Experiment Test#####
#     sleep(5)
#     logging.info("Remove Experiment")
#     e.execute("experiment remove sample")
#     res = e.execute("experiment status")
#     logging.debug("Waiting for experiment remove to complete...")
#     while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
#         sleep(1)
#         logging.debug("Waiting for experiment remove to complete...")
#         res = e.execute("experiment status")
#     logging.debug("Experiment remove complete.")    

#     sleep(3) #allow some time for observation
#     #quit

