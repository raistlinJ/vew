from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

from engine.Engine import Engine
from time import sleep
from engine.VMManage.VMManage import VMManage
from engine.Connection.Connection import Connection
import logging

class ConfigureVMThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, vmName, localIP, remoteIP, octetLocal, adaptorNum, connName ):
        QThread.__init__(self)
        logging.debug("configuringVMThread(): instantiated")
        
        self.vmName = vmName
        self.localIP = localIP
        self.remoteIP = remoteIP
        self.octetLocal = octetLocal
        self.adaptorNum = adaptorNum
        self.connName = connName

    # run method gets called when we start the thread
    def run(self):
        logging.debug("configuringVMThread(): running: vm-manage config " + self.vmName + " " + self.localIP + " " + self.remoteIP + " " + self.octetLocal + " " + self.octetLocal + " " + self.adaptorNum + " " + self.connName)
        self.watchsignal.emit("Configuring VM", None, None)
        e = Engine.getInstance()
        e.execute("vm-manage config " + self.vmName + " " + self.localIP + " " + self.remoteIP + " " + self.octetLocal + " " + self.octetLocal + " " + self.adaptorNum + " " + self.connName)
        #will check status every 1 second and will either display stopped or ongoing or connected
        dots = 1
        while(True):
            self.status = e.execute("vm-manage mgrstatus")
            logging.debug("configureStatus(): result: " + str(self.status))
            if self.status["mgrStatus"]["readStatus"] != VMManage.MANAGER_IDLE or (self.status["mgrStatus"]["writeStatus"] != VMManage.MANAGER_IDLE and self.status["mgrStatus"]["writeStatus"] != VMManage.MANAGER_UNKNOWN):
                dotstring = ""
                for i in range(1,dots):
                    dotstring = dotstring + "."
                self.watchsignal.emit( "Configuring VM"+dotstring, self.status, None)
                dots = dots+1
                if dots > 4:
                    dots = 1
            else:
                break
            sleep(0.5)
        logging.debug("configuringVMThread(): thread ending")
        self.watchsignal.emit("Configuration Complete", self.status, True)
        return

class ConfiguringVMDialog(QDialog):
    def __init__(self, parent, vmName, localIP, remoteIP, octetLocal, adaptorNum, connectionName):
        logging.debug("ConfiguringVMDialog(): instantiated")
        super(ConfiguringVMDialog, self).__init__(parent)     
        ##################
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.vmName = vmName
        self.localIP = localIP
        self.remoteIP = remoteIP
        self.octetLocal = octetLocal
        self.adaptorNum = adaptorNum
        self.connectionName = connectionName

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("Configuring VM")
        self.setFixedSize(225, 75)
                
        self.box_main_layout = QGridLayout()
        self.box_main = QWidget()
        self.box_main.setLayout(self.box_main_layout)
       
        self.statusLabel = QLabel("Initializing please wait")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.box_main_layout.addWidget(self.statusLabel, 1, 0)
        
        self.box_main_layout.addWidget(self.buttons, 2,0)
        
        self.setLayout(self.box_main_layout)
        
        self.status = -1
        
    def exec_(self):
        t = ConfigureVMThread(self.vmName, self.localIP, self.remoteIP, self.octetLocal, self.adaptorNum, self.connectionName)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(ConfiguringVMDialog, self).exec_()
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
        
