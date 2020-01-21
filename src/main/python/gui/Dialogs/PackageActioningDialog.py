from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)
from engine.Manager.PackageManage.PackageManage import PackageManage
from engine.Engine import Engine
import sys, traceback
import time
import logging
import shutil
import os

class PackageActioningThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, filenames, actionname, args):
        QThread.__init__(self)
        logging.debug("PackageActioningThread(): instantiated")
        
        self.filenames = filenames
        self.actionname = actionname
        self.args = args
        self.successfilenames = []

    # run method gets called when we start the thread
    def run(self):
        logging.debug("PackageActioningThread(): instantiated")
        stringExec = "Processing " + str(self.actionname)
        self.watchsignal.emit(stringExec, None, None)
        try:
            logging.debug("PackageActioningThread(): Processing for " + str(self.filenames) + " " + str(self.actionname) )
            e = Engine.getInstance()
            if self.actionname == "import":
                e.execute("packager import " + str(self.filenames))
            elif self.actionname == "export":
                e.execute("packager export " + self.args[0] + " " + str(self.filenames))
            #will check status every 0.5 second and will either display stopped or ongoing or connected
            dots = 1
            while(True):
                logging.debug("PackageActioningThread(): running: package status")
                self.status = e.execute("packager status")
                logging.debug("PackageActioningThread(): result: " + str(self.status))
                if self.status["writeStatus"] != PackageManage.PACKAGE_MANAGE_COMPLETE:
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
            self.successfilenames.append(self.filenames)
            logging.debug("PackageActioningThread(): thread ending")
            self.watchsignal.emit("Action " + str(self.actionname) + " Complete", self.status, True)
            return
        except:
            logging.error("Error in PackageActioningThread(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            #self.watchsignal.emit("Error executing action: " + str(self.actionname), None, True)
            self.watchsignal.emit("Error executing action: " + str(exc_value), None, True)
            self.status = -1
            return None
        finally:
            return None

class PackageActioningDialog(QDialog):
    def __init__(self, parent, filename, actionname, args):
        logging.debug("PackageActioningDialog(): instantiated")
        super(PackageActioningDialog, self).__init__(parent)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
              
        self.filename = filename
        self.actionname = actionname
        self.args = args

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("Packager")
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
        t = PackageActioningThread(self.filename, self.actionname, self.args)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(PackageActioningDialog, self).exec_()
        logging.debug("exec_(): initiated")
        logging.debug("exec_: self.status: " + str(self.status))
        return (self.status, t.successfilenames)

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
