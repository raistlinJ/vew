from PyQt5.QtCore import QStandardPaths

import configparser
import os
import logging

class SystemConfigIO():

    def __init__(self):
        logging.debug("SystemConfigIO(): instantiated")
        if os.path.exists("config") and os.path.exists(os.path.join("config","resconfig.ini")):
            self.path = "config"
            self.filename = os.path.join("config","resconfig.ini")
        else:
            self.path = self.writablePath()
            self.filename = os.path.join(self.path,"resconfig.ini")
        self.config = configparser.ConfigParser()
        self.readConfig()

    def readConfig(self):
        logging.debug("SystemConfigIO: readConfig(): instantiated")
        logging.debug("readConfig(): checking if folder exists: " + self.path)
        if os.path.exists(self.path):
            logging.debug("readConfig(): folder was found: " + self.path)
            logging.debug("readConfig(): checking if file exists: " + self.filename)
            if os.path.exists(self.filename):
                logging.debug("readConfig(): file was found: " + self.filename)
                self.config.read(self.filename, encoding="utf-8")        
                return
        else:
            try:
                # Create target Directory
                os.mkdir("config")
                logging.debug("readConfig(): directory config created")
            except FileExistsError:
                logging.debug("readConfig(): Directory config already exists")
            
        logging.debug("readConfig(): file was NOT found: " + self.filename)

        self.config['VBOX_WIN'] = {}
        self.config['VBOX_WIN']['VBOX_PATH'] = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
        self.config['VBOX_LINUX'] = {}
        self.config['VBOX_LINUX']['VBOX_PATH'] = "VBoxManage"
        self.config['EXPERIMENTS'] = {}
        self.config['EXPERIMENTS']['EXPERIMENTS_PATH'] = "ExperimentData"

    def getConfig(self):
        return self.config

    #currently only accepts serverIP and username as saveable to the config file
    def writeConfig(self, serverIP, username):
        logging.debug("SystemConfigIO: writeConfig(): instantiated")
        #Write any default values here, e.g., 
        #self.config['SERVER']['SERVER_IP'] = serverIP
        #self.config['SERVER']['USERNAME'] = username
        logging.debug("writeConfig(): writing to file: " + self.filename)
        with open(self.filename, 'w', encoding="utf-8") as configfile:
            self.config.write(configfile)

    def writablePath(self, suffix=None):
        logging.debug("SystemConfigIO: writablePath(): instantiated")
        if hasattr(QStandardPaths, "AppLocalDataLocation"):
            p = QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
        else:
            # Qt < 5.4
            p = QStandardPaths.writableLocation(QStandardPaths.DataLocation)
        if suffix:
            p = os.path.join(p, suffix)
        if not os.path.exists(p):
            os.makedirs(p)
        return p

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting SystemConfigConfigIO driver")

    #self.readConfig(ConfigurationFile.CONFIG_FILE)
