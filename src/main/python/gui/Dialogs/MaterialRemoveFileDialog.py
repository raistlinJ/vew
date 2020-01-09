from PyQt5.QtWidgets import QFileDialog, QWidget
from gui.Dialogs.MaterialRemovingFileDialog import MaterialRemovingFileDialog
from engine.Configuration.SystemConfigIO import SystemConfigIO
import os
import logging

class MaterialRemoveFileDialog:
    def materialRemoveFileDialog(self, configname, materialname):       
        logging.debug("materialRemoveFileDialog(): Instantiated")
        self.configname = configname
        self.materialname = materialname
        self.s = SystemConfigIO()
        self.destinationPath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], self.configname,"Materials")
        self.removeMaterial(materialname)
        logging.debug("materialRemoveFileDialog(): Completed")

    def removeMaterial(self, materialname):
        logging.debug("removeMaterial(): instantiated")
        materialRemovingFileDialog = MaterialRemovingFileDialog(None, materialname, self.destinationPath).exec_()