import logging
import sys, traceback
import threading
import json
from engine.Manager.ConnectionManage.ConnectionManage import ConnectionManage
from engine.ExternalIFX.GuacIFX import GuacIFX
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from engine.Manager.ConnectionManage.ConnectionManageGuacRDP import ConnectionManageGuacRDP
import time

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    logging.debug("Instantiating ConnectionManageGuacRDP")

    c = ConnectionManageGuacRDP()
    logging.info("Creating connection")
    c.createConnections("sample", "127.0.0.1", "guacadmin", "guacadmin", "/guacamole", "http")

    logging.info("Operation Complete")