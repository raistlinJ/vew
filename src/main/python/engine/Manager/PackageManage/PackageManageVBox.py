import logging
import sys, traceback
import threading
import json
from engine.Manager.PackageManage.PackageManage import PackageManage
from engine.Manager.VMManage.VBoxManage import VBoxManage
from engine.Manager.VMManage.VBoxManageWin import VBoxManageWin
from engine.Configuration.SystemConfigIO import SystemConfigIO
import time

class PackageManageVBox(PackageManage):
    def __init__(self):
        logging.debug("PackageManageVBox(): instantiated")
        PackageManage.__init__(self)
        #Create an instance of vmManage
        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            self.vmManage = VBoxManage()
        else:
            self.vmManage = VBoxManageWin()
        self.s = SystemConfigIO()

    #abstractmethod
    def importPackage(self, resfilename, runVagrantProvisionScript=False):
        logging.debug("importPackage(): instantiated")
        t = threading.Thread(target=self.runImportPackage, args=(resfilename,))
        t.start()
        return 0
    
    def runImportPackage(self, resfilename, vagrantProvisionScriptfilename=None):
        logging.debug("runImportPackage(): instantiated")
        self.writeStatus = PackageManage.PACKAGE_MANAGE_IMPORTING
        #Unzip the file contents
            
            # get path for temporary directory to hold uncompressed files
            tmpPath = self.s.getConfig()['EXPERIMENTS']['TEMP_DATA_PATH']
            tempPath = os.path.join(os.path.dirname(zipPath), "creatorImportTemp",
                                    os.path.splitext(os.path.basename(zipPath))[0])
            baseTempPath = os.path.join(os.path.dirname(zipPath), "creatorImportTemp")

        #Copy uncompressed file contents into a experiments subfolder

        #For ova files
            #call vmManage to import VMs as specified in config file; wait and query the vmManage status, and then set the complete status

        self.writeStatus = PackageManage.PACKAGE_MANAGE_COMPLETE

    #abstractmethod
    def exportPackage(self, configfilename, exportfilename):
        logging.debug("exportPackage(): instantiated")
        t = threading.Thread(target=self.runImportPackage, args=(configfilename, exportfilename,))
        t.start()
        return 0

    def runExportPackage(self, configfilename, exportfilename):
        logging.debug("runExportPackage(): instantiated")
        self.writeStatus = PackageManage.PACKAGE_MANAGE_EXPORTING

        #For ova files
            #call vmManage to export VMs to ova as specified in config file; wait and query the vmManage status, and then set the complete status

        #Zip the file contents to a .res file
        
        self.writeStatus = PackageManage.PACKAGE_MANAGE_COMPLETE

    #abstractmethod
    def getPackageManageStatus(self):
        logging.debug("getPackageManageStatus(): instantiated")
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus}
    
    #abstractmethod
    def decompressFileContents(self, compressedfilename, destinationdir):
        logging.debug("decompressFileContents(): instantiated")

    #abstractmethod
    def compressFileContents(self, dirtocompress, destinationfilename):
        logging.debug("compressFileContents(): instantiated")