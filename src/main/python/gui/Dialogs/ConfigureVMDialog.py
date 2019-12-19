from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

from engine.Engine import Engine
from time import sleep
from engine.Configuration.ConfigurationFile import ConfigurationFile
from engine.Connection.Connection import Connection
from gui.Dialogs.VMRetrieveDialog import VMRetrieveDialog
from gui.Dialogs.ConfiguringVMDialog import ConfiguringVMDialog
from gui.Widgets.VMTreeWidget import VMTreeWidget
import logging
import configparser

class ConfigureVMDialog(QDialog):
    CONFIG_FILE = "config/config.ini"
    def __init__(self, parent, connection):
        logging.debug("ConfigureVMDialog(): instantiated")
        super(ConfigureVMDialog, self).__init__(parent)      

        self.cf = ConfigurationFile()
        self.serverIntIP = self.cf.getConfig()['SERVER']['INTERNAL_IP']
        self.connName = Connection.NAME
        
        self.connection = connection
        self.vms = {}
        self.vmName = None
        self.adaptorSelected = None
        self.vmStatus = None

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        self.buttons.addButton( self.buttons.Cancel )

        self.buttons.accepted.connect( self.accept )
        self.buttons.rejected.connect( self.reject )

        self.setWindowTitle("Configure Virtual Machine")
        self.setFixedSize(550, 300)

        self.box_main_layout = QGridLayout()
        self.box_main = QWidget()
        self.box_main.setLayout(self.box_main_layout)

        label = QLabel("Select a VM and Adaptor")
        self.box_main_layout.addWidget(label, 1, 0)
        
        self.setLayout(self.box_main_layout)       

#####
        # Here we will place the tree view
        self.treeWidget = VMTreeWidget(self)
        self.treeWidget.cellClicked.connect(self.onItemSelected)
        
        self.box_main_layout.addWidget(self.treeWidget, 1, 0)
        
        s = VMRetrieveDialog(self).exec_()
        self.vms = s["mgrStatus"]["vmstatus"]
        
        if len(self.vms) == 0:
            logging.error("No VMs were retrieved")
            noVMsDialog = QMessageBox.critical(self, "VM Error", "No VMs were found. If you think this is incorrect, please check the path to VBoxManage in config/config.ini and then restart the program.", QMessageBox.Ok)
        self.treeWidget.populateTreeStore(self.vms)
        #self.treeWidget.adjustSize()
        #self.adjustSize()
        
#####
        self.box_main_layout.addWidget(self.buttons, 2, 0)

        self.setLayout(self.box_main_layout)

    def exec_(self):
        result = super(ConfigureVMDialog, self).exec_()
        if str(result) == str(1):        
            logging.debug("dialog_response(): OK was pressed")
            self.configuringVM()
            return (QMessageBox.Ok, self.vmName)
        return (QMessageBox.Cancel, None)

        
    def onItemSelected(self, row, column):
        self.vmStatus = self.treeWidget.item(row,2).text()
        if "Running" in str(self.vmStatus) or "No adaptors enabled" in str(self.vmStatus):
            self.ok_button.setEnabled(False)
            return
        self.vmName = self.treeWidget.item(row,0).text()
        self.adaptorSelected = self.treeWidget.cellWidget(row,1).currentText()
        self.ok_button.setEnabled(True)
            
    def configuringVM(self):
        logging.debug("dialogResponseActionEvent(): OK was pressed: " + str(self.vmName) + " " + str(self.adaptorSelected))
        self.status = {"vmName" : self.vmName, "adaptorSelected" : self.adaptorSelected}
        #get the first value in adaptorSelected (should always be a number)
        adaptorNum = self.adaptorSelected[0]
        octetLocal = self.connection["localIP"].split(".")[3]
        configuringVMDialog = ConfiguringVMDialog(self, self.vmName, self.connection["localIP"], self.serverIntIP, octetLocal, adaptorNum, self.connName).exec_()
        
