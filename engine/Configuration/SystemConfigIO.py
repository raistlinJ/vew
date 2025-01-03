#from PyQt5.QtCore import QStandardPaths
import sys, traceback
import configparser
import os
import logging

class SystemConfigIO():

    def __init__(self):
        logging.debug("SystemConfigIO(): instantiated")
        self.configfilename = "resconfig.ini"
        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            self.configfilename = "resconfig_posix.ini"
        else:
            self.configfilename = "resconfig_win.ini"
        if os.path.exists("config") and os.path.exists(os.path.join("config", self.configfilename)):
            self.path = "config"
            self.filename = os.path.join("config",self.configfilename)
        else:
            self.path = self.writablePath()
            self.filename = os.path.join(self.path,self.configfilename)
        self.config = configparser.ConfigParser()
        self.readConfig()

    def readConfig(self):
        logging.debug("SystemConfigIO: readConfig(): instantiated")
        logging.debug("readConfig(): checking if folder exists: " + self.path)
        try:
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
                    return
            logging.debug("readConfig(): file was NOT found: " + self.filename)

        except Exception:
            logging.error("Error in readConfig(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            self.config['VBOX'] = {}
            self.config['VBOX']['VMANAGE_PATH'] = "VBoxManage"
            self.config['VBOX']['VBOX_PATH'] = "VirtualBox"
            self.config['VMWARE'] = {}
            env_path = os.path.expandvars("/home/$USER/vmware/")
            self.config['VMWARE']['VMANAGE_VM_PATH'] = env_path
            self.config['VMWARE']['VMANAGE_CLI_PATH'] = "vmcli"
            self.config['VMWARE']['VMANAGE_RUN_PATH'] = "vmrun"
            self.config['VMWARE']['VMANAGE_OVF_PATH'] = "ovftool"
            self.config['VMWARE']['VMWARE_PATH'] = "vmware"
            env_path = os.path.expandvars("/home/$USER/.vmware/preferences")
            self.config['VMWARE']['VMWARE_PREFSFILE_PATH'] = env_path
            env_path = os.path.expandvars("/home/$USER/.vmware/inventory.vmls")
            self.config['VMWARE']['VMWARE_INVENTORYFILE_PATH'] = env_path
            self.config['BROWSER'] = {}
            self.config['BROWSER']['BROWSER_PATH'] = "firefox"
            self.config['BROWSER']['ARGS'] = "-private-window"
        else:
            self.config['VBOX'] = {}
            self.config['VBOX']['VMANAGE_PATH'] = "C:\\Program Files\\Oracle\\VirtualBox\\VBoxManage.exe"
            self.config['VBOX']['VBOX_PATH'] = "C:\\Program Files\\Oracle\\VirtualBox\\VirtualBox.exe"
            self.config['VMWARE'] = {}
            env_path = os.path.expandvars("C:\\Users\\$USERNAME\\VMware_VMs\\")
            self.config['VMWARE']['VMANAGE_VM_PATH'] = env_path
            self.config['VMWARE']['VMANAGE_CLI_PATH'] = "C:\\Program Files (x86)\\VMware\\VMware Workstation\\vmcli.exe"
            self.config['VMWARE']['VMANAGE_RUN_PATH'] = "C:\\Program Files (x86)\\VMware\\VMware Workstation\\vmrun.exe"
            self.config['VMWARE']['VMANAGE_OVF_PATH'] = "C:\\Program Files (x86)\\VMware\\VMware Workstation\\OVFTool\\ovftool.exe"
            self.config['VMWARE']['VMWARE_PATH'] = "C:\\Program Files (x86)\\VMware\\VMware Workstation\\vmware.exe"
            env_path = os.path.expandvars("C:\\Documents and Settings\\$USERNAME\\Application Data\\VMWare\\preferences.ini")
            self.config['VMWARE']['VMWARE_PREFSFILE_PATH'] = env_path
            env_path = os.path.expandvars("C:\\Documents and Settings\\$USERNAME\\Application Data\\VMWare\\inventory.vmls")
            self.config['VMWARE']['VMWARE_INVENTORYFILE_PATH'] = env_path
            self.config['BROWSER'] = {}
            self.config['BROWSER']['BROWSER_PATH'] = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
            self.config['BROWSER']['ARGS'] = "-private-window"
        self.config['HYPERVISOR'] = {}
        self.config['HYPERVISOR']['ACTIVE'] = "VMWARE"
        self.config['EXPERIMENTS'] = {}
        self.config['EXPERIMENTS']['EXPERIMENTS_PATH'] = "ExperimentData"
        self.config['EXPERIMENTS']['TEMP_DATA_PATH'] = "tmp"

    def getConfig(self):
        return self.config

    #currently only accepts serverIP and username as saveable to the config file
    def writeConfig(self, key, subkey, value):
        logging.debug("SystemConfigIO: writeConfig(): instantiated")
        #Write any default values here, e.g., 
        #self.config['SERVER']['SERVER_IP'] = serverIP
        #self.config['SERVER']['USERNAME'] = username
        try:
            logging.debug("writeConfig(): making sure keys exist")
            if key in self.config and subkey in self.config[key]:    
                logging.debug("writeConfig(): writing to file: " + self.filename)
                self.config[key][subkey] = value
                with open(self.filename, 'w', encoding="utf-8") as configfile:
                    self.config.write(configfile)
            else:
                logging.error("writeConfig(): Key or subkey do not exist in config" + str(key) + " " + str(subkey))
        except Exception:
            logging.error("Error in writeConfig(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
            
    def writablePath(self, suffix=None):
        logging.debug("SystemConfigIO: writablePath(): instantiated")
        # if hasattr(QStandardPaths, "AppLocalDataLocation"):
        #     p = QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation)
        # else:
        #     # Qt < 5.4
        #     p = QStandardPaths.writableLocation(QStandardPaths.DataLocation)
        p = "config"
        if suffix:
            p = os.path.join(p, suffix)
        if not os.path.exists(p):
            os.makedirs(p)
        return p

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting SystemConfigConfigIO driver")

    #self.readConfig(ConfigurationFile.CONFIG_FILE)