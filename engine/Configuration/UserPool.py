import logging
import os
import sys, traceback
import csv
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO

class UserPool():
    def __init__(self):
        logging.debug("UserPool(): instantiated")
        self.eco = ExperimentConfigIO.getInstance()
        self.filepool = []
        self.basepool = []
        self.num_created_fromfile = 0
        self.num_created_frombase = 0

    def addFromCSV(self, csvfilename, remove_invalid_chars=True):
        logging.debug("addFromCSV(): instantiated")
        #quick lazy way to generate the users/passes from csv:
        i = 0
        if csvfilename == None:
            logging.warning("addFromCSV(): csvfilename was None cannot create users from file")
            return
        try:
            if os.path.exists(csvfilename) == False:
                logging.error("addFromCSV(): Filename: " + csvfilename + " does not exists; cannot create users from file")
                return None
            with open(csvfilename) as infile:
                reader = csv.reader(infile, delimiter=" ")
                for user, password in reader:
                    i = i+1
                    if remove_invalid_chars:
                        user = ''.join(e for e in user if e.isalnum())
                    self.num_created_fromfile+=1
                    self.filepool.append((user, password))
        except Exception as e:
            logging.error("Error in addFromCSV().")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(exc_traceback)
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def addFromBase(self, base="user", num=20):
        logging.debug("addFromBase(): instantiated")
        for i in range(1,num+1):
            self.num_created_frombase += 1
            self.basepool.append(((str(base)+str(self.num_created_frombase),str(base)+str(self.num_created_frombase))))

    def popUser(self, genIfEmpty=True):
        logging.debug("popUser(): instantiated")
        if len(self.filepool) > 0:
            return self.filepool.pop(0)[0]
        else:
            if genIfEmpty == True:
                if len(self.basepool) == 0:
                    self.addFromBase(base="user")
                return self.basepool.pop(0)[0]
            else:
                return None

    def popUserPass(self, genIfEmpty=True):
        logging.debug("popUserPass(): instantiated")
        if len(self.filepool) > 0:
            return self.filepool.pop(0)
        else:
            if genIfEmpty==True:
                if len(self.basepool) == 0:
                    self.addFromBase(base="user")
                return self.basepool.pop(0)
            else:
                return None
    
    def generateUsersConns(self, configname, creds_file="", rolledout_json=None):
        logging.debug("generateUsersConns(): instantiated")
        if rolledout_json == None:
            rolledout_json = self.eco.getExperimentVMRolledOut(configname)
        clonevmjson, numclones = rolledout_json

        if creds_file == "":
            self.addFromBase()
        else:
            self.addFromCSV(creds_file)

        usersConns = {}
        #first create the users for each set of VMs
        createdUsers = {}
        username = ""
        password = ""
        
        for vm in clonevmjson.keys(): 
            vmName = vm
            logging.debug("generateUsersConns(): working with vm: " + str(vmName))
            #get names for clones
            for cloneinfo in clonevmjson[vm]:
                # if vrdpPort exists, then we know it's enabled for this vm; let's set it up
                if "vrdpPort" in cloneinfo:
                    #keep track of users/connections using the groupnum
                    currGroupNum = cloneinfo["groupNum"]
                    vmServerIP = cloneinfo["vm-server-ip"]
                    # rdpBrokerIP = cloneinfo["rdp-broker-ip"]
                    chatServerIP = cloneinfo["chat-server-ip"]
                    challengesServerIP = cloneinfo["challenges-server-ip"]
                    cloneVMName = cloneinfo["name"]
                    vrdpPort = cloneinfo["vrdpPort"]

                    # Create a User if we haven't done so for this group/set and it doesn't exist
                    if createdUsers == {} or currGroupNum not in createdUsers:
                        (username, password) = self.popUserPass()
                        logging.debug( "Generating Username: " + username)
                        createdUsers[currGroupNum] = (username, password)
                        usersConns[(username, password)] = []
                    #otherwise add it to the list known created users
                    else:
                        (username, password) = createdUsers[currGroupNum]
                    # Associate a User and Connection
                    logging.debug( "Generating Username: " + username)
                    usersConns[(username, password)].append((cloneVMName, vmServerIP, vrdpPort))
        logging.debug("generateUsersConns(): Complete...")
        return usersConns