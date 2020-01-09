from PyQt5.QtWidgets import QFileDialog, QWidget
from gui.Dialogs.ExperimentRemovingFileDialog import ExperimentRemovingFileDialog
from engine.Configuration.SystemConfigIO import SystemConfigIO
import os
import logging

class ExperimentRemoveFileDialog:
    def experimentRemoveFileDialog(self, configname):       
        logging.debug("experimentRemoveFileDialog(): Instantiated")
        self.configname = configname
        self.s = SystemConfigIO()
        self.destinationPath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'])
        self.removeExperiment()
        logging.debug("experimentRemoveFileDialog(): Completed")

    def removeExperiment(self):
        logging.debug("removeExperiment(): instantiated")
        experimentRemovingFileDialog = ExperimentRemovingFileDialog(None, self.configname, self.destinationPath).exec_()