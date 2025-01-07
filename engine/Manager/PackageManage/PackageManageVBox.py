import logging
import sys, traceback
import threading
import json
from engine.Manager.PackageManage.PackageManage import PackageManage
from engine.Manager.VMManage.VBoxManage import VBoxManage
from engine.Manager.ExperimentManage.ExperimentManageVBox import ExperimentManageVBox
from engine.Manager.VMManage.VBoxManageWin import VBoxManageWin
from engine.Configuration.SystemConfigIO import SystemConfigIO
import zipfile
import os
import shutil
import time

class PackageManageVBox(PackageManage):
    def __init__(self, vmManage, experimentManage):
        logging.debug("PackageManageVBox(): instantiated")
        PackageManage.__init__(self)

        self.vmManage = vmManage
        self.em = experimentManage
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
        try:
            self.writeStatus = PackageManage.PACKAGE_MANAGE_IMPORTING
            #Unzip the file contents
            # get path for temporary directory to hold uncompressed files
            logging.info("runImportPackage(): unzipping contents")
            tmpPathBase = os.path.join(self.s.getConfig()['EXPERIMENTS']['TEMP_DATA_PATH'], "import")
            assumedExperimentName = os.path.basename(resfilename)
            assumedExperimentName = os.path.splitext(assumedExperimentName)[0]
            tmpPathBaseImportedExperiment = os.path.join(tmpPathBase, assumedExperimentName)
            targetPathBase = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], assumedExperimentName)

            self.unzipWorker(resfilename, tmpPathBase)
            logging.info("runImportPackage(): completed unzipping contents")
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
                    logging.debug("runImportPackage(): Importing " + str(vmFilename) + " into VirtualBox...")
                logging.info("Importing VM " + str(vmNum) + " of " + str(len(vmFilenames)))
                #Import the VM using a system call
                self.importVMWorker(os.path.join(tmpPathVMs, vmFilename))
                #since we added a new VM, we have to refresh
                
                self.vmManage.refreshAllVMInfo()
                result = self.vmManage.getManagerStatus()["writeStatus"]
                while result != self.vmManage.MANAGER_IDLE:
                #waiting for manager to finish query...
                    result = self.vmManage.getManagerStatus()["writeStatus"]
                    time.sleep(.1)

                #now take a snapshot
                self.snapshotVMWorker(os.path.join(vmFilename[:-4]))
                vmNum = vmNum + 1

            #move all unzipped files (except ovas) to experiment path)
            #remove experiment from experiment folder if it already exists
            if os.path.exists(tmpPathBaseImportedExperiment) == False:
                logging.error("Experiment folder not found after decompressing files... Skipping: " + str(tmpPathBaseImportedExperiment))
                self.writeStatus = PackageManage.PACKAGE_MANAGE_COMPLETE
                return None
            logging.info("runImportPackage(): copying experiment files to experiment folder: " + str(targetPathBase))
            if os.path.exists(targetPathBase):
                logging.error("Experiment path already exists. Removing and copying anyway..." + str(targetPathBase))
                shutil.rmtree(targetPathBase, ignore_errors=True)
            logging.info("runImportPackage(): copying completed")
            #copy all files to experiment folder
            shutil.copytree(tmpPathBaseImportedExperiment, targetPathBase, ignore=shutil.ignore_patterns("*.ova"))

            #now remove the temporary data folder
            logging.debug("runExportPackage(): removing temporary folder: " + str(tmpPathBaseImportedExperiment))
            if os.path.exists(tmpPathBaseImportedExperiment):
                shutil.rmtree(tmpPathBaseImportedExperiment, ignore_errors=True)
            #double check to see if path was removed or not...
            if os.path.exists(tmpPathBaseImportedExperiment):
                logging.error("runExportPackage(): Could not remove temporary directory: " + str(tmpPathBaseImportedExperiment))

            self.writeStatus = PackageManage.PACKAGE_MANAGE_COMPLETE
        except FileNotFoundError:
            logging.error("Error in runImportPackage(): File not found")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
        except:
            logging.error("Error in runImportPackage(): An error occured")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
        finally:
            self.writeStatus = PackageManage.PACKAGE_MANAGE_COMPLETE
            return None

    def unzipWorker(self, resfilename, tmpOutPath):
        logging.debug("unzipWorker() initiated " + str(resfilename))
        zipPath = resfilename
        block_size = 1048576
        try:
            if os.path.exists(zipPath) == False:
                logging.error("unzipWorker(): path to zip not found... Skipping..." + str(zipPath))
                return

            z = zipfile.ZipFile(zipPath, 'r')
            outputPath = os.path.join(tmpOutPath)
            members_list = z.namelist()

            currmem_num = 0
            for entry_name in members_list:
                if entry_name[-1] == '/':  # if entry is a directory
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
                        logging.info("unzipWorker(): Processing file " + str(currmem_num) + "/" + str(
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
            time.sleep(.1)
            logging.debug("Waiting for import vm to complete...")
            res = self.vmManage.getManagerStatus()
        logging.info("Import complete...")
        logging.debug("importVMWorker(): complete")

    def snapshotVMWorker(self, vmName):
        logging.debug("snapshotVMWorker(): instantiated")
        self.vmManage.snapshotVM(vmName)
        res = self.vmManage.getManagerStatus()
        logging.debug("Waiting for snapshot create to complete...")
        while res["writeStatus"] != self.vmManage.MANAGER_IDLE:
            time.sleep(.1)
            logging.debug("Waiting for snapshot vm to complete...")
            res = self.vmManage.getManagerStatus()
        logging.info("snapshotVMWorker(): complete")

    #abstractmethod
    def exportPackage(self, experimentname, exportpath):
        logging.debug("exportPackage: instantiated")
        t = threading.Thread(target=self.runExportPackage, args=(experimentname, exportpath,))
        t.start()
        return 0

    def runExportPackage(self, experimentname, exportpath):
        logging.debug("runExportPackage(): instantiated")
        try:
            self.writeStatus = PackageManage.PACKAGE_MANAGE_EXPORTING

            #get/create the temp directory to hold all
            experimentDatapath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], experimentname)
            tmpPathBase = os.path.join(self.s.getConfig()['EXPERIMENTS']['TEMP_DATA_PATH'], "export",experimentname)
            tmpPathVMs = os.path.join(tmpPathBase,"VMs")
            tmpPathMaterials = os.path.join(tmpPathBase,"Materials")
            tmpPathExperiments = os.path.join(tmpPathBase,"Experiments")
            exportfilename = os.path.join(exportpath,experimentname+".res")
            
            #copy all files to temp folder
            logging.debug("runExportPackage(): copying experiment files to temporary folder: " + str(tmpPathBase))
            if os.path.exists(tmpPathBase):
                shutil.rmtree(tmpPathBase, ignore_errors=True)
            #have to check again if path was removed or not...
            if os.path.exists(tmpPathBase):
                logging.error("runExportPackage(): Could not remove directory. Cancelling export: " + str(tmpPathBase))
                self.writeStatus = PackageManage.PACKAGE_MANAGE_IDLE
                return

            shutil.copytree(experimentDatapath, tmpPathBase)
            #create any folders that should exist but don't
            if os.path.exists(tmpPathVMs) == False:
                os.makedirs(tmpPathVMs)
            if os.path.exists(tmpPathMaterials) == False:
                os.makedirs(tmpPathMaterials)
            if os.path.exists(tmpPathExperiments) == False:
                os.makedirs(tmpPathExperiments)
                        
            #export vms that are part of this experiment to the temp folder
            vmNames = self.em.getExperimentVMNames(experimentname)
            logging.debug("runExportPackage(): preparing to export experiment vms: " + str(vmNames))
            for vmName in vmNames:
                logging.info("runExportPackage(): exporting: " + str(vmName))
                self.exportVMWorker(vmName, tmpPathVMs)
                logging.info("runExportPackage(): exporting of " + str(vmName) + " complete")

            #add to zip everything that exists in the experiment folder
            logging.info("runExportPackage(): zipping files")
            self.zipWorker(tmpPathBase, exportfilename)
            logging.info("runExportPackage(): completed zipping files")
            #now remove the temporary data folder
            logging.debug("runExportPackage(): removing temporary folder: " + str(tmpPathBase))
            if os.path.exists(tmpPathBase):
                shutil.rmtree(tmpPathBase, ignore_errors=True)
            #double check to see if path was removed or not...
            if os.path.exists(tmpPathBase):
                logging.error("runExportPackage(): Could not remove temporary directory: " + str(tmpPathBase))
            self.writeStatus = PackageManage.PACKAGE_MANAGE_COMPLETE
        except FileNotFoundError:
            logging.error("Error in runExportPackage(): File not found")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
        except:
            logging.error("Error in runExportPackage(): An error occured")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
        finally:
            self.writeStatus = PackageManage.PACKAGE_MANAGE_COMPLETE
            return None

    def zipWorker(self, pathToAdd, zipfilename):
        logging.debug("zipWorker(): instantiated")
        try:
            logging.debug("zipWorker(): checking if destination path exists")
            zipBasePath = os.path.dirname(zipfilename)
            if os.path.exists(zipBasePath) == False:
                logging.debug("zipWorker(): destination path does not exist; attempting to create it: " + str(zipBasePath))
                os.makedirs(zipBasePath)
            if os.path.exists(pathToAdd):
                outZipFile = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_STORED)
                # The root directory within the ZIP file.
                rootdir = os.path.basename(pathToAdd)
                for dirpath, dirnames, filenames in os.walk(pathToAdd):
                    for filename in filenames:
                        # Write the file named filename to the archive,
                        # giving it the archive name 'arcname'.
                        filepath   = os.path.join(dirpath, filename)
                        parentpath = os.path.relpath(filepath, pathToAdd)
                        arcname    = os.path.join(rootdir, parentpath)
                        outZipFile.write(filepath, arcname)
        except FileNotFoundError:
            logging.error("Error in zipWorker(): File not found")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
        except:
            logging.error("Error in zipWorker(): An error occured")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
        finally:
            return None

    def exportVMWorker(self, vmName, filepath):
        logging.debug("exportVMWorker(): instantiated")
        self.vmManage.refreshAllVMInfo()
        logging.debug("Waiting for export to complete...")
        result = self.vmManage.getManagerStatus()["writeStatus"]
        while result != self.vmManage.MANAGER_IDLE:
        #waiting for manager to finish query...
            result = self.vmManage.getManagerStatus()["writeStatus"]
            time.sleep(.1)

        self.vmManage.exportVM(vmName, filepath)
        res = self.vmManage.getManagerStatus()
        logging.debug("Waiting for export to complete...")
        while res["writeStatus"] != self.vmManage.MANAGER_IDLE:
            time.sleep(.1)
            logging.debug("exportVMWorker(): Waiting for export vm to complete...")
            res = self.vmManage.getManagerStatus()
        logging.debug("Export complete...")

    #abstractmethod
    def getPackageManageStatus(self):
        logging.debug("getPackageManageStatus(): instantiated")
        return {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus}

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    resfilename = "samples\\sample.res"

    logging.debug("Instantiating Experiment Config IO")
    p = PackageManageVBox()
    logging.info("Importing file")
    p.importPackage(resfilename)
    logging.info("Operation Complete")