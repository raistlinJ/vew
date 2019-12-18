import logging
import sys, traceback
from engine.Manager.ConnectionManage.ConnectionManage import ConnectionManage

class ConnectionManageGuacRDP(ConnectionManage):
    def __init__(self):
        logging.debug("ConnectionManageGuacRDP(): instantiated")
        ConnectionManage.__init__(self)

    #abstractmethod
    def createConnections(self, configfilename):
        logging.debug("createConnections(): instantiated")
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_CREATING
        #call guac backend API to make connections as specified in config file and then set the complete status
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE

    #abstractmethod
    def removeConnections(self, configfilename):
        logging.debug("removeConnections(): instantiated")
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_REMOVING
        #call guac backend API to remove connections as specified in config file and then set the complete status
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE

    #abstractmethod
    def openConnection(self, configfilename, experimentid, vmid):
        logging.debug("createConnections(): instantiated")
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_OPENING
        #call guac backend API to remove connections as specified in config file and then set the complete status
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE

    #abstractmethod
    def getConnectionManageStatus(self):
        logging.debug("getConnectionManageStatus(): instantiated")
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus}