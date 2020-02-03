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
    c.createConnections("sample", "192.168.99.100:8080", "guacadmin", "guacadmin", "/guacamole", "http", maxConnections="1", maxConnectionsPerUser="1", width="1280", height="1024")
    time.sleep(10)
    logging.info("Removing connection")
    c.removeConnections("sample", "192.168.99.100:8080", "guacadmin", "guacadmin", "/guacamole", "http")

    logging.info("Creating connection")
    c.createConnections("sample", "192.168.99.100:8080", "guacadmin", "guacadmin", "/guacamole", "http")
    time.sleep(10)
    logging.info("Clearing all entries")
    c.clearAllConnections("192.168.99.100:8080", "guacadmin", "guacadmin", "/guacamole", "http")

    logging.info("Operation Complete")