from PyQt5.QtWidgets import QFileDialog, QWidget
import logging

class MaterialFileDialog:
    def materialDialog(self):
        logging.debug("MaterialFileDialog(): Instantiated")
        widget = QFileDialog()
        filenames = ""
        filenames, _ = QFileDialog.getOpenFileNames(widget, "Choose Material", "")
        if len(filenames) > 1:
            return filenames
        elif len(filenames) == 1:
            return [filenames]
        else:
            return []
        logging.debug("MaterialFileDialog(): Completed")