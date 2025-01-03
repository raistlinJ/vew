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

class ExperimentAddThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, filename, destinationPath):
        QThread.__init__(self)
        logging.debug("ExperimentAddThread(): instantiated")
        
        self.filename = filename
        self.successfilenames = []
        self.successfoldernames = []
        self.destinationPath = destinationPath
        self.foldersToCreate = []
        self.filesToCreate = []
        ##TODO: create folders files for new then return 
        basePath = os.path.join(destinationPath,filename)
        self.foldersToCreate.append(basePath)
        self.foldersToCreate.append(os.path.join(basePath, "Materials"))
        self.foldersToCreate.append(os.path.join(basePath, "VMs"))
        self.foldersToCreate.append(os.path.join(basePath, "Experiments"))
        self.filesToCreate.append(os.path.join(basePath, "Experiments",filename+str(".xml")))

    # run method gets called when we start the thread
    def run(self):
        logging.debug("ExperimentAddThread(): instantiated")
        stringExec = "Copying file to " + str(self.destinationPath)
        self.watchsignal.emit(stringExec, None, None)
        try:
            logging.debug("ExperimentAddThread(): Creating files and folders for " + str(self.destinationPath) + " " + str(self.filename) )
            
            #will check status every 1 second and will either display stopped or ongoing or connected
            numFolders = len(self.foldersToCreate)
            currFolderNum = 1
            for filename in self.foldersToCreate:
                logging.debug("ExperimentAddThread(): creating folder: " + str(filename))
                stringExec = "Creating folder (" + str(currFolderNum) + "/" + str(numFolders) + ") " + filename
                self.watchsignal.emit( stringExec, None, None)
                os.makedirs(filename)
                self.successfoldernames.append(filename)
            logging.debug("ExperimentAddThread(): thread ending")
            self.watchsignal.emit("Finished Creating Folders", None, False)

            numFiles = len(self.filesToCreate)
            currFileNum = 1
            for filename in self.filesToCreate:
                logging.debug("ExperimentAddThread(): creating file: " + str(filename))
                stringExec = "Creating folder (" + str(currFileNum) + "/" + str(numFiles) + ") " + filename
                self.watchsignal.emit( stringExec, None, None)
                open(filename, "w").close()
                self.successfilenames.append(filename)
            logging.debug("ExperimentAddThread(): thread ending")
            self.watchsignal.emit("Finished Creating Experiment", None, True)

            return
        except FileNotFoundError:
            logging.error("Error in ExperimentAddThread(): File not found")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("One or more file not found.", None, True)
            return None
        except:
            logging.error("Error in ExperimentAddThread(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("One or more file could not be created. Check permissions.", None, True)
            return None
        finally:
            return None

class ExperimentAddingDialog(QDialog):
    def __init__(self, parent, filename, destinationPath):
        logging.debug("ExperimentAddingDialog(): instantiated")
        super(ExperimentAddingDialog, self).__init__(parent)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
              
        self.filename = filename
        self.destinationPath = destinationPath

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("Experiment")
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
        t = ExperimentAddThread(self.filename, self.destinationPath)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(ExperimentAddingDialog, self).exec_()
        logging.debug("exec_(): initiated")
        logging.debug("exec_: self.status: " + str(self.status))
        return (self.status, t.successfoldernames, t.successfilenames)

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
