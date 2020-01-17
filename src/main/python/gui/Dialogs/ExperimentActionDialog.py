from PyQt5.QtWidgets import QFileDialog, QWidget
from gui.Dialogs.ExperimentActioningDialog import ExperimentActioningDialog
from engine.Configuration.SystemConfigIO import SystemConfigIO
import os
import logging

class ExperimentActionDialog:
    def ExperimentActionDialog(self, configname, actionname):       
        logging.debug("ExperimentActionDialog(): Instantiated")
        self.configname = configname
        self.s = SystemConfigIO()
        self.destinationPath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'])
        ouputstr = self.experimentAction(actionname)
        logging.debug("ExperimentActionDialog(): Completed")
        return ouputstr

    def experimentAction(self, actionname):
        logging.debug("experimentAction(): instantiated")
        status, outputstr = ExperimentActioningDialog(None, self.configname, actionname).exec_()
        return outputstr