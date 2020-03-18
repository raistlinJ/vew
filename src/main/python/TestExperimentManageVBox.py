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
    vbm = VBoxManageWin()
    e = ExperimentManageVBox(vbm)
    ####---Create Experiment Test#####
    logging.info("Creating Experiment")
    e.createExperiment("sample")
    result = e.getExperimentManageStatus()["writeStatus"]
    while result != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment create to complete...")
        result = e.getExperimentManageStatus()["writeStatus"]
    
    #####---Start Experiment Test#####
    logging.info("Starting Experiment")
    e.startExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment start to complete...")
    logging.debug("Experiment start complete.")    

    #####---Pause Experiment Test#####
    logging.info("Pause Experiment")
    e.pauseExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment pause to complete...")
    logging.debug("Experiment pause complete.")

    #####---Stop Experiment Test#####
    logging.info("Stopping Experiment")
    e.stopExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment stop to complete...")
    logging.debug("Experiment stop complete.")    

    #####---Suspend Experiment Test#####
    logging.info("Suspend Experiment")
    e.suspendExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment suspend to complete...")
    logging.debug("Experiment suspend complete.")    

    #####---Restore Experiment Test#####
    logging.info("Restoring Experiment")
    e.restoreExperiment("sample")
    while e.getExperimentManageStatus()["writeStatus"] != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment stop to complete...")
    logging.debug("Experiment stop complete.")

    # #####---Remove Experiment Test#####
    logging.info("Removing Experiment")
    e.removeExperiment("sample")
    result = e.getExperimentManageStatus()["writeStatus"]
    while result != e.EXPERIMENT_MANAGE_COMPLETE:
        time.sleep(.1)
        logging.debug("Waiting for experiment create to complete...")
        result = e.getExperimentManageStatus()["writeStatus"]


