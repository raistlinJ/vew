import logging
import sys, traceback
import threading
import json
import os
import csv
from engine.Manager.ConnectionManage.ConnectionManage import ConnectionManage
from engine.ExternalIFX.GuacIFX import GuacIFX
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from engine.Configuration.UserPool import UserPool
from guacapy import Guacamole

class ConnectionManageGuacRDP(ConnectionManage):
    def __init__(self):
        logging.debug("ConnectionManageGuacRDP(): instantiated")
        ConnectionManage.__init__(self)
        self.guacifx = GuacIFX()
        self.eco = ExperimentConfigIO()

    #abstractmethod
    def createConnections(self, configname, guacHostname, username, password, url_path, method, maxConnections="", maxConnectionsPerUser="", width="1400", height="1050", bitdepth="16", creds_file=""):
        logging.debug("createConnections(): instantiated")
        t = threading.Thread(target=self.runCreateConnections, args=(configname, guacHostname, username, password, url_path, method, maxConnections, maxConnectionsPerUser, width, height, bitdepth, creds_file))
        t.start()
        return 0

    def runCreateConnections(self, configname, guacHostname, username, password,url_path, method, maxConnections, maxConnectionsPerUser, width, height, bitdepth, creds_file):
        logging.debug("runCreateConnections(): instantiated")
        #call guac backend API to make connections as specified in config file and then set the complete status
        #self.guacifx.createGuacEntries(inputFilename, guacHostname, guacUsername, guacPass, guacURLPath, guacConnMethod)
        userpool = UserPool()
        try:
            self.writeStatus = ConnectionManage.CONNECTION_MANAGE_CREATING
            logging.debug("runCreateConnection(): guacHostname: " + str(guacHostname) + " username/pass: " + username + " url_path: " + url_path + " method: " + str(method) + " creds_file: " + creds_file)
            guacConn = Guacamole(guacHostname,username=username,password=password,url_path=url_path,method=method)
            if guacConn == None:
                logging.error("runCreateConnection(): Error with guac connection... skipping: " + str(guacHostname) + " " + str(username))
                self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE
                return -1
            if creds_file == "":
                userpool.addFromBase()
            else:
                userpool.addFromCSV(creds_file)
            if userpool == None:
                logging.error("runCreateConnection(): User/Pass could not be created from file: " + str(creds_file) + " using default: user")
                userpool.addFromBase()

            #first create the users for each set of VMs
            createdUsers = {}
            username = ""
            password = ""
            clonevmjson, numclones = self.eco.getExperimentVMRolledOut(configname)
            for vm in clonevmjson.keys(): 
                vmName = vm
                logging.debug("runCreateConnections(): working with vm: " + str(vmName))
                #get names for clones
                for cloneinfo in clonevmjson[vm]:
                    # if vrdpPort exists, then we know it's enabled for this vm; let's set it up
                    if "vrdpPort" in cloneinfo:
                        #keep track of users/connections using the groupnum
                        currGroupNum = cloneinfo["groupNum"]                        
                        ipAddress = cloneinfo["ip-address"]
                        cloneVMName = cloneinfo["name"]
                        vrdpPort = cloneinfo["vrdpPort"]

                        # Create a User if we haven't done so for this group/set and it doesn't exist
                        if createdUsers == {} or currGroupNum not in createdUsers:
                            (username, password) = userpool.popUserPass()
                            logging.debug( "Creating Username: " + username)
                            createdUsers[currGroupNum] = (username, password)

                            logging.debug( "Creating Username in Guac: " + username)
                            try:
                                result = self.createUser(guacConn, username, password)
                                if result == "already_exists":
                                    logging.debug("User already exists; skipping...")
                            except Exception:
                                logging.error("runCreateConnections(): Error in runCreateConnections(): when trying to add user.")
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                traceback.print_exception(exc_type, exc_value, exc_traceback)
                        #otherwise add it to the list known created users
                        else:
                            (username, password) = createdUsers[currGroupNum]

                        # Associate a User and Connection
                        logging.debug( "Creating Connection for Username: " + username)
                        try:
                            result = self.createConnAssociation(guacConn, cloneVMName, username, ipAddress, vrdpPort, maxConnections, maxConnectionsPerUser, width, height, bitdepth)
                            if result == "already_exists":
                                logging.debug("Connection already exists; skipping...")
                        except Exception:
                                logging.error("runCreateConnections(): Error in runCreateConnections(): when trying to add connection.")
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                #traceback.print_exception(exc_type, exc_value, exc_traceback)

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
    def clearAllConnections(self, guacHostname, username, password, url_path, method):
        logging.debug("clearAllConnections(): instantiated")
        t = threading.Thread(target=self.runClearAllConnections, args=(guacHostname, username, password, url_path, method))
        t.start()
        return 0

    def runClearAllConnections(self, guacHostname, username, password, url_path, method):
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_REMOVING
        #sample guacConn = Guacamole(192.168.99.102',username='guacadmin',password='guacadmin',url_path='/guacamole',method='http')
        logging.debug("runClearAllConnections(): guacHostname: " + str(guacHostname) + " username/pass: " + username + " url_path: " + url_path + " method: " + str(method))
        guacConn = Guacamole(guacHostname,username=username,password=password,url_path=url_path,method=method)
        if guacConn == None:
            logging.error("Error with guac connection... skipping: " + str(guacHostname) + " " + str(username))
            self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE
            return -1

        # Get list of all users
        usernames = guacConn.get_users()
        for username in usernames:
            logging.debug( "Removing Username: " + username)
            try:
                guacConn.delete_user(username)
            except Exception:
                logging.error("runClearAllConnections(): Error in runClearAllConnections(): when trying to remove user.")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                #traceback.print_exception(exc_type, exc_value, exc_traceback)
        # Remove All Connections
        connections = guacConn.get_connections()
        logging.debug( "Retrieved Connections: " + str(connections))
        if "childConnections" in connections:
            for connection in connections["childConnections"]:
                logging.debug( "Removing Connection: " + str(connection))
                try:
                    guacConn.delete_connection(connection["identifier"])
                except Exception:
                        logging.error("runClearAllConnections(): Error in runClearAllConnections(): when trying to remove connection.")
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        #traceback.print_exception(exc_type, exc_value, exc_traceback)
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE

    #abstractmethod
    def removeConnections(self, configname, guacHostname, username, password, url_path, method, creds_file=""):
        logging.debug("removeConnections(): instantiated")
        t = threading.Thread(target=self.runRemoveConnections, args=(configname,guacHostname, username, password, url_path, method, creds_file))
        t.start()
        return 0

    def runRemoveConnections(self, configname, guacHostname, username, password, url_path, method, creds_file):
        self.writeStatus = ConnectionManage.CONNECTION_MANAGE_REMOVING
        logging.debug("runRemoveConnections(): instantiated")
        #call guac backend API to make connections as specified in config file and then set the complete status
        userpool = UserPool()
        try:
            self.writeStatus = ConnectionManage.CONNECTION_MANAGE_CREATING
            #sample guacConn = Guacamole(192.168.99.102',username='guacadmin',password='guacadmin',url_path='/guacamole',method='http')
            logging.debug("runRemoveConnections(): guacHostname: " + str(guacHostname) + " username/pass: " + username + " url_path: " + url_path + " method: " + str(method))
            guacConn = Guacamole(guacHostname,username=username,password=password,url_path=url_path,method=method)
            if guacConn == None:
                logging.error("runRemoveConnections(): Error with guac connection... skipping: " + str(guacHostname) + " " + str(username))
                self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE
                return -1
            if creds_file == "":
                userpool.addFromBase()
            else:
                userpool.addFromCSV(creds_file)
            if userpool == None:
                logging.error("runRemoveConnections(): User/Pass could not be generated from file: " + str(creds_file) + " using default: user")
                userpool.addFromBase()

            #first generate the users for each set of VMs
            removedUsers = {}
            username = ""
            password = ""
            clonevmjson, numclones = self.eco.getExperimentVMRolledOut(configname)
            for vm in clonevmjson.keys(): 
                vmName = vm
                logging.debug("runRemoveConnections(): working with vm: " + str(vmName))
                #get names for clones
                for cloneinfo in clonevmjson[vm]:
                    # if vrdpPort exists, then we know it's enabled for this vm; let's set it up
                    if "vrdpPort" in cloneinfo:
                        #keep track of users/connections using the groupnum
                        currGroupNum = cloneinfo["groupNum"]                        
                        ipAddress = cloneinfo["ip-address"]
                        cloneVMName = cloneinfo["name"]
                        vrdpPort = cloneinfo["vrdpPort"]
                        # Generate a User if we haven't done so yet
                        if removedUsers == {} or currGroupNum not in removedUsers:
                            (username, password) = userpool.popUserPass()
                            removedUsers[currGroupNum] = (username, password)
                            logging.debug( "Removing Username in Guac: " + username)
                            try:
                                result = self.removeUser(guacConn, username)
                                if result == "already_exists":
                                    logging.debug("User already exists; skipping...")
                            except Exception:
                                logging.error("runRemoveConnections(): Error in runRemoveConnections(): when trying to remove user.")
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                #traceback.print_exception(exc_type, exc_value, exc_traceback)
                        #otherwise add it to the list known removed users
                        else:
                            (username, password) = removedUsers[currGroupNum]

                        # DisAssociate a User and Connection
                        logging.debug( "Removing Connection for Username: " + username)
                        try:
                            result = self.removeConnAssociation(guacConn, cloneVMName)
                            if result == "":
                                logging.debug("Connection could not be removed; skipping...")
                        except Exception:
                                logging.error("runRemoveConnections(): Error in runRemoveConnections(): when trying to remove connection.")
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                traceback.print_exception(exc_type, exc_value, exc_traceback)

            logging.debug("runRemoveConnections(): Complete...")
            self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE
        except Exception:
            logging.error("runRemoveConnections(): Error in runRemoveConnections(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ConnectionManage.CONNECTION_MANAGE_COMPLETE
            return
        finally:
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
        logging.debug("createUser(): Instantiated")
        try:
            ########User creation##########
            userCreatePayload = {"username":username, "password":password, "attributes":{ "disabled":"", "expired":"", "access-window-start":"", "access-window-end":"", "valid-from":"", "valid-until":"", "timezone":0}}
            result = guacConn.add_user(userCreatePayload)
            return result
        except Exception as e:
            logging.error("Error in createUser().")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # Extract unformatter stack traces as tuples
            trace_back = traceback.extract_tb(exc_traceback)
            #traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def removeUser(self, guacConn, username):
        logging.debug("removeUser(): Instantiated")
        try:
            ########User removal##########
            result = guacConn.delete_user(username)
            return result
        except Exception as e:
            logging.error("Error in removeUser().")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # Extract unformatter stack traces as tuples
            trace_back = traceback.extract_tb(exc_traceback)
            #traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def createConnAssociation(self, guacConn, connName, username, ip, port, maxConnections, maxConnectionsPerUser, width, height, bitdepth):
        logging.debug("createConnAssociation(): Instantiated")
        try:
            #logic to add a user/connection and associate them together
            ########Connection creation##########
            connCreatePayload = {"name":connName,
            "parentIdentifier":"ROOT",
            "protocol":"rdp",
            "attributes":{"max-connections":maxConnectionsPerUser, "max-connections-per-user":maxConnectionsPerUser},
            "activeConnections":0,
            "parameters":{
                "port":port,
                "enable-menu-animations":"true",
                "enable-desktop-composition":"true",
                "hostname":ip,
                "color-depth":bitdepth,
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
                "width":width,
                "height":height,
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
        except Exception as e:
            logging.error("Error in createConnAssociation(). Did not add connection or assign relation!")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(exc_traceback)
            #TODO: This doesn't quite work, but it'd be nice to get the specific error to return it
            for trace in trace_back:
                if "already exists" in str(trace):
                    return "already_exists"
            #traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def removeConnAssociation(self, guacConn, connName):
        logging.debug("removeConnAssociation(): Instantiated")
        try:
            ########Connection removal##########
            logging.debug("removeConnAssociation(): getting connection by name: " + str(connName))
            res = guacConn.get_connection_by_name(connName)
            logging.debug("removeConnAssociation(): result: " + str(res))
            connID = res['identifier']
            ########Connection Permission for User#########
            guacConn.delete_connection(connID)
        except Exception as e:
            logging.error("Error in removeConnAssociation(). Did not remove connection or relation!")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(exc_traceback)
            #traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    #abstractmethod
    def getConnectionManageStatus(self):
        logging.debug("getConnectionManageStatus(): instantiated")
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus}

    def get_user_pass_frombase(self, base, num_users):
        logging.debug("get_user_pass_frombase(): instantiated")
        #not efficient at all, but it's a quick lazy way to do it:
        answer = []
        for i in range(1,num_users+1):
            answer.append(((str(base)+str(i),str(base)+str(i))))
        return answer

    def get_user_pass_fromfile(self, filename):
        logging.debug("get_user_pass_fromfile(): instantiated")
        #not efficient at all, but it's a quick lazy way to do it:
        answer = []
        i = 0
        try:
            if os.path.exists(filename) == False:
                logging.error("getConnectionManageStatus(): Filename: " + filename + " does not exists; returning")
                return None
            with open(filename) as infile:
                reader = csv.reader(infile, delimiter=" ")
                for user, password in reader:
                    i = i+1
                    answer.append((user, password))
            # if len(answer) < num_users:
            #     logging.error("getConnectionManageStatus(): file does not have enough users: " + len(answer) + "; returning")
            #     return None
            return answer
        except Exception as e:
            logging.error("Error in getConnectionManageStatus().")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(exc_traceback)
            #traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None