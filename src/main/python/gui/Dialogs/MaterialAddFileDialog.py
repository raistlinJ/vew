from PyQt5.QtWidgets import QFileDialog, QWidget
from gui.Dialogs.MaterialAddingFileDialog import MaterialAddingFileDialog
from engine.Configuration.SystemConfigIO import SystemConfigIO
import os
import logging

class MaterialAddFileDialog:
    def materialAddFileDialog(self, configname):       
        logging.debug("materialAddFileDialog(): Instantiated")
        self.configname = configname
        self.s = SystemConfigIO()
        self.destinationPath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], self.configname,"Materials")
        widget = QFileDialog()
        filenames = ""
        filenames, _ = QFileDialog.getOpenFileNames(widget, "Choose Material", "")
        if len(filenames) > 1:
            self.copyMaterial(filenames)
            return filenames
        elif len(filenames) == 1:
            self.copyMaterial(filenames)
            return filenames
        else:
            return []
        logging.debug("materialAddFileDialog(): Completed")

    def copyMaterial(self, filenames):
        logging.debug("copyMaterial(): instantiated")
        #self.status = {"vmName" : self.vmName, "adaptorSelected" : self.adaptorSelected}
        #get the first value in adaptorSelected (should always be a number)
        
        materialAddingFileDialog = MaterialAddingFileDialog(None, filenames, self.destinationPath).exec_()