from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

from engine.Engine import Engine
import time
from engine.Manager.ConnectionManage.ConnectionManage import ConnectionManage
from gui.Dialogs.ConnectionActioningDialog import ConnectionActioningDialog
from gui.Widgets.FileSelectorWidget import FileSelectorWidget
import logging
import configparser

class ConnectionActionDialog(QDialog):

    def __init__(self, parent, configname, actionname, experimentHostname):
        logging.debug("ConnectionActionDialog(): instantiated")
        super(ConnectionActionDialog, self).__init__(parent)      
        self.parent = parent
        self.configname = configname
        self.actionname = actionname
        self.experimentHostname = experimentHostname
        self.cm = ConnectionManage()
        self.setMinimumWidth(450)

        self.createFormGroupBox()
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        
        self.setWindowTitle(str(actionname) + " Connection")
        
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Connection Information")
        self.layout = QFormLayout()
        self.experimentHostnameLineEdit = QLineEdit(self.experimentHostname)
        self.experimentHostnameLineEdit.setEnabled(False)
        self.layout.addRow(QLabel("Experiment Hostname/IP:"), self.experimentHostnameLineEdit)
        self.hostnameLineEdit = QLineEdit("11.0.0.2:8080")
        self.layout.addRow(QLabel("RDP Broker Hostname/IP:"), self.hostnameLineEdit)
        self.usernameLineEdit = QLineEdit()
        self.layout.addRow(QLabel("Username:"), self.usernameLineEdit)
        self.passwordLineEdit = QLineEdit()
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        self.layout.addRow(QLabel("Password:"), self.passwordLineEdit)
        self.urlPathLineEdit = QLineEdit("/guacamole")
        self.layout.addRow(QLabel("URL Path:"), self.urlPathLineEdit)
        self.methodComboBox = QComboBox()
        self.methodComboBox.addItem("HTTP")
        self.methodComboBox.addItem("HTTPS")
        self.methodComboBox.setCurrentIndex(0)
        self.layout.addRow(QLabel("Method:"), self.methodComboBox)
        
        self.maxConnectionsLineEdit = QLineEdit("1")
        self.heightLineEdit = QLineEdit("1400")
        self.widthLineEdit = QLineEdit("1050")
        self.bitdepthComboBox = QComboBox()
        self.bitdepthComboBox.addItem("256 colors (8-bit)")
        self.bitdepthComboBox.addItem("Low color (16-bit)")
        self.bitdepthComboBox.addItem("True color (24-bit)")
        self.bitdepthComboBox.addItem("True color (32-bit)")
        self.bitdepthComboBox.setCurrentIndex(1)

        self.fileSelectorWidget = FileSelectorWidget()

        if self.actionname == "Add":
            #Need to make a function to create more than one user to a single instance 
            # self.layout.addRow(QLabel("Max Connections Per Instance:"), self.maxConnectionsLineEdit)      
            # self.maxConnectionsLineEdit = QLineEdit("1")
            self.layout.addRow(QLabel("Usernames/Passwords File (csv): "), self.fileSelectorWidget)
            self.layout.addRow(QLabel("Max Connections Per User:"), self.maxConnectionsLineEdit)      
            self.layout.addRow(QLabel("Display Height:"), self.heightLineEdit)
            self.layout.addRow(QLabel("Display Width:"), self.widthLineEdit)
            self.layout.addRow(QLabel("Bit Depth:"), self.bitdepthComboBox)
        if self.actionname == "Remove":
            self.layout.addRow(QLabel("Usernames/Passwords File (csv): "), self.fileSelectorWidget)

        self.formGroupBox.setLayout(self.layout)

    def exec_(self):
        logging.debug("ConnectionActionDialog(): exec_() instantiated")
        result = super(ConnectionActionDialog, self).exec_()
        if str(result) == str(1):
            logging.debug("dialog_response(): OK was pressed")
            if self.actionname == "Add":
                bitDepth = self.bitdepthComboBox.currentText()
                if bitDepth == "256 colors (8-bit)":
                    bitDepth = "8"
                elif bitDepth == "Low color (16-bit)":
                    bitDepth = "16"
                elif bitDepth == "True color (24-bit)":
                    bitDepth = "24"
                elif bitDepth == "True color (32-bit)":
                    bitDepth = "32"
                self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.urlPathLineEdit.text(), self.methodComboBox.currentText(), "1", self.maxConnectionsLineEdit.text(), self.heightLineEdit.text(), self.widthLineEdit.text(), bitDepth, self.fileSelectorWidget.getCredsFilename()]
            elif self.actionname == "Remove":
                self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.urlPathLineEdit.text(), self.methodComboBox.currentText(), self.fileSelectorWidget.getCredsFilename()]
            else:
                self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.urlPathLineEdit.text(), self.methodComboBox.currentText()]

            cad = ConnectionActioningDialog(self.parent, self.configname, self.actionname, self.args).exec_()
            return (QMessageBox.Ok)
        return (QMessageBox.Cancel)
        