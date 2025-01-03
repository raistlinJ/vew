from PyQt5.QtWidgets import QFileDialog, QWidget
from gui.Dialogs.HypervisorOpeningDialog import HypervisorOpeningDialog
from engine.Configuration.SystemConfigIO import SystemConfigIO
import os
import logging

class HypervisorOpenDialog:
    def hypervisorOpenDialog(self, parent):       
        logging.debug("hypervisorOpenDialog(): Instantiated")
        self.parent = parent
        self.s = SystemConfigIO()
        if self.s.getConfig()["HYPERVISOR"]["ACTIVE"] == 'VMWARE':
            result = self.openHypervisor(self.s.getConfig()["VMWARE"]["VMWARE_PATH"])
        elif self.s.getConfig()["HYPERVISOR"]["ACTIVE"] == 'VBOX':
            result = self.openHypervisor(self.s.getConfig()["VBOX"]["VBOX_PATH"])

        logging.debug("hypervisorOpenDialog(): Completed")
        return result

    def openHypervisor(self, pathToHypervisor):
        logging.debug("openHypervisor(): instantiated")
        result = HypervisorOpeningDialog(self.parent, pathToHypervisor).exec_()
        return result