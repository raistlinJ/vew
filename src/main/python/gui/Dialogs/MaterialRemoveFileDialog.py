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
        successfilenames = self.removeMaterial(materialname)
        logging.debug("materialRemoveFileDialog(): Completed")
        return successfilenames

    def removeMaterial(self, materialname):
        logging.debug("removeMaterial(): instantiated")
        (status, successfilenames) = MaterialRemovingFileDialog(None, materialname, self.destinationPath).exec_()
        return successfilenames
        