import logging
import sys, traceback
import threading
import json
from engine.Manager.ConnectionManage.ConnectionManage import ConnectionManage
from engine.ExternalIFX.GuacIFX import GuacIFX
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO

class ConnectionManageGuacRDP(ConnectionManage):
    def __init__(self):
        logging.debug("ConnectionManageGuacRDP(): instantiated")
        ConnectionManage.__init__(self)
        self.guacifx = GuacIFX()

    #abstractmethod
    def createConnections(self, configfilename):
        logging.debug("createConnections(): instantiated")
        t = threading.Thread(target=self.runCreateConnections, args=(configfilename,))
        t.start()
        return 0

    def runCreateConnections(self, configfilename):
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_CREATING
        #call guac backend API to make connections as specified in config file and then set the complete status
        #self.guacifx.createGuacEntries(inputFilename, guacHostname, guacUsername, guacPass, guacURLPath, guacConnMethod)
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE

    #abstractmethod
    def removeConnections(self, configfilename):
        logging.debug("removeConnections(): instantiated")
        t = threading.Thread(target=self.runRemoveConnections, args=(configfilename,))
        t.start()
        return 0

    def runRemoveConnections(self, configfilename):
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_REMOVING
        #call guac backend API to remove connections as specified in config file and then set the complete status
        #self.guacifx.removeGuacEntries(inputFilename, guacHostname, guacUsername, guacPass, guacURLPath, guacConnMethod)
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE

    #abstractmethod
    def openConnection(self, configfilename, experimentid, vmid):
        logging.debug("openConnection(): instantiated")
        t = threading.Thread(target=self.runRemoveConnections, args=(configfilename,))
        t.start()
        return 0

    def runOpenConnection(self, configfilename, experimentid, vmid):
        logging.debug("runOpenConnection(): instantiated")
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_OPENING
        #open an RDP session using configuration from systemconfigIO to the specified experimentid/vmid
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE

    #abstractmethod
    def getConnectionManageStatus(self):
        logging.debug("getConnectionManageStatus(): instantiated")
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus}