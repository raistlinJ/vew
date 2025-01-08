from configparser import InterpolationSyntaxError
from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)
from engine.Engine import Engine
from engine.Manager.ExperimentManage.ExperimentManage import ExperimentManage
import sys, traceback
import logging
import shutil
import os
import time

class ExperimentActionThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, configname, actionname, itype, name):
        QThread.__init__(self)
        logging.debug("ExperimentActionThread(): instantiated")

        self.configname = configname
        self.actionname = actionname
        self.itype = itype
        self.name = name
        self.outputstr = []
        self.status = -1

    # run method gets called when we start the thread
    def run(self):
        logging.debug("ExperimentActionThread(): instantiated")
        self.watchsignal.emit("Running " + str(self.actionname) + "...", None, None)
        try:
            e = Engine.getInstance()
            if self.actionname == "Create Experiment":
                e.execute("experiment create " + str(self.configname) + " " + str(self.itype) + " \"" + str(self.name) + "\"")
            elif self.actionname == "Start Experiment":
                e.execute("experiment start " + str(self.configname) + " " + str(self.itype) + " \"" + str(self.name) + "\"")
            elif self.actionname == "Stop Experiment":
                e.execute("experiment stop " + str(self.configname) + " " + str(self.itype) + " \"" + str(self.name) + "\"")
            elif self.actionname == "Suspend Experiment":
                e.execute("experiment suspend " + str(self.configname) + " " + str(self.itype) + " \"" + str(self.name) + "\"")
            elif self.actionname == "Pause Experiment":
                e.execute("experiment pause " + str(self.configname) + " " + str(self.itype) + " \"" + str(self.name) + "\"")
            elif self.actionname == "Snapshot Experiment":
                e.execute("experiment snapshot " + str(self.configname) + " " + str(self.itype) + " \"" + str(self.name) + "\"")
            elif self.actionname == "Restore Experiment":
                e.execute("experiment restore " + str(self.configname) + " " + str(self.itype) + " \"" + str(self.name) + "\"")
            elif self.actionname == "Remove Experiment":
                e.execute("experiment remove " + str(self.configname) + " " + str(self.itype) + " \"" + str(self.name) + "\"")
            elif self.actionname == "Run GuestCmds":
                e.execute("experiment guestcmd " + str(self.configname) + " " + str(self.itype) + " \"" + str(self.name) + "\"")
            elif self.actionname == "Run GuestStored":
                e.execute("experiment gueststored " + str(self.configname) + " " + str(self.itype) + " \"" + str(self.name) + "\"")
            
            #will check status every 0.5 second and will either display stopped or ongoing or connected
            dots = 1
            while(True):
                logging.debug("ExperimentActionThread(): running: experiment status")
                self.status = e.execute("experiment status")
                logging.debug("ExperimentActionThread(): result: " + str(self.status))
                if self.status["writeStatus"] != ExperimentManage.EXPERIMENT_MANAGE_COMPLETE:
                    dotstring = ""
                    for i in range(1,dots):
                        dotstring = dotstring + "."
                    self.watchsignal.emit(" Running " + str(self.actionname) + dotstring, self.status, None)
                    dots = dots+1
                    if dots > 4:
                        dots = 1
                else:
                    break
                time.sleep(0.5)
            logging.debug("WatchRetrieveThread(): thread ending")
            self.watchsignal.emit("Action " + str(self.actionname) + " Complete", self.status, True)
            return
        except:
            logging.error("Error in ExperimentActionThread(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            #self.watchsignal.emit("Error executing action: " + str(self.actionname), None, True)
            self.watchsignal.emit("Error executing action: " + str(exc_value), None, True)
            self.status = -1
            return None
        finally:
            return None

class ExperimentActioningDialog(QDialog):
    def __init__(self, parent, configname, actionname, itype, name):
        logging.debug("ExperimentActioningDialog(): instantiated")
        super(ExperimentActioningDialog, self).__init__(parent)
        self.configname = configname
        self.actionname = actionname
        self.itype = itype
        self.name = name
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("Action")
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
        t = ExperimentActionThread(self.configname, self.actionname, self.itype, self.name)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(ExperimentActioningDialog, self).exec_()
        logging.debug("exec_(): initiated")
        logging.debug("exec_: self.status: " + str(self.status))
        return (self.status, t.outputstr)

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
