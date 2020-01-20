from PyQt5.QtWidgets import QInputDialog, QWidget, QMessageBox, QFileDialog
from gui.Dialogs.PackageActioningDialog import PackageActioningDialog
import os
import logging

class PackageExportDialog:
    def packageExportDialog(self, parent, configname):       
        logging.debug("packageImportDialog(): Instantiated")
        self.parent = parent
        self.configname = configname

        fdialog = QFileDialog()
        fdialog.setFileMode(QFileDialog.DirectoryOnly)
        fdialog.setOption(QFileDialog.ShowDirsOnly, True)
        fdialog.setViewMode(QFileDialog.Detail)
        fdialog.setWindowTitle("Choose Export Folder")
        filedir = ""
        if fdialog.exec_() == QFileDialog.Accepted:
            filedirs = fdialog.selectedFiles()
        if len(filedirs) > 0:
            #check to make sure the name doesn't already exist
            filedir = filedirs[0]
            filename = os.path.join(filedir)
            successfile = self.exportData(filename)
            if len(successfile) > 0:
                logging.debug("packageExportDialog(): returning: " + str(successfile))
                return successfile
        return []

    def exportData(self, foldername):
        logging.debug("exportData(): instantiated")
        status, successnames = PackageActioningDialog(None, foldername, "export", [self.configname]).exec_()
        return successnames