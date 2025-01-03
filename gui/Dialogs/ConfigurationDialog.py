from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit, 
        QDial, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox, QFrame, QButtonGroup)

import time
from engine.Configuration.SystemConfigIO import SystemConfigIO
import logging

class ConfigurationDialog(QDialog):

    def __init__(self, parent):
        logging.debug("ConfigurationDialog(): instantiated")
        super(ConfigurationDialog, self).__init__(parent)      
        self.parent = parent
        self.s = SystemConfigIO()
        self.setMinimumWidth(485)

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
        #VirtualBox stuff
        self.virtualboxPathLineEdit = QLineEdit(self.s.getConfig()["VBOX"]["VBOX_PATH"])
        self.layout.addRow(QLabel("VirtualBox Path:"), self.virtualboxPathLineEdit)
        self.vmanagePathLineEdit = QLineEdit(self.s.getConfig()["VBOX"]["VMANAGE_PATH"])
        self.layout.addRow(QLabel("VBoxManage Path:"), self.vmanagePathLineEdit)

        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        self.layout.addRow(separator1)
    
        #VMware stuff
        self.vmwarePathLineEdit = QLineEdit(self.s.getConfig()['VMWARE']['VMWARE_PATH'])
        self.layout.addRow(QLabel("VMware Path:"), self.vmwarePathLineEdit)
        self.vmwareVMPathLineEdit = QLineEdit(self.s.getConfig()['VMWARE']['VMANAGE_VM_PATH'])
        self.layout.addRow(QLabel("VMware VMs Path:"), self.vmwareVMPathLineEdit)
        self.vmwareCliPathLineEdit = QLineEdit(self.s.getConfig()['VMWARE']['VMANAGE_CLI_PATH'])
        self.layout.addRow(QLabel("vmcli Path:"), self.vmwareCliPathLineEdit)
        self.vmwareRunPathLineEdit = QLineEdit(self.s.getConfig()['VMWARE']['VMANAGE_RUN_PATH'])
        self.layout.addRow(QLabel("vmrun Path:"), self.vmwareRunPathLineEdit)
        self.vmwareOVFPathLineEdit = QLineEdit(self.s.getConfig()['VMWARE']['VMANAGE_OVF_PATH'])
        self.layout.addRow(QLabel("OVF Tool Path:"), self.vmwareOVFPathLineEdit)
        self.vmwarePrefsPathLineEdit = QLineEdit(self.s.getConfig()['VMWARE']['VMWARE_PREFSFILE_PATH'])
        self.layout.addRow(QLabel("Preferences File Path:"), self.vmwarePrefsPathLineEdit)
        self.vmwareInvPathLineEdit = QLineEdit(self.s.getConfig()['VMWARE']['VMWARE_INVENTORYFILE_PATH'])
        self.layout.addRow(QLabel("Inventory File Path:"), self.vmwareInvPathLineEdit)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        self.layout.addRow(separator2)

        self.browserPathLineEdit = QLineEdit(self.s.getConfig()['BROWSER']['BROWSER_PATH'])
        self.layout.addRow(QLabel("Browser Path:"), self.browserPathLineEdit)
        
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.HLine)
        separator3.setFrameShadow(QFrame.Sunken)
        self.layout.addRow(separator3)
        
        self.experimentPathLineEdit = QLineEdit(self.s.getConfig()["EXPERIMENTS"]["EXPERIMENTS_PATH"])
        self.layout.addRow(QLabel("Experiments Data Path:"), self.experimentPathLineEdit)
        self.temporaryPathLineEdit = QLineEdit(self.s.getConfig()["EXPERIMENTS"]["TEMP_DATA_PATH"])
        self.layout.addRow(QLabel("Temporary Data Path:"), self.temporaryPathLineEdit)

        self.groupLayout = QHBoxLayout()
        self.vboxRadio = QRadioButton("VirtualBox")
        self.vmwareRadio = QRadioButton("VMware Workstation")
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.addButton(self.vboxRadio)
        self.buttonGroup.addButton(self.vmwareRadio)
        self.groupLayout.addWidget(self.vboxRadio)
        self.groupLayout.addWidget(self.vmwareRadio)
        if self.s.getConfig()["HYPERVISOR"]["ACTIVE"] == "VBOX":
            self.vboxRadio.setChecked(True)
        elif self.s.getConfig()["HYPERVISOR"]["ACTIVE"] == "VMWARE":
            self.vmwareRadio.setChecked(True)
        self.layout.addRow(QLabel("Active Hypervisor (change requires restart):"), self.groupLayout)

        self.formGroupBox.setLayout(self.layout)

    def exec_(self):
        logging.debug("ConfigurationDialog(): exec_() instantiated")
        result = super(ConfigurationDialog, self).exec_()
        if str(result) == str(1):
            logging.debug("dialog_response(): OK was pressed")
            # For each value on the form, write it to the config file
            self.s.writeConfig("VBOX", "VBOX_PATH", self.virtualboxPathLineEdit.text())
            self.s.writeConfig("VBOX", "VMANAGE_PATH", self.vmanagePathLineEdit.text())
            
            self.s.writeConfig("VMWARE", "VMWARE_PATH", self.vmwarePathLineEdit.text())
            self.s.writeConfig("VMWARE", "VMANAGE_VM_PATH", self.vmwareVMPathLineEdit.text())
            self.s.writeConfig("VMWARE", "VMANAGE_CLI_PATH", self.vmwareCliPathLineEdit.text())
            self.s.writeConfig("VMWARE", "VMANAGE_RUN_PATH", self.vmwareRunPathLineEdit.text())
            self.s.writeConfig("VMWARE", "VMANAGE_OVF_PATH", self.vmwareOVFPathLineEdit.text())
            self.s.writeConfig("VMWARE", "VMWARE_PREFSFILE_PATH", self.vmwarePrefsPathLineEdit.text())
            self.s.writeConfig("VMWARE", "VMWARE_INVENTORYFILE_PATH", self.vmwareInvPathLineEdit.text())

            self.s.writeConfig("BROWSER", "BROWSER_PATH", self.browserPathLineEdit.text())
            
            self.s.writeConfig("EXPERIMENTS", "EXPERIMENTS_PATH", self.experimentPathLineEdit.text())
            self.s.writeConfig("EXPERIMENTS", "TEMP_DATA_PATH", self.temporaryPathLineEdit.text())

            if self.vboxRadio.isChecked():
                self.s.writeConfig("HYPERVISOR", "ACTIVE", "VBOX")
            elif self.vmwareRadio.isChecked():
                self.s.writeConfig("HYPERVISOR", "ACTIVE", "VMWARE")

            return (QMessageBox.Ok)
        return (QMessageBox.Cancel)
        