import logging
import sys, traceback
import threading
import json
from engine.Manager.ConnectionManage.ConnectionManage import ConnectionManage
from engine.ExternalIFX.GuacIFX import GuacIFX
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from guacapy import Guacamole

class ConnectionManageGuacRDP(ConnectionManage):
    def __init__(self):
        logging.debug("ConnectionManageGuacRDP(): instantiated")
        ConnectionManage.__init__(self)
        self.guacifx = GuacIFX()
        self.eco = ExperimentConfigIO()

    #abstractmethod
    def createConnections(self, configname):
        logging.debug("createConnections(): instantiated")
        t = threading.Thread(target=self.runCreateConnections, args=(configname,))
        t.start()
        return 0

    def runCreateConnections(self, configname, guacHostname,username,password,url_path, method):
        logging.debug("runCreateConnections(): instantiated")
        #call guac backend API to make connections as specified in config file and then set the complete status
        #self.guacifx.createGuacEntries(inputFilename, guacHostname, guacUsername, guacPass, guacURLPath, guacConnMethod)
        try:
            self.writeStatus = ConnectionManage.CONNECTION_MANAGE_CREATING
            #call vmManage to remove clones as specified in config file; wait and query the vmManage status, and then set the complete status
            clonevmjson = self.eco.getExperimentVMRolledOut(configname)
            for vm in clonevmjson.keys(): 
                vmName = vm
                logging.debug("runCreateConnections(): working with vm: " + str(vmName))
                #get names for clones and remove them
                for cloneinfo in clonevmjson[vm]:
                    cloneVMName = cloneinfo["name"]
                    ##### send command here
                    #######Guac connection##########
                    #guacConn = Guacamole('192.168.99.102',username='guacadmin',password='guacadmin',url_path='/guacamole',method='http')
                    #guacConn = Guacamole(guacHostname,username=guacUsername,password=guacPass,url_path=guacURLPath, method=guacConnMethod)
                    guacConn = Guacamole(guacHostname,username,password,url_path, method)
                    if guacConn == None:
                        logging.error("Error with guac connection... skipping: " + str(guacHostname) + " " + str(username))
                        exit()

            logging.debug("runCreateConnections(): Complete...")
            self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE
        except Exception:
            logging.error("runCreateConnections(): Error in runCreateConnections(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE

    #abstractmethod
    def removeConnections(self, configname):
        logging.debug("removeConnections(): instantiated")
        t = threading.Thread(target=self.runRemoveConnections, args=(configname,))
        t.start()
        return 0

    def runRemoveConnections(self, configname):
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_REMOVING
        #call guac backend API to remove connections as specified in config file and then set the complete status
        #self.guacifx.removeGuacEntries(inputFilename, guacHostname, guacUsername, guacPass, guacURLPath, guacConnMethod)
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE

    #abstractmethod
    def openConnection(self, configname, experimentid, vmid):
        logging.debug("openConnection(): instantiated")
        t = threading.Thread(target=self.runRemoveConnections, args=(configname,))
        t.start()
        return 0

    def runOpenConnection(self, configname, experimentid, vmid):
        logging.debug("runOpenConnection(): instantiated")
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_OPENING
        #open an RDP session using configuration from systemconfigIO to the specified experimentid/vmid
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE

    def createUser(self, guacConn, username, password):
        logging.debug("createConnAssociation(): Instantiated")
        try:
            ########User creation##########
            userCreatePayload = {"username":username, "password":password, "attributes":{ "disabled":"", "expired":"", "access-window-start":"", "access-window-end":"", "valid-from":"", "valid-until":"", "timezone":0}}
            guacConn.add_user(userCreatePayload)
        except Exception:
                logging.error("Error in createUser().")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                return None

    def createConnAssociation(self, guacConn, connName, username, ip, port):
        logging.debug("createConnAssociation(): Instantiated")
        try:
            #logic to add a user/connection and associate them together
            ########Connection creation##########
            connCreatePayload = {"name":connName,
            "parentIdentifier":"ROOT",
            "protocol":"rdp",
            "attributes":{"max-connections":"","max-connections-per-user":""},
            "activeConnections":0,
            "parameters":{
                "port":port,
                "enable-menu-animations":"true",
                "enable-desktop-composition":"true",
                "hostname":ip,
                "color-depth":"16",
                "enable-font-smoothing":"true",
                "ignore-cert":"true",
                "enable-drive":"false",
                "enable-full-window-drag":"true",
                "security":"",
                "password":"",
                "enable-wallpaper":"true",
                "create-drive-path":"true",
                "enable-theming":"true",
                "username":"",
                "console":"",
                "disable-audio":"true",
                "domain":"",
                "drive-path":"",
                "disable-auth":"",
                "server-layout":"",
                "width":"1280",
                "height":"768",
                "dpi":"",
                "resize-method":"display-update",
                "console-audio":"",
                "enable-printing":"",
                "preconnection-id":"",
                "enable-sftp":"",
                "sftp-port":""}}
            res = guacConn.add_connection(connCreatePayload)
            logging.debug("createConnAssociation(): Finished adding connection: " + str(res))
            connID = res['identifier']
            ########Connection Permission for User#########
            connPermPayload = [{"op":"add","path":"/connectionPermissions/"+connID,"value":"READ"}]
            guacConn.grant_permission(username, connPermPayload)
        except Exception:
                logging.error("Error in createConnAssociation().")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                return None

    #abstractmethod
    def getConnectionManageStatus(self):
        logging.debug("getConnectionManageStatus(): instantiated")
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus}