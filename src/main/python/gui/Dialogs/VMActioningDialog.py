from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

from engine.Engine import Engine
from time import sleep
from engine.VMManage.VMManage import VMManage
import logging

class VMActionThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, vmName, vmAction):
        QThread.__init__(self)
        logging.debug("VMActionThread(): instantiated")
        
        self.vmName = vmName
        self.vmAction = vmAction


    # run method gets called when we start the thread
    def run(self):
        logging.debug("VMActionThread(): instantiated")
        stringExec = "Executing " + self.vmAction #+ " on VM: " + self.vmName
        self.watchsignal.emit(stringExec, None, None)
        e = Engine.getInstance()
        #execute refresh command
        logging.debug("vmActionStatus(): running: vm-manage " + self.vmAction + " " + self.vmName )
        e.execute("vm-manage " + self.vmAction + " " + self.vmName)

        #will check status every 1 second and will either display stopped or ongoing or connected
        dots = 1
        while(True):
            self.status = e.execute("vm-manage mgrstatus")
            logging.debug("vmActionStatus(): result: " + str(self.status))
            if self.status["mgrStatus"]["readStatus"] != VMManage.MANAGER_IDLE or (self.status["mgrStatus"]["writeStatus"] != VMManage.MANAGER_IDLE and self.status["mgrStatus"]["writeStatus"] != VMManage.MANAGER_UNKNOWN):
                dotstring = ""
                for i in range(1,dots):
                    dotstring = dotstring + "."
                self.watchsignal.emit( stringExec+dotstring, self.status, None)
                dots = dots+1
                if dots > 4:
                    dots = 1
            else:
                break
            sleep(0.5)
        logging.debug("VMActionThread(): thread ending")
        self.watchsignal.emit("VM Action Complete", self.status, True)
        return

class VMActioningDialog(QDialog):
    def __init__(self, parent, vmName, vmAction):
        logging.debug("ConfiguringVMDialog(): instantiated")
        super(VMActioningDialog, self).__init__(parent)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
              
        self.vmName = vmName
        self.vmAction = vmAction

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("VM Action")
        self.setFixedSize(225, 75)
                
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
        t = VMActionThread(self.vmName, self.vmAction)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(VMActioningDialog, self).exec_()
        logging.debug("exec_(): initiated")
        logging.debug("exec_: self.status: " + str(self.status))
        return self.status

    def setStatus(self, msg, status, buttonEnabled):
        if status != None:
            self.status = status
            
        self.statusLabel.setText(msg)
        self.statusLabel.adjustSize()
        self.adjustSize()

        if buttonEnabled != None:
            if buttonEnabled == True:
                self.ok_button.setEnabled(True)
            else:
                self.ok_button.setEnabled(False)
