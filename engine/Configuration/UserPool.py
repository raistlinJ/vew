import logging
import os
import sys, traceback
import csv

class UserPool():
    def __init__(self):
        logging.debug("UserPool(): instantiated")
        self.filepool = []
        self.basepool = []
        self.num_created_fromfile = 0
        self.num_created_frombase = 0

    def addFromCSV(self, csvfilename, remove_invalid_chars=True):
        logging.debug("addFromCSV(): instantiated")
        #quick lazy way to generate the users/passes from csv:
        i = 0
        try:
            if os.path.exists(csvfilename) == False:
                logging.error("getConnectionManageStatus(): Filename: " + csvfilename + " does not exists; returning")
                return None
            with open(csvfilename) as infile:
                reader = csv.reader(infile, delimiter=" ")
                for user, password in reader:
                    i = i+1
                    if remove_invalid_chars:
                        user = ''.join(e for e in user if e.isalnum())
                    self.filepool.append((user, password))
        except Exception as e:
            logging.error("Error in getConnectionManageStatus().")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(exc_traceback)
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def addFromBase(self, base="user", num=20):
        logging.debug("createUserPassPoolFromCSV(): instantiated")
        for i in range(1,num+1):
            self.basepool.append(((str(base)+str(i),str(base)+str(i))))

    def popUser(self, genIfEmpty=True):
        logging.debug("popUser(): instantiated")
        if len(self.filepool) > 0:
            self.num_created_fromfile += 1
            return self.filepool.pop(0)[0]
        else:
            if genIfEmpty == True:
                if len(self.basepool) == 0:
                    self.addFromBase(base="extra_")
                self.num_created_frombase += 1
                return self.basepool.pop(0)[0]
            else:
                return None

    def popUserPass(self, genIfEmpty=True):
        logging.debug("popUserPass(): instantiated")
        if len(self.filepool) > 0:
            self.num_created_fromfile += 1
            return self.filepool.pop(0)
        else:
            if genIfEmpty==True:
                if len(self.basepool) == 0:
                    self.addFromBase(base="extra_")
                self.num_created_frombase += 1
                return self.basepool.pop(0)
            else:
                return None
    
