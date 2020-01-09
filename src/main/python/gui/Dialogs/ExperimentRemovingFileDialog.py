from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)
import sys, traceback
import logging
import shutil
import os

class ExperimentRemoveThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, filenames, destinationPath):
        QThread.__init__(self)
        logging.debug("ExperimentRemoveThread(): instantiated")
        
        self.filenames = filenames
        self.destinationPath = destinationPath

    # run method gets called when we start the thread
    def run(self):
        logging.debug("ExperimentRemoveThread(): instantiated")
        stringExec = "Removing experiment from " + str(self.destinationPath)
        self.watchsignal.emit(stringExec, None, None)
        try:
            fullfilename = os.path.join(self.destinationPath,self.filenames)
            logging.debug("ExperimentRemoveThread(): removing file: " + str(fullfilename))
            stringExec = "Removing experiment " + fullfilename
            self.watchsignal.emit( stringExec, None, None)
            if os.path.exists(fullfilename):
                shutil.rmtree(fullfilename, ignore_errors=True)
                self.watchsignal.emit("Finished Removing Experiment", None, True)
            else:
                self.watchsignal.emit("Experiment not found in experiments folder; skipping", None, True)
            logging.debug("ExperimentRemoveThread(): thread ending")
            
            return
        except FileNotFoundError:
            logging.error("Error in ExperimentRemoveThread(): File not found")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
        except Exception:
            logging.error("Error in ExperimentRemoveThread(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

class ExperimentRemovingFileDialog(QDialog):
    def __init__(self, parent, filenames, destinationPath):
        logging.debug("ExperimentRemovingFileDialog(): instantiated")
        super(ExperimentRemovingFileDialog, self).__init__(parent)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
              
        self.filenames = filenames
        self.destinationPath = destinationPath

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("Removing Experiment")
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
        t = ExperimentRemoveThread(self.filenames, self.destinationPath)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(ExperimentRemovingFileDialog, self).exec_()
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
