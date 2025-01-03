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

class WatchRetrieveThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self):
        QThread.__init__(self)

    # run method gets called when we start the thread
    def run(self):
        logging.debug("WatchRetrieveThread(): instantiated")
        self.watchsignal.emit("Querying Hypervisor...", None, None)
        try:
            e = Engine.getInstance()
            logging.debug("watchRetrieveStatus(): running: vm-manage refresh")
            e.execute("vm-manage refresh")
            #will check status every 0.5 second and will either display stopped or ongoing or connected
            dots = 1
            while(True):
                logging.debug("watchRetrieveStatus(): running: vm-manage refresh")
                self.status = e.execute("vm-manage mgrstatus")
                logging.debug("watchRetrieveStatus(): result: " + str(self.status))
                if self.status["writeStatus"] != VMManage.MANAGER_IDLE:
                    dotstring = ""
                    for i in range(1,dots):
                        dotstring = dotstring + "."
                    self.watchsignal.emit( "Reading VM Status"+dotstring, self.status, None)
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
            logging.error("Error in ExperimentRemoveThread(): File not found")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("Error retrieving VMs. Check your paths and permissions.", None, True)
            self.status = -1
            return None
        except:
            logging.error("Error in ExperimentRemoveThread(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("Error retrieving VMs. Check your paths and permissions.", None, True)
            self.status = -1
            return None
        finally:
            return None

class VMRetrievingDialog(QDialog):
    def __init__(self, parent):
        logging.debug("VMRetrievingDialog(): instantiated")
        super(VMRetrievingDialog, self).__init__(parent)     
        
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
        t = WatchRetrieveThread()
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(VMRetrievingDialog, self).exec_()
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

