from PyQt5.QtWidgets import QInputDialog, QWidget, QMessageBox
from gui.Dialogs.ExperimentAddingFileDialog import ExperimentAddingFileDialog
from engine.Configuration.SystemConfigIO import SystemConfigIO
import os
import logging

class MaterialAddFileDialog:
    def materialAddFileDialog(self, existingconfignames):       
        logging.debug("materialAddFileDialog(): Instantiated")
        self.s = SystemConfigIO()
        self.destinationPath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'])
        self.configname, ok = QInputDialog.getText(self, 'Input Dialog', 
            'Enter your name:')
        if ok:
            #check to make sure the name doesn't already exist
            if self.configname in existingconfignames.keys():
                close = QMessageBox.warning(self,
                                        "Name Exists",
                                        "The experiment name specified already exists",
                                        QMessageBox.Ok)            
                return
        ##Otherwise, create the folders for this and return the name so that it can be added to the main GUI window
        successfilename = addExperiment()
        logging.debug("materialAddFileDialog(): Completed")
        return successfilename

    def addExperiment(self):
        logging.debug("copyMaterial(): instantiated")
        #self.status = {"vmName" : self.vmName, "adaptorSelected" : self.adaptorSelected}
        #get the first value in adaptorSelected (should always be a number)
        status, successfilename = ExperimentAddingDialog(None, self.configname, self.destinationPath).exec_()
        return successfilename