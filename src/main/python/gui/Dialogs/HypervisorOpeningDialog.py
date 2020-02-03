from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)
import sys, traceback
import logging
import subprocess
import os

class HypervisorOpeningThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, pathToHypervisor):
        QThread.__init__(self)
        logging.debug("HypervisorOpeningThread(): instantiated")
        
        self.pathToHypervisor = pathToHypervisor

    # run method gets called when we start the thread
    def run(self):
        logging.debug("HypervisorOpeningThread(): instantiated")
        stringExec = "Starting Hypervisor: " + str(self.pathToHypervisor)
        self.watchsignal.emit(stringExec, None, None)
        try:
            logging.debug("HypervisorOpeningThread(): Starting Hypervisor: " + str(self.pathToHypervisor))
            result = subprocess.Popen(self.pathToHypervisor)
            logging.debug("HypervisorOpeningThread(): thread ending")
            self.watchsignal.emit("Operation complete.", "success", True)
            return
        except FileNotFoundError:
            logging.error("Error in HypervisorOpeningThread(): File not found")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("File not found.", "failed", True)
            return None
        except:
            logging.error("Error in HypervisorOpeningThread(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("Could not complete operation.", "failed", True)
            return None
        finally:
            return None

class HypervisorOpeningDialog(QDialog):
    def __init__(self, parent, pathToHypervisor):
        logging.debug("HypervisorOpeningDialog(): instantiated")
        super(HypervisorOpeningDialog, self).__init__(parent)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
              
        self.pathToHypervisor = pathToHypervisor

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("Hypervisor")
        #self.setFixedSize(225, 75)
                
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
        t = HypervisorOpeningThread(self.pathToHypervisor)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(HypervisorOpeningDialog, self).exec_()
        logging.debug("exec_(): initiated")
        logging.debug("exec_: self.status: " + str(self.status))
        return (self.status)

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
