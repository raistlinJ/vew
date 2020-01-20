from PyQt5.QtWidgets import QInputDialog, QWidget, QMessageBox, QFileDialog
from gui.Dialogs.PackageActioningDialog import PackageActioningDialog
import os
import logging

class PackageImportDialog:
    def packageImportDialog(self, parent, existingconfignames):       
        logging.debug("packageImportDialog(): Instantiated")
        self.parent = parent

        fdialog = QFileDialog()
        filenames = ""
        filenames, _ = QFileDialog.getOpenFileNames(fdialog, "Choose RES File to Import", filter="RES Files(*.res)")
        if len(filenames) > 0:
            #check if experiment already exists
            filename = filenames[0]
            logging.debug("packageImportDialog(): files chosen: " + str(filename))
            baseNoExt = os.path.basename(filename)
            baseNoExt = os.path.splitext(baseNoExt)[0]
            self.configname = ''.join(e for e in baseNoExt if e.isalnum())
            #check to make sure the name doesn't already exist
            if self.configname in existingconfignames:
                QMessageBox.warning(self.parent,
                                        "Import Error",
                                        "An experiment with the same name already exists. Skipping...",
                                        QMessageBox.Ok)            
                return []           
            successfilenames = self.importData(filename)
            if len(successfilenames) > 0:
                logging.debug("packageImportDialog(): success files: " + str(successfilenames))
                successfilename = successfilenames[0]
                sbaseNoExt = os.path.basename(successfilename)
                sbaseNoExt = os.path.splitext(sbaseNoExt)[0]
                return sbaseNoExt
        return []

    def importData(self, filenames):
        logging.debug("importData(): instantiated")
        status, successnames = PackageActioningDialog(None, filenames, "import", None).exec_()
        return successnames