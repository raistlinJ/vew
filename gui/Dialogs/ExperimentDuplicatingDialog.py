from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)
from engine.Configuration.SystemConfigIO import SystemConfigIO
import sys, traceback
import logging
import shutil
import os

class ExperimentCopyThread(QThread):
    watchsignal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, orig_configname, duplicate_configname):
        QThread.__init__(self)
        logging.debug("ExperimentCopyThread(): instantiated")
        
        self.orig_configname = orig_configname
        self.duplicate_configname = duplicate_configname
        self.successfilenames = []

    def getFilesInDir(self, path):
        logging.debug('getFilesInDir(): Instantiated')
        full_paths = []
        for apath in os.listdir(path):
            full_path = os.path.join(path, apath)
            if os.path.isfile(full_path):
                full_paths.append(full_path)
        logging.debug('getFilesInDir(): Completed')
        return full_paths

    # run method gets called when we start the thread
    def run(self):
        logging.debug("ExperimentCopyThread(): instantiated")
        stringExec = "Duplicating file to " + str(self.duplicate_configname)
        self.watchsignal.emit(stringExec, None, None)
        try:
            self.s = SystemConfigIO()

            logging.debug("destinationPathStatus(): Getting Experiment Files for " + str(self.orig_configname) + " to " + str(self.duplicate_configname))
            sourceExperimentsPath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], self.orig_configname,"Experiments")
            destinationExperimentsPath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], self.duplicate_configname,"Experiments")
            experimentFiles = self.getFilesInDir(sourceExperimentsPath)

            logging.debug("destinationPathStatus(): Getting Materials Files for " + str(self.orig_configname) + " ")
            sourceMaterialsPath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], self.orig_configname,"Materials")
            destinationMaterialsPath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], self.duplicate_configname,"Materials")
            materialsFiles = self.getFilesInDir(sourceMaterialsPath)
            
            #will check status every 1 second and will either display stopped or ongoing or connected
            numFiles = len(experimentFiles)
            currFileNum = 1
            for filename in experimentFiles:
                logging.debug("ExperimentCopyThread(): copying experiment file: " + str(filename))
                stringExec = "Copying Experiment file (" + str(currFileNum) + "/" + str(numFiles) + ") " + filename
                self.watchsignal.emit( stringExec, None, None)
                dirname = os.path.dirname(filename)
                basename = os.path.basename(filename)
                ext = os.path.splitext(basename)[1]
                #copy old experiment file to new folder with new experiment name
                dupl_exp_filename = os.path.join(destinationExperimentsPath,self.duplicate_configname+str(ext))
                shutil.rmtree(dupl_exp_filename, ignore_errors=True)
                shutil.copy(filename, dupl_exp_filename)
                self.successfilenames.append(filename)

            for filename in materialsFiles:
                logging.debug("ExperimentCopyThread(): copying materials file: " + str(filename))
                stringExec = "Copying Material file (" + str(currFileNum) + "/" + str(numFiles) + ") " + filename
                self.watchsignal.emit( stringExec, None, None)
                shutil.copy(filename, destinationMaterialsPath)
                self.successfilenames.append(filename)

            logging.debug("ExperimentCopyThread(): thread ending")
            self.watchsignal.emit("File Update Complete", None, True)
            return
        except FileNotFoundError:
            logging.error("Error in ExperimentCopyThread(): File not found")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("One or more files were not found and were not added.", None, True)
            return None
        except:
            logging.error("Error in ExperimentCopyThread(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            self.watchsignal.emit("One or more files could not be copied.\r\nFile may be in use or you have invalid permissions.", None, True)
            return None
        finally:
            return None

class ExperimentDuplicatingDialog(QDialog):
    def __init__(self, parent, orig_configname, duplicate_configname):
        logging.debug("ExperimentDuplicatingDialog(): instantiated")
        super(ExperimentDuplicatingDialog, self).__init__(parent)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
              
        self.orig_configname = orig_configname
        self.duplicate_configname = duplicate_configname

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        
        self.buttons.accepted.connect( self.accept )
        self.setWindowTitle("Adding Experiment")
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
        t = ExperimentCopyThread(self.orig_configname, self.duplicate_configname)
        t.watchsignal.connect(self.setStatus)
        t.start()
        result = super(ExperimentDuplicatingDialog, self).exec_()
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
