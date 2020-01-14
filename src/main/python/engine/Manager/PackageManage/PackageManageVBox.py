import logging
import sys, traceback
import threading
import json
from engine.Manager.PackageManage.PackageManage import PackageManage
from engine.Manager.VMManage.VBoxManage import VBoxManage
from engine.Manager.VMManage.VBoxManageWin import VBoxManageWin
from engine.Configuration.SystemConfigIO import SystemConfigIO
import zipfile
import os
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
        self.s.readConfig()

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
        logging.debug("runImportPackage(): unzipping contents")
        tmpPathBase = os.path.join(self.s.getConfig()['EXPERIMENTS']['TEMP_DATA_PATH'], "import")
        assumedExperimentName = os.path.basename(resfilename)
        assumedExperimentName = os.path.splitext(assumedExperimentName)[0]
        self.unzipWorker(resfilename, tmpPathBase)
        logging.debug("runImportPackage(): completed unzipping contents")
        tmpPathVMs = os.path.join(tmpPathBase, assumedExperimentName, "VMs")
        #For ova files
            #call vmManage to import VMs as specified in config file; wait and query the vmManage status, and then set the complete status
            # Get all files that end with .ova
            #import and then snapshot
        vmFilenames = []
        if os.path.exists(tmpPathVMs):
            vmFilenames = os.listdir(tmpPathVMs)
        logging.debug("runImportPackage(): Unzipped files: " + str(vmFilenames))
        vmNum = 1
        for vmFilename in vmFilenames:
            if vmFilename.endswith(".ova"):
                logging.debug("importActionEvent(): Importing " + str(vmFilename) + " into VirtualBox...")
            logging.debug("Importing VM " + str(vmNum) + " of " + str(len(vmFilenames)))
            #Import the VM using a system call
            self.importVMWorker(os.path.join(tmpPathVMs, vmFilename))
            self.snapshotVMWorker(os.path.join(vmFilename[:-4]))
            vmNum = vmNum + 1

        self.writeStatus = PackageManage.PACKAGE_MANAGE_COMPLETE

    def unzipWorker(self, resfilename, tmpOutPath):
        logging.debug("unzipWorker() initiated " + str(resfilename))
        zipPath = resfilename
        block_size = 1048576
        try:
            z = zipfile.ZipFile(zipPath, 'r')
            outputPath = os.path.join(tmpOutPath)
            members_list = z.namelist()

            currmem_num = 0
            for entry_name in members_list:
                if entry_name[-1] is '/':  # if entry is a directory
                    continue
                logging.debug("unzipWorker(): unzipping " + str(entry_name))
                # increment our file progress counter
                currmem_num = currmem_num + 1

                entry_info = z.getinfo(entry_name)
                i = z.open(entry_name)
                if not os.path.exists(outputPath):
                    os.makedirs(outputPath)

                filename = os.path.join(outputPath, entry_name)
                file_dirname = os.path.dirname(filename)
                if not os.path.exists(file_dirname):
                    os.makedirs(file_dirname)

                o = open(filename, 'wb')
                offset = 0
                int_val = 0
                while True:
                    b = i.read(block_size)
                    offset += len(b)
                    logging.debug("unzipWorker(): file_size: " +str(float(entry_info.file_size)))
                    logging.debug("unzipWorker(): Offset: " +str(offset))
                    if entry_info.file_size > 0.1:
                        status = float(offset) / float(entry_info.file_size) * 100.
                    else:
                        status = 0
                    logging.debug("unzipWorker(): Status: " +str(status))
                    
                    if int(status) > int_val:
                        int_val = int(status)
                        logging.debug("unzipWorker(): Progress: " +str(float(int_val / 100.)))
                        logging.debug("unzipWorker(): Processing file " + str(currmem_num) + "/" + str(
                            len(members_list)) + ":\r\n" + entry_name + "\r\nExtracting: " + str(int_val) + " %")
                    if b == b'':
                        break
                    #logging.debug("unzipWorker(): Writing out file data for file: " + str(entry_name) + " data: " + str(b))
                    o.write(b)
                logging.debug("unzipWorker(): Finished processing file: " + str(entry_name))
                i.close()
                o.close()
        except FileNotFoundError:
            logging.error("Error in unzipWorker(): File not found: ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        except Exception:
            logging.error("Error in unzipWorker(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)

    def importVMWorker(self, vmFilepath):
        logging.debug("importVMWorker(): instantiated")
        self.vmManage.importVM(vmFilepath)
        res = self.vmManage.getManagerStatus()
        logging.debug("Waiting for import to complete...")
        while res["writeStatus"] != self.vmManage.MANAGER_IDLE:
            time.sleep(1)
            logging.debug("Waiting for import vm to complete...")
            res = self.vmManage.getManagerStatus()
        logging.debug("Import complete...")
        
        logging.debug("Refreshing vmManager...")
        self.vmManage.refreshAllVMInfo()
        res = self.vmManage.getManagerStatus()
        logging.debug("Waiting for refresh vms to complete...")
        while res["readStatus"] != self.vmManage.MANAGER_IDLE:
            time.sleep(1)
            logging.debug("Waiting for refresh vms to complete...")
            res = self.vmManage.getManagerStatus()
        logging.debug("Refresh vmManager complete...")
        logging.debug("importVMWorker(): complete")

    def snapshotVMWorker(self, vmName):
        logging.debug("snapshotVMWorker(): instantiated")
        self.vmManage.snapshotVM(vmName)
        res = self.vmManage.getManagerStatus()
        logging.debug("Waiting for snapshot create to complete...")
        while res["writeStatus"] != self.vmManage.MANAGER_IDLE:
            time.sleep(1)
            logging.debug("Waiting for snapshot vm to complete...")
            res = self.vmManage.getManagerStatus()
        logging.debug("snapshotVMWorker(): complete")

    #abstractmethod
    def exportPackage(self, experimentname, exportpath):
        logging.debug("exportPackage: instantiated")
        t = threading.Thread(target=self.runExportPackage, args=(experimentname, exportpath,))
        t.start()
        return 0

    def runExportPackage(self, experimentname, exportpath):
        logging.debug("runExportPackage(): instantiated")
        self.writeStatus = PackageManage.PACKAGE_MANAGE_EXPORTING

        #get/create the temp directory to hold all
        experimentDatapath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], experimentname)
        tmpPathBase = os.path.join(self.s.getConfig()['EXPERIMENTS']['TEMP_DATA_PATH'], "export",experimentname)
        tmpPathVMs = os.path.join(tmpPathBase,"VMs")
        exportfilename = os.path.join(exportpath,experimentname+".res")
        
        #first add to zip everything that exists in the experiment folder (will add vms later)
        logging.debug("runExportPackage(): zipping non-VM files")
        self.zipWorker(experimentDatapath, exportfilename)
        logging.debug("runExportPackage(): completed zipping non-VM files")

        # for material in self.currentWorkshop.materialList:
        #     shutil.copy2(os.path.join(WORKSHOP_MATERIAL_DIRECTORY, self.currentWorkshop.baseGroupName, material.name),
        #                  materialsPath)

        # vmsToExport = self.currentWorkshop.vmList
        # currVMNum = 0
        # numVMs = len(vmsToExport)
        # for vm in vmsToExport:
        #     # subprocess.call([VBOXMANAGE_DIRECTORY, 'export', vm.name, '-o', os.path.join(folderPath,vm.name+'.ova')])
        #     logging.debug("exportWorkshop(): Exporting VMS loop")
        #     logging.debug("Current VM NAME: " + vm.name)
        #     outputOva = os.path.join(folderPath, vm.name + '.ova')
        #     logging.debug("exportWorkshop(): adjusting dialog progress value to " + str(currVMNum / (numVMs * 1.)))
        #     GLib.idle_add(spinnerDialog.setProgressVal, currVMNum / (numVMs * 1.))
        #     GLib.idle_add(spinnerDialog.setLabelVal, "Exporting VM " + str(currVMNum + 1) + "/" + str(numVMs) + ": " + str(vm.name))
        #     currVMNum = currVMNum + 1
        #     logging.debug("Checking if " + folderPath + " exists: ")
        #     if os.path.exists(folderPath):
        #         pd = ProcessDialog(VBOXMANAGE_DIRECTORY + " export \"" + vm.name + "\" -o \"" + outputOva + "\" --iso", granularity="char", capture="stderr")
        #         pd.run()
        #         #pd.destroy()
        #     else:
        #         logging.error("folderPath" + folderPath + " was not created!")

        self.writeStatus = PackageManage.PACKAGE_MANAGE_COMPLETE

    def zipWorker(self, pathToAdd, zipfilename):
        logging.debug("zipWorker(): instantiated")
        with zipfile.ZipFile(zipfilename, 'w') as zipObj:
            # Iterate over all the files in directory
            logging.debug("zipWorker(): getting files in: " + str(pathToAdd))
            for folderName, subfolders, filenames in os.walk(pathToAdd):
                for filename in filenames:
                    logging.debug("zipWorker(): adding to zip: " + str(filename))
                    #create complete filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    # Add file to zip
                    zipObj.write(filePath)

    def exportVMWorker(self, vmName, filepath):
        logging.debug("exportVMWorker(): instantiated")


    #abstractmethod
    def getPackageManageStatus(self):
        logging.debug("getPackageManageStatus(): instantiated")
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus}

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    resfilename = "samples\sample.res"

    logging.debug("Instantiating Experiment Config IO")
    p = PackageManageVBox()
    logging.info("Importing file")
    p.importPackage(resfilename)
    logging.info("Operation Complete")