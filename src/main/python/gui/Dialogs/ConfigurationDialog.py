from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

import time
from engine.Configuration.SystemConfigIO import SystemConfigIO
import logging

class ConfigurationDialog(QDialog):

    def __init__(self, parent):
        logging.debug("ConfigurationDialog(): instantiated")
        super(ConfigurationDialog, self).__init__(parent)      
        self.parent = parent
        self.s = SystemConfigIO()
        self.setMinimumWidth(435)

        self.createFormGroupBox()
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        
        self.setWindowTitle("RES Configuration")
        
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Configuration Paths (don't change unless you really know what you're doing)")
        self.layout = QFormLayout()
        self.virtualboxPathLineEdit = QLineEdit(self.s.getConfig()["VBOX"]["VBOX_PATH"])
        self.layout.addRow(QLabel("VirtualBox Path:"), self.virtualboxPathLineEdit)
        self.vmanagePathLineEdit = QLineEdit(self.s.getConfig()["VBOX"]["VMANAGE_PATH"])
        self.layout.addRow(QLabel("VBoxManage Path:"), self.vmanagePathLineEdit)
        self.experimentPathLineEdit = QLineEdit(self.s.getConfig()["EXPERIMENTS"]["EXPERIMENTS_PATH"])
        self.layout.addRow(QLabel("Experiments Data Path:"), self.experimentPathLineEdit)
        self.temporaryPathLineEdit = QLineEdit(self.s.getConfig()["EXPERIMENTS"]["TEMP_DATA_PATH"])
        self.layout.addRow(QLabel("Temporary Data Path:"), self.temporaryPathLineEdit)
        
        self.formGroupBox.setLayout(self.layout)

    def exec_(self):
        logging.debug("ConfigurationDialog(): exec_() instantiated")
        result = super(ConfigurationDialog, self).exec_()
        if str(result) == str(1):
            logging.debug("dialog_response(): OK was pressed")
            # For each value on the form, write it to the config file
            self.s.writeConfig("VBOX", "VBOX_PATH", self.virtualboxPathLineEdit.text())
            self.s.writeConfig("VBOX", "VMANAGE_PATH", self.vmanagePathLineEdit.text())
            self.s.writeConfig("EXPERIMENTS", "EXPERIMENTS_PATH", self.experimentPathLineEdit.text())
            self.s.writeConfig("EXPERIMENTS", "TEMP_DATA_PATH", self.temporaryPathLineEdit.text())
            return (QMessageBox.Ok)
        return (QMessageBox.Cancel)
        