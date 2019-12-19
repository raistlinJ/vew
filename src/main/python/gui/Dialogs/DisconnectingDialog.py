from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

from engine.Engine import Engine
from time import sleep
from engine.Connection.Connection import Connection
import logging

class WatchDisconnThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, connName):
        QThread.__init__(self)
        self.git_url = ""
        self.connName = connName
        
    # run method gets called when we start the thread
    def run(self):
        logging.debug("watchDisconnStatus(): instantiated")
        self.watchsignal.emit("Checking connection", None, None)
        e = Engine.getInstance()
        #will check status every 1 second and will either display stopped or ongoing or connected
        dots = 1
        while(True):
            logging.debug("watchConnStatus(): running: pptp status " + self.connName)
            self.status = e.execute("pptp status " + self.connName)
            logging.debug("watchConnStatus(): result: " + str(self.status))
            if self.status["connStatus"] == Connection.CONNECTING or self.status["disConnStatus"] == Connection.DISCONNECTING or self.status["refreshConnStatus"] == Connection.REFRESHING:
                dotstring = ""
                for i in range(1,dots):
                    dotstring = dotstring + "."
                self.watchsignal.emit( "Disconnecting"+dotstring, self.status, None)
                dots = dots+1
                if dots > 4:
                    dots = 1
            else:
                break
            sleep(0.5)
        logging.debug("watchConnStatus(): thread ending")
        if self.status["connStatus"] == Connection.NOT_CONNECTED:
            self.watchsignal.emit("Disconnected successfully", self.status, True)
        else:
            self.watchsignal.emit("Could not disconnect", self.status, True)
            
class DisconnectingDialog(QDialog):
    def __init__(self, parent, connName):
        logging.debug("DisconnectingDialog(): instantiated")
        super(DisconnectingDialog, self).__init__(parent)     
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        
        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("CIT Connection")
        self.setFixedSize(225, 75)
        
        self.connName = connName

        self.box_main_layout = QGridLayout()
        self.box_main = QWidget()
        self.box_main.setLayout(self.box_main_layout)
       
        self.statusLabel = QLabel("Initializing please wait...")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.box_main_layout.addWidget(self.statusLabel, 1, 0)
        
        self.box_main_layout.addWidget(self.buttons, 2,0)
        
        self.setLayout(self.box_main_layout)
        self.status = -1
        
    def exec_(self):
        t = WatchDisconnThread(self.connName)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(DisconnectingDialog, self).exec_()
        logging.debug("exec_(): initiated")
        logging.debug("exec_: self.status: " + str(self.status))
        return self.status
            
    def setStatus(self, msg, status, buttonEnabled):
        if status != None:
            self.status = status
            
        self.statusLabel.setText(msg)

        if buttonEnabled != None:
            if buttonEnabled == True:
                self.ok_button.setEnabled(True)
            else:
                self.ok_button.setEnabled(False)
        
