from posixpath import supports_unicode_filenames
from PyQt5.QtWidgets import QFileDialog, QWidget
from gui.Dialogs.ExperimentDuplicatingDialog import ExperimentDuplicatingDialog
from engine.Configuration.SystemConfigIO import SystemConfigIO
import os
import logging

class ExperimentDuplicateDialog:
    def experimentDuplicateDialog(self, orig_configname, duplicate_configname):
        logging.debug("ExperimentDuplicateDialog(): Instantiated")
        successfilenames = self.duplicateExperiment(orig_configname, duplicate_configname)
        return successfilenames        

    def duplicateExperiment(self, orig_configname, duplicate_configname):
        logging.debug("duplicateExperiment(): instantiated")
        #self.status = {"vmName" : self.vmName, "adaptorSelected" : self.adaptorSelected}
        #get the first value in adaptorSelected (should always be a number)
        status, successfilenames = ExperimentDuplicatingDialog(None, orig_configname, duplicate_configname).exec_()
        return successfilenames