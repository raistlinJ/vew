from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)
import sys, traceback, platform
import logging
import subprocess
import shlex

class ConnectionOpeningThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, pathToBrowser, browserArgs, userpasses, url, method):
        QThread.__init__(self)
        logging.debug("ConnectionOpeningThread(): instantiated")
        self.pathToBrowser = pathToBrowser
        self.browserArgs = browserArgs
        self.userpasses = userpasses
        self.url = url
        self.method = method

    # run method gets called when we start the thread
    def run(self):
        logging.debug("ConnectionOpeningThread(): instantiated")
        stringExec = "Opening with Browser: " + str(self.pathToBrowser)
        self.watchsignal.emit(stringExec, None, None)
        result = []
        try:
            logging.debug("ConnectionOpeningThread(): Starting Connection: " + str(self.pathToBrowser))
            for (username, password) in self.userpasses:
                #cmd = PATH_TO_FIREFOX + " -private-window" + " \"" + baseURL + "/#/?username=" + username + "&password=" + username + "\""
                cmd = "\""+self.pathToBrowser + "\" \"" + self.browserArgs + "\" \"" + self.method + "://" + self.url + "/#/?username=" + username + "&password=" + password + "\""
                stringExec = "Opening Conn: " + str(cmd)
                self.watchsignal.emit(stringExec, None, None)
                logging.debug(stringExec)
                result.append(subprocess.Popen(shlex.split(cmd)))
                logging.debug("ConnectionOpeningThread(): thread ending")
            self.watchsignal.emit("Operation complete.", "success", True)
            return
        except FileNotFoundError:
            logging.error("Error in ConnectionOpeningThread(): File not found")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("File not found.", "failed", True)
            return None
        except:
            logging.error("Error in ConnectionOpeningThread(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("Could not complete operation.", "failed", True)
            return None
        finally:
            return None

class ConnectionOpeningDialog(QDialog):
    def __init__(self, parent, pathToBrowser, browserArgs, userpasses, url, method):
        logging.debug("ConnectionOpeningDialog(): instantiated")
        super(ConnectionOpeningDialog, self).__init__(parent)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.userpasses = userpasses
        self.pathToBrowser = pathToBrowser
        self.browserArgs = browserArgs
        self.url = url
        self.method = method
        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("Connection")
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
        t = ConnectionOpeningThread(self.pathToBrowser, self.browserArgs, self.userpasses, self.url, self.method)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(ConnectionOpeningDialog, self).exec_()
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
