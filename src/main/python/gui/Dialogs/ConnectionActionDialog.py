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
import logging
import configparser

class ConnectionActionDialog(QDialog):

    def __init__(self, parent, configname, actionname):
        logging.debug("ConnectionActionDialog(): instantiated")
        super(ConnectionActionDialog, self).__init__(parent)      
        self.parent = parent
        self.configname = configname
        self.actionname = actionname
        self.cm = ConnectionManage()
        self.setMinimumWidth(275)

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
        self.formGroupBox = QGroupBox("Form layout")
        self.layout = QFormLayout()
        self.hostnameLineEdit = QLineEdit("11.0.0.2:8080")
        self.layout.addRow(QLabel("Hostname:"), self.hostnameLineEdit)
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
        self.heightLineEdit = QLineEdit("1280")
        self.widthLineEdit = QLineEdit("768")
        if self.actionname == "Add":
            #Need to make a function to create more than one user to a single instance 
            # self.layout.addRow(QLabel("Max Connections Per Instance:"), self.maxConnectionsLineEdit)      
            # self.maxConnectionsLineEdit = QLineEdit("1")
            self.layout.addRow(QLabel("Max Connections Per User:"), self.maxConnectionsLineEdit)      
            self.layout.addRow(QLabel("Display Height:"), self.heightLineEdit)
            self.layout.addRow(QLabel("Display Width:"), self.widthLineEdit)

        self.formGroupBox.setLayout(self.layout)

    def exec_(self):
        logging.debug("ConnectionActionDialog(): exec_() instantiated")
        result = super(ConnectionActionDialog, self).exec_()
        if str(result) == str(1):
            logging.debug("dialog_response(): OK was pressed")
            if self.actionname == "Add":
                self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.urlPathLineEdit.text(), self.methodComboBox.currentText(), "1", self.maxConnectionsLineEdit.text(), self.heightLineEdit.text(), self.widthLineEdit.text()]
            else:
                self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.urlPathLineEdit.text(), self.methodComboBox.currentText()]
            cad = ConnectionActioningDialog(self.parent, self.configname, self.actionname, self.args).exec_()
            return (QMessageBox.Ok)
        return (QMessageBox.Cancel)
        