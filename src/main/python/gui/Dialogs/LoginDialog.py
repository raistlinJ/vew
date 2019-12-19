from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

from gui.Dialogs.LoginConnectingDialog import LoginConnectingDialog
import logging
from engine.Configuration.ConfigurationFile import ConfigurationFile
import os

class LoginDialog(QDialog):
    
    def __init__(self, parent):
        logging.debug("LoginDialog(): instantiated")
        super(LoginDialog, self).__init__(parent)      

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.buttons.addButton( self.buttons.Cancel )

        self.buttons.accepted.connect( self.accept )
        self.buttons.rejected.connect( self.reject )

        self.setWindowTitle("Login Dialog")
        self.setFixedSize(250, 150)
        
        self.cf = ConfigurationFile()
        self.config = self.cf.getConfig()
                
        self.box_main_layout = QGridLayout()
        self.box_main = QWidget()
        self.box_main.setLayout(self.box_main_layout)

        self.label = QLabel("<b>Login to CIT</b>")
        self.box_main_layout.addWidget(self.label, 1,0)

        self.serverIPLabel = QLabel("Server Address")
        self.box_main_layout.addWidget(self.serverIPLabel, 2,0)

        self.serverIPEntry = QLineEdit()
        self.serverIPEntry.setText(self.config['SERVER']['SERVER_IP'])
        self.box_main_layout.addWidget(self.serverIPEntry, 2, 1)

        self.box_username = QWidget()
        self.usernameLabel = QLabel("Username")
        self.box_main_layout.addWidget(self.usernameLabel, 3, 0)

        self.usernameEntry = QLineEdit()
        self.usernameEntry.setText(self.config['SERVER']['USERNAME'])
        self.box_main_layout.addWidget(self.usernameEntry, 3, 1)

        self.passwordLabel = QLabel("Password")
        self.box_main_layout.addWidget(self.passwordLabel, 4, 0)

        self.passwordEntry = QLineEdit()
        self.passwordEntry.setText("")
        self.passwordEntry.setEchoMode(QLineEdit.Password)
                             
        self.box_main_layout.addWidget(self.passwordEntry, 4, 1)
        self.box_main_layout.addWidget(self.buttons, 5,0,1,2)
        
        self.setLayout(self.box_main_layout)
    
    def exec_(self):
        result = super(LoginDialog, self).exec_()
        if str(result) == str(1):        
            logging.debug("dialog_response(): OK was pressed, saving serverIP and username")
            self.cf.writeConfig(self.serverIPEntry.text(), self.usernameEntry.text())
            return (QMessageBox.Ok, self.serverIPEntry.text(), self.usernameEntry.text(), self.passwordEntry.text())
        return (QMessageBox.Cancel, self.serverIPEntry.text(), self.usernameEntry.text(), self.passwordEntry.text())
       
    def clearPass(self):
        logging.debug("clearPass(): instantiated")
        self.passwordEntry.setText("")

    def clearEntries(self):
        logging.debug("clearEntries(): instantiated")
        self.passwordEntry.setText("")
        self.serverIPEntry.setText("")
        self.usernameEntry.setText("")
        self.passwordEntry.setText("")

    def getServerIPText(self):
        logging.debug("getServerIPText(): instantiated")
        return self.serverIPEntry.text()
        
    def getUsernameText(self):
        logging.debug("getUsernameText(): instantiated")
        return self.usernameEntry.text()

    def getPasswordText(self):
        logging.debug("getPasswordText(): instantiated")
        return self.passwordEntry.text()
        
