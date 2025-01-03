import logging
import traceback
import sys

from PyQt5.QtWidgets import (QTextEdit)

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        try:
            msg = self.format(record)
            self.widget.append(msg)
        except Exception:
            logging.error("Error in getExperimentXMLFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
