import logging
import sys, traceback
import threading
import os
import csv
from engine.Manager.ChallengesManage.ChallengesManage import ChallengesManage
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from engine.Configuration.UserPool import UserPool
from guacapy import Guacamole
from threading import RLock

class ChallengesManageGuacRDP(ChallengesManage):
    def __init__(self):
        logging.debug("ChallengesManageGuacRDP(): instantiated")
        ChallengesManage.__init__(self)
        self.eco = ExperimentConfigIO.getInstance()
        self.usersConnsStatus = {}
        self.lock = RLock()

    #abstractmethod
    def createChallengess(self, configname, guacHostname, username, password, url_path, method, maxChallengess="", maxChallengessPerUser="", width="1400", height="1050", bitdepth="16", creds_file="", itype="", name=""):
        logging.debug("createChallengess(): instantiated")
        t = threading.Thread(target=self.runCreateChallengess, args=(configname, guacHostname, username, password, url_path, method, maxChallengess, maxChallengessPerUser, width, height, bitdepth, creds_file, itype, name))
        t.start()
        return 0

    def runCreateChallengess(self, configname, guacHostname, musername, mpassword,url_path, method, maxChallengess, maxChallengessPerUser, width, height, bitdepth, creds_file, itype, name):
        logging.debug("runCreateChallengess(): instantiated")
        #call guac backend API to make challenges as specified in config file and then set the complete status
        rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
        validchallengesnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)

        userpool = UserPool()
        usersConns = userpool.generateUsersConns(configname, creds_file=creds_file)

        try:
            self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_CREATING
            logging.debug("runCreateChallenges(): guacHostname: " + str(guacHostname) + " username/pass: " + musername + " url_path: " + url_path + " method: " + str(method) + " creds_file: " + creds_file)
            guacConn = Guacamole(guacHostname,username=musername,password=mpassword,url_path=url_path,method=method)
            if guacConn == None:
                logging.error("runCreateChallenges(): Error with guac challenges... skipping: " + str(guacHostname) + " " + str(musername))
                self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE
                return -1
            user_dict = guacConn.get_users()
            try:
                for (username, password) in usersConns:
                    for challenge in usersConns[(username, password)]:
                        cloneVMName = challenge[0]
                        vmServerIP = challenge[1]
                        vrdpPort = challenge[2]
                        #only if this is a specific challenges to create; based on itype and name
                        if cloneVMName in validchallengesnames:
                            #if user doesn't exist, create it
                            if username not in user_dict:
                                logging.debug( "Creating User: " + username)
                                try:
                                    result = self.createUser(guacConn, username, password)
                                    if result == "already_exists":
                                        logging.debug("User already exists; skipping...")
                                    #add to the list of known users
                                    user_dict[username] = ""
                                except Exception:
                                    logging.error("runCreateChallengess(): Error in runCreateChallengess(): when trying to add user.")
                                    exc_type, exc_value, exc_traceback = sys.exc_info()
                                    traceback.print_exception(exc_type, exc_value, exc_traceback)
                            #add the challenges association
                            result = self.createConnAssociation(guacConn, cloneVMName, username, vmServerIP, vrdpPort, maxChallengess, maxChallengessPerUser, width, height, bitdepth)
                            if result == "already_exists":
                                logging.debug("Challenges already exists; skipping...")
            except Exception:
                    logging.error("runCreateChallengess(): Error in runCreateChallengess(): when trying to add challenges.")
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback)
            logging.debug("runCreateChallengess(): Complete...")
            self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE
        except Exception:
            logging.error("runCreateChallengess(): Error in runCreateChallengess(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE

    #abstractmethod
    def clearAllChallengess(self, guacHostname, username, password, url_path, method):
        logging.debug("clearAllChallengess(): instantiated")
        t = threading.Thread(target=self.runClearAllChallengess, args=(guacHostname, username, password, url_path, method))
        t.start()
        return 0

    def runClearAllChallengess(self, guacHostname, username, password, url_path, method):
        self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_REMOVING
        #sample guacConn = Guacamole(192.168.99.102',username='guacadmin',password='guacadmin',url_path='/guacamole',method='http')
        logging.debug("runClearAllChallengess(): guacHostname: " + str(guacHostname) + " username/pass: " + username + " url_path: " + url_path + " method: " + str(method))
        guacConn = Guacamole(guacHostname,username=username,password=password,url_path=url_path,method=method)
        if guacConn == None:
            logging.error("Error with guac challenges... skipping: " + str(guacHostname) + " " + str(username))
            self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE
            return -1

        # Get list of all users
        usernames = guacConn.get_users()
        for username in usernames:
            logging.debug( "Removing Username: " + username)
            try:
                guacConn.delete_user(username)
            except Exception:
                logging.error("runClearAllChallengess(): Error in runClearAllChallengess(): when trying to remove user.")
                exc_type, exc_value, exc_traceback = sys.exc_info()
                #traceback.print_exception(exc_type, exc_value, exc_traceback)
        # Remove All Challengess
        challenges = guacConn.get_challenges()
        logging.debug( "Retrieved Challengess: " + str(challenges))
        if "childChallengess" in challenges:
            for challenges in challenges["childChallengess"]:
                logging.debug( "Removing Challenges: " + str(challenges))
                try:
                    guacConn.delete_challenges(challenges["identifier"])
                except Exception:
                        logging.error("runClearAllChallengess(): Error in runClearAllChallengess(): when trying to remove challenges.")
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        #traceback.print_exception(exc_type, exc_value, exc_traceback)
        self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE

    #abstractmethod
    def removeChallengess(self, configname, guacHostname, username, password, url_path, method, creds_file="", itype="", name=""):
        logging.debug("removeChallengess(): instantiated")
        t = threading.Thread(target=self.runRemoveChallengess, args=(configname,guacHostname, username, password, url_path, method, creds_file, itype, name))
        t.start()
        return 0

    def runRemoveChallengess(self, configname, guacHostname, username, password, url_path, method, creds_file, itype, name):
        self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_REMOVING
        logging.debug("runRemoveChallengess(): instantiated")
        #call guac backend API to make challenges as specified in config file and then set the complete status
        rolledoutjson = self.eco.getExperimentVMRolledOut(configname)
        validchallengesnames = self.eco.getValidVMsFromTypeName(configname, itype, name, rolledoutjson)

        userpool = UserPool()
        try:
            usersConns = userpool.generateUsersConns(configname, creds_file=creds_file)
            self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_CREATING
            logging.debug("runRemoveChallengess(): guacHostname: " + str(guacHostname) + " username/pass: " + username + " url_path: " + url_path + " method: " + str(method) + " creds_file: " + creds_file)
            guacConn = Guacamole(guacHostname,username=username,password=password,url_path=url_path,method=method)
            if guacConn == None:
                logging.error("runRemoveChallengess(): Error with guac challenges... skipping: " + str(guacHostname) + " " + str(username))
                self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE
                return -1

            for (username, password) in usersConns:
                logging.debug( "Removing Challenges for Username: " + username)
                try:
                    for challenge in usersConns[(username, password)]:
                        cloneVMName = challenge[0]
                        if cloneVMName in validchallengesnames:
                            result = self.removeChallengeAssociation(guacConn, cloneVMName)
                            if result == "Does not Exist":
                                logging.debug("Challenges doesn't exists; skipping...")

                    #check if any other challenges exist for user, if not, remove the user too
                    try:
                        result = guacConn.get_permissions(username)
                        if len(result["challengesPermissions"]) == 0:
                            logging.debug( "Removing User: " + username)
                            result = self.removeUser(guacConn, username)
                            if result == "Does not Exist":
                                logging.debug("User doesn't exist; skipping...")
                    except Exception:
                        logging.error("runRemoveChallengess(): Error in runRemoveChallengess(): when trying to remove user.")
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_exception(exc_type, exc_value, exc_traceback)

                except Exception:
                        logging.error("runRemoveChallengess(): Error in runRemoveChallengess(): when trying to remove challenges.")
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_exception(exc_type, exc_value, exc_traceback)
            logging.debug("runRemoveChallengess(): Complete...")
            self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE
        except Exception:
            logging.error("runRemoveChallengess(): Error in runRemoveChallengess(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE
            return
        finally:
            self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE

    #abstractmethod
    def openChallenges(self, configname, experimentid, vmid):
        logging.debug("openChallenges(): instantiated")
        t = threading.Thread(target=self.runRemoveChallengess, args=(configname,))
        t.start()
        return 0

    def runOpenChallenges(self, configname, experimentid, vmid):
        logging.debug("runOpenChallenges(): instantiated")
        self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_OPENING
        #open an RDP session using configuration from systemconfigIO to the specified experimentid/vmid
        self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE

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

    #abstractmethod
    def getChallengesManageStatus(self):
        logging.debug("getChallengesManageStatus(): instantiated")
        #format: {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus, "usersChallengeStatus" : [(username, challengeName): {"user_status": user_perm, "challengeStatus": active}] }
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus, "usersChallengesStatus" : self.usersChallengesStatus}
    
    def getChallengesManageRefresh(self, guacHostname, username, password, url_path, method):
        logging.debug("getChallengesManageStatus(): instantiated")
        self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_REFRESHING
        try:
            self.lock.acquire()
            self.usersConnsStatus.clear()
            guacConn = Guacamole(guacHostname,username=username,password=password,url_path=url_path,method=method)
            #username, challengeName/VMName, userStatus (admin/etc.), challengeStatus (logged in or not)
            users = guacConn.get_users()
            
            challengeIDsNames = {}
            activeConns = {}
            allChallenges = guacConn.get_challenges()
            if 'childChallengess' in allChallenges:
                for challenge in guacConn.get_challenges()['childChallenges']:
                    challengeIDsNames[challenge['identifier']] = challenge['name']
            guac_activeChallenges = guacConn.get_active_challenges()
            for challenge in guac_activeChallenges:
                activeConns[(guac_activeChallenges[challenge]["username"], guac_activeChallenges[challenge]["challengesIdentifier"])] = True

            for user in users:
                #user status first
                perm = guacConn.get_permissions(user)
                user_perm = "not_found"
                if "READ" in perm['userPermissions'][user]:
                    user_perm = "Non-Admin"
                if "ADMINISTER" in perm['userPermissions'][user]:
                    user_perm = "Admin"
                #next, get the list of challenges and the names of those challenges and their status associated with those challenges
                for challengeID in perm['challengesPermissions']:
                    active = "not_active"
                    #if the challenges is in an active state (exists in our activeConns dict), then state it as such
                    if (user, challengeID) in activeConns:
                        active = "active"
                    self.usersConnsStatus[(user, challengeIDsNames[challengeID])] = {"user_status": user_perm, "challengeStatus": active}
            
        except Exception as e:
            logging.error("Error in getChallengesManageStatus(). Did not remove challenges or relation!")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(exc_traceback)
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
        finally:
            self.lock.release()
            self.writeStatus = ChallengesManage.CHALLENGES_MANAGE_COMPLETE

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
                logging.error("getChallengesManageStatus(): Filename: " + filename + " does not exists; returning")
                return None
            with open(filename) as infile:
                reader = csv.reader(infile, delimiter=" ")
                for user, password in reader:
                    i = i+1
                    answer.append((user, password))
            # if len(answer) < num_users:
            #     logging.error("getChallengesManageStatus(): file does not have enough users: " + len(answer) + "; returning")
            #     return None
            return answer
        except Exception as e:
            logging.error("Error in getChallengesManageStatus().")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(exc_traceback)
            #traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
