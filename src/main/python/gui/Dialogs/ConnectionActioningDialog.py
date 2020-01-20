from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)
import sys, traceback
from engine.Engine import Engine
from time import sleep
from engine.Manager.ConnectionManage.ConnectionManage import ConnectionManage
import logging

class WatchActioningThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, configname, actionname, args):
        QThread.__init__(self)
        self.configname = configname
        self.actionname = actionname
        self.args = args
        self.status = -1

    # run method gets called when we start the thread
    def run(self):
        logging.debug("WatchActioningThread(): instantiated")
        self.watchsignal.emit("Processing Connection " + str(self.actionname) + "...", None, None)
        try:
            e = Engine.getInstance()
            if self.actionname == "Add":
                if len(self.args) != 5:
                    logging.error("WatchActioningThread(): invalid number of args for create connections. Skipping...")
                    self.watchsignal.emit("Invalid number of args for create connections. Skipping...", self.status, True)
                    self.status = -1
                    return None
                cmd = "conns " + " create " + self.configname + " " + str(self.args[0]) + " " + str(self.args[1]) + " " + str(self.args[2]) + " " + str(self.args[3]) + " " + str(self.args[4])
            if self.actionname == "Remove":
                if len(self.args) != 5:
                    logging.error("WatchActioningThread(): invalid number of args for remove connections. Skipping...")
                    self.watchsignal.emit("Invalid number of args for remove connections. Skipping...", self.status, True)
                    self.status = -1
                    return None
                cmd = "conns " + " remove " + self.configname + " " + str(self.args[0]) + " " + str(self.args[1]) + " " + str(self.args[2]) + " " + str(self.args[3]) + " " + str(self.args[4])
            if self.actionname == "Clear":
                if len(self.args) != 5:
                    logging.error("WatchActioningThread(): invalid number of args for clear connections. Skipping...")
                    self.watchsignal.emit("Invalid number of args for clear connections. Skipping...", self.status, True)
                    self.status = -1
                    return None
                cmd = "conns " + " clear " + str(self.args[0]) + " " + str(self.args[1]) + " " + str(self.args[2]) + " " + str(self.args[3]) + " " + str(self.args[4])                
            logging.debug("WatchActioningThread(): running: " + cmd)
            e.execute(cmd)
            #will check status every 0.5 second and will either display stopped or ongoing or connected
            dots = 1
            while(True):
                logging.debug("WatchActioningThread(): running: " + cmd)
                self.status = e.execute("conns status")
                logging.debug("WatchActioningThread(): result: " + str(self.status))
                if self.status["writeStatus"] != ConnectionManage.CONNECTION_MANAGE_COMPLETE:
                    dotstring = ""
                    for i in range(1,dots):
                        dotstring = dotstring + "."
                    self.watchsignal.emit( "Processing " + str(self.actionname) + dotstring, self.status, None)
                    dots = dots+1
                    if dots > 4:
                        dots = 1
                else:
                    break
                sleep(0.5)
            logging.debug("WatchActioningThread(): thread ending")
            self.watchsignal.emit(str(self.actionname) + " Complete", self.status, True)
            return
        except:
            logging.error("Error in WatchActioningThread(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("Error while completing connection action.", None, True)
            self.status = -1
            return None
        finally:
            return None

class ConnectionActioningDialog(QDialog):
    def __init__(self, parent, configname, actionname, args):
        logging.debug("ConnectionActioningDialog(): instantiated")
        super(ConnectionActioningDialog, self).__init__(parent)     
        
        self.configname = configname
        self.actionname = actionname
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
        t = WatchActioningThread(self.configname, self.actionname, self.args)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(ConnectionActioningDialog, self).exec_()
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

