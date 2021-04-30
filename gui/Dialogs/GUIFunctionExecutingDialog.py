from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)
import sys, traceback
from engine.Engine import Engine
import time
from engine.Manager.VMManage.VMManage import VMManage
import logging
import os
import shlex
from subprocess import Popen

class GUIFunctionExecutingThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, msg, funcs):
        QThread.__init__(self)
        self.funcs = funcs
        self.msg = msg

    # run method gets called when we start the thread
    def run(self):
        logging.debug("GUIFunctionExecutingThread(): instantiated")
        numFuncs = len(self.funcs)
        self.watchsignal.emit(self.msg + str(numFuncs), None, False)
        try:
            num = 1
            for ((func, *args)) in self.funcs:
                if numFuncs > 1:
                    self.watchsignal.emit( self.msg + " " + str(num) + " of " + str(numFuncs), None, False)
                else:
                    self.watchsignal.emit( self.msg , None, False)
                logging.debug("run(): running: " + str(func))
                res = func(*args)
                logging.debug("run(): result: " + str(res))
                num = num+1
            logging.debug("run(): Operation Complete, result: " + str(res))    
            self.watchsignal.emit( "Operation Complete", None, True)
            logging.debug("GUIFunctionExecutingThread(): thread ending")
            return
        except FileNotFoundError:
            logging.error("Error in GUIFunctionExecutingThread(): An error occured.")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("Error executing operation.", None, True)
            self.status = -1
        finally:
            return None

class GUIFunctionExecutingDialog(QDialog):
    def __init__(self, parent, msg, funcs):
        logging.debug("GUIFunctionExecutingDialog(): instantiated")
        super(GUIFunctionExecutingDialog, self).__init__(parent)     
        
        self.funcs = funcs
        self.msg = msg
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        
        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("Processing")
        self.setMinimumSize(250, 75)
                       
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
        t = GUIFunctionExecutingThread(self.msg, self.funcs)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(GUIFunctionExecutingDialog, self).exec_()
        logging.debug("exec_(): initiated")
        logging.debug("exec_: self.status: " + str(self.status))
        return self.status
            
    def setStatus(self, msg, status, buttonEnabled):
        if status != None:
            self.status = status
          
        self.statusLabel.setText(msg)

        if buttonEnabled != None:
            logging.debug("buttonEnabled: " + str(buttonEnabled))
            if buttonEnabled == True:
                logging.debug("SO TRUE")
                self.ok_button.setEnabled(True)
                self.hide()
            else:
                self.ok_button.setEnabled(False)

