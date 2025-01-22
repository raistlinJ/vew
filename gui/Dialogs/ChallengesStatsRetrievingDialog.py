from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)
from engine.Manager.ChallengesManage.ChallengesManage import ChallengesManage
import sys, traceback
from engine.Engine import Engine
import time
import logging

class WatchRetrieveThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, args):
        QThread.__init__(self)
        self.args = args

    # run method gets called when we start the thread
    def run(self):
        logging.debug("WatchRetrieveThread(): instantiated")
        self.watchsignal.emit("Collecting Challenges...", None, None)
        try:
            e = Engine.getInstance()
            logging.debug("watchRetrieveStatus(): running: vm-manage refresh")

            if len(self.args) != 4:
                logging.error("WatchActioningThread(): invalid number of args for create challenges. Skipping...")
                self.watchsignal.emit("Invalid number of args for create challenges. Skipping...", self.status, True)
                self.status = -1
                return None
            #format: "challenges refresh <ip> <user> <pass> <method>"
            cmd = "challenges " + " getstats " + str(self.args[0]) + " " + str(self.args[1]) + " " + str(self.args[2]) + " " + str(self.args[3])

            e.execute(cmd)
            #will check status every 0.5 second and will either display stopped or ongoing or connected
            dots = 1
            while(True):
                logging.debug("watchRetrieveStatus(): running: vm-manage refresh")
                self.status = e.execute("challenges status")
                logging.debug("watchRetrieveStatus(): result: " + str(self.status))
                if self.status["writeStatus"] != ChallengesManage.CHALLENGES_MANAGE_IDLE:
                    dotstring = ""
                    for i in range(1,dots):
                        dotstring = dotstring + "."
                    self.watchsignal.emit( "Reading Challenges Status"+dotstring, self.status, None)
                    dots = dots+1
                    if dots > 4:
                        dots = 1
                else:
                    break
                time.sleep(0.5)
            logging.debug("WatchRetrieveThread(): thread ending")
            self.watchsignal.emit("Retrieval Complete", self.status, True)
            return
        except FileNotFoundError:
            logging.error("Error in ChallengesStatsRetrievingThread(): File not found")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("Error retrieving Challenges. Make sure they exist and that your username/pass is correct.", None, True)
            self.status = -1
            return None
        except:
            logging.error("Error in ChallengesStatsRetrievingThread(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("Error retrieving Challenges. Make sure they exist and that your username/pass is correct.", None, True)
            self.status = -1
            return None
        finally:
            return None

class ChallengesStatsRetrievingDialog(QDialog):
    def __init__(self, parent, args):
        logging.debug("ChallengesStatsRetrievingDialog(): instantiated")
        super(ChallengesStatsRetrievingDialog, self).__init__(parent)     

        self.args = args
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        
        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("Retrieving")
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
        t = WatchRetrieveThread(self.args)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(ChallengesStatsRetrievingDialog, self).exec_()
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
                self.hide()
            else:
                self.ok_button.setEnabled(False)

