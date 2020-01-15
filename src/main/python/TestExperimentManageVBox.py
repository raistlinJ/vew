import logging
import time
import sys, traceback
import threading
import json
from engine.Manager.ExperimentManage.ExperimentManageVBox import ExperimentManageVBox
from engine.Manager.VMManage.VMManage import VMManage
from engine.Manager.VMManage.VBoxManage import VBoxManage
from engine.Manager.VMManage.VBoxManageWin import VBoxManageWin
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    logging.debug("Instantiating Engine")
    e = ExperimentManageVBox(initializeVMManage=True)

    e.createExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(1)
        logging.debug("Waiting for experiment create to complete...")

    # logging.info("Starting Experiment")
    # e.startExperiment("sample")
    # logging.debug("Experiment start complete.")    

    # #####---Stop Experiment Test#####
    # time.sleep(30)
    # logging.info("Stopping Experiment")
    # e.stopExperiment("sample")
    # logging.debug("Experiment stop complete.")      
