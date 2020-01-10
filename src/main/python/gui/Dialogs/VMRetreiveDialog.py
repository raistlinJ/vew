from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

from engine.Engine import Engine
from time import sleep
from engine.Configuration.SystemConfigIO import SystemConfigIO
from gui.Dialogs.VMRetrievingDialog import VMRetrievingDialog
from gui.Widgets.VMTreeWidget import VMTreeWidget
import logging
import configparser

class VMRetrieveDialog(QDialog):

    def __init__(self, parent):
        logging.debug("VMRetrieveDialog(): instantiated")
        super(VMRetrieveDialog, self).__init__(parent)      
        self.parent = parent
        self.s = SystemConfigIO()
        self.vms = {}
        self.vmNames = []

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        self.ok_button.setEnabled(False)
        self.buttons.addButton( self.buttons.Cancel )

        self.buttons.accepted.connect( self.accept )
        self.buttons.rejected.connect( self.reject )

        self.setWindowTitle("Add Virtual Machines")
        #self.setFixedSize(550, 300)

        self.box_main_layout = QGridLayout()
        self.box_main = QWidget()
        self.box_main.setLayout(self.box_main_layout)

        label = QLabel("Select VMs to add")
        self.box_main_layout.addWidget(label, 1, 0)
        
        self.setLayout(self.box_main_layout)       

#####
        # Here we will place the tree view
        self.treeWidget = VMTreeWidget(self)
        self.treeWidget.itemSelectionChanged.connect(self.onItemSelected)
        
        self.box_main_layout.addWidget(self.treeWidget, 1, 0)
        
        s = VMRetrievingDialog(self.parent).exec_()
        self.vms = s["vmstatus"]
        
        if len(self.vms) == 0:
            logging.error("No VMs were retrieved")
            noVMsDialog = QMessageBox.critical(self, "VM Error", "No VMs were found. If you think this is incorrect, please check the path to VBoxManage in config/config.ini and then restart the program.", QMessageBox.Ok)

        #self.treeWidget.setSelectionMode(VMTreeWidget.MultiSelection)
        self.treeWidget.populateTreeStore(self.vms)
        #self.treeWidget.adjustSize()
        #self.adjustSize()
        
#####
        self.box_main_layout.addWidget(self.buttons, 2, 0)

        self.setLayout(self.box_main_layout)

    def exec_(self):
        logging.debug("VMRetrieveDialog(): exec_() instantiated")
        result = super(VMRetrieveDialog, self).exec_()
        if str(result) == str(1):        
            logging.debug("dialog_response(): OK was pressed")
#            self.configuringVM()
            return (QMessageBox.Ok, self.vmNames)
        return (QMessageBox.Cancel, self.vmNames)
        
    def onItemSelected(self):
        logging.debug("VMRetrieveDialog(): onItemSelected() instantiated")
        selectedItems = self.treeWidget.selectedItems()
        logging.debug("VMRetrieveDialog(): onItemSelected() selected items: " + str(selectedItems))

        if len(selectedItems) > 0:
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)
            return
        self.vmNames = []
        for selectedItem in selectedItems:
            self.vmNames.append(selectedItem.text())

                    