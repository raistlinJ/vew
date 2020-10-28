from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget, QLineEdit, QPushButton
import logging

class FileSelectorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logging.debug("FileSelectorWidget instantiated")
        QtWidgets.QWidget.__init__(self, parent=None)
        
        self.outerHBox = QtWidgets.QHBoxLayout()
        self.outerHBox.setContentsMargins(0, 0, 0, 0)
        self.outerHBox.setObjectName("outerVertBox")
        self.credsFileLineEdit = QLineEdit()
        self.credsFileLineEdit.setPlaceholderText("Leave blank to use default: user<id>")
        self.outerHBox.addWidget(self.credsFileLineEdit)
        self.selectFileButton = QPushButton("...")
        self.selectFileButton.setMaximumSize(30, 30)
        self.selectFileButton.clicked.connect(self.open_file_dialog)
        self.outerHBox.addWidget(self.selectFileButton)
        self.setLayout(self.outerHBox)

    def open_file_dialog(self):
        logging.debug('open_file_dialog(): Instantiated')
        widget = QFileDialog()
        filename, _ = QFileDialog.getOpenFileName(widget, "Choose a credentials file", "", "CREDS Files (*.csv)")

        if filename:
            logging.debug("open_file_dialog(): selected file: "  + str(filename))
            self.credsFileLineEdit.setText(filename)
        else:
            logging.debug("open_file_dialog(): cancelled")
        logging.debug('open_file_dialog(): Completed')
    
    def getCredsFilename(self):
        logging.debug('getCredsFilename(): Instantiated')
        filename = self.credsFileLineEdit.text()
        if filename != None and isinstance(filename, str) and filename.strip() != "":
            logging.debug('getCredsFilename(): returning: ' + str(filename))
            return filename
        else:
            logging.debug('getCredsFilename(): blank')
            return ""