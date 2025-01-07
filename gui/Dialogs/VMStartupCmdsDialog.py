from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox, QScrollArea)

import time
import logging
import configparser
from gui.Widgets.VMStartupCmdWidget import VMStartupCmdWidget

class VMStartupCmdsDialog(QDialog):

    def __init__(self, parent, configname, vmName, startupjsondata=None):
        logging.debug("VMStartupCmdsDialog(): instantiated")
        super(VMStartupCmdsDialog, self).__init__(parent)      
        self.parent = parent
        self.setWindowTitle("Startup Commands")
        self.setObjectName("VMStartupCmdWidget")
        self.configname = configname
        self.vmName = vmName
        self.setMinimumSize(600, 600)

        #self.setStyleSheet("QGroupBox { font-weight: normal; }")

        self.startupCommandsWidgets = {}

        self.setObjectName("VMStartupCmdsDialog")
        self.layoutWidget = QWidget(parent)
        self.layoutWidget.setObjectName("layoutWidget")

        self.outerVertBox = QVBoxLayout()
        #self.outerVertBox.setContentsMargins(0, 0, 0, 0)
        self.outerVertBox.setObjectName("outerVertBox")
        
        self.startupCommandsGroupBox = QGroupBox("Commands for " + vmName + " (correct Guest Additions/VMware Tools required)")
        self.startupCommandsVertBox = QVBoxLayout()
        self.startupCommandsVertBox.setObjectName("startupCommandsVertBox")
        self.startupCommandsVertBox.setAlignment(Qt.AlignTop)
        self.startupCommandsGroupBox.setLayout(self.startupCommandsVertBox)

        self.startupDelayHBox = QHBoxLayout()
        self.startupDelayHBox.setObjectName("startupDelayHBox")
        self.startupDelayHBox.setAlignment(Qt.AlignLeft)
        self.delayLabel = QLabel("Startup Commands Delay (in seconds)")
        self.startupDelayHBox.addWidget(self.delayLabel)
        self.delaySpinBox = QSpinBox()
        self.delaySpinBox.setObjectName("delaySpinBox")
        self.delaySpinBox.setRange(0, 9999)
        self.startupDelayHBox.addWidget(self.delaySpinBox)
        self.startupCommandsVertBox.addLayout(self.startupDelayHBox)

        self.commandsScrollArea = QScrollArea()
        self.commandsScrollArea.setWidget(self.startupCommandsGroupBox)
        self.commandsScrollArea.setWidgetResizable(True)
        self.outerVertBox.addWidget(self.commandsScrollArea)

        self.addStartupCommandButton = QPushButton()
        self.addStartupCommandButton.setObjectName("addStartupCommandButton")
        self.addStartupCommandButton.setText("Add Command")
        self.addStartupCommandButton.clicked.connect(self.buttonAddStartupCommand)
        self.outerVertBox.addWidget(self.addStartupCommandButton, alignment=Qt.AlignHCenter)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.outerVertBox.addWidget(self.buttonBox, alignment=Qt.AlignHCenter)

        self.setLayout(self.outerVertBox)
        self.retranslateUi(startupjsondata)

    def retranslateUi(self, startupjsondata):
        logging.debug("VMStartupCmdsDialog: retranslateUi(): instantiated")

        if startupjsondata != None and "cmd" in startupjsondata:
            startupdelay = 0
            if "delay" in startupjsondata:
                startupdelay = startupjsondata["delay"]
            print("STARTUP-DELAY: " + str(startupdelay))
            self.delaySpinBox.setValue(int(startupdelay))
            startupcmds = startupjsondata["cmd"]
            #if this is not a list, make it one (xml to json limitation)
            if isinstance(startupcmds, list) == False:
                startupcmds = [startupcmds]
            #iterate through each startup command
            for cmdjson in startupcmds:
                #if exec does not exist, just quit; can't do anything without it
                if "exec" not in cmdjson:
                    logging.error("getExperimentVMRolledOut(): exec tag missing: " + str(cmdjson))
                    continue
                self.addStartupCommand(cmdjson)
        else:
            vmjsondata = {}

    def buttonAddStartupCommand(self):
        logging.debug("VMStartupCmdsDialog: buttonAddStartupCommand(): instantiated")
        self.addStartupCommand(cmdjson=None)

    def addStartupCommand(self, cmdjson):
        logging.debug("VMStartupCmdsDialog: addStartupCommand(): instantiated")
        #set default hypervisor and seq if they aren't specified        
        ##create a widget for each entry
        startupCmdWidget = VMStartupCmdWidget(self.parent, cmdjson)
        self.startupCommandsVertBox.addWidget(startupCmdWidget)

        #need to keep track for easy removal later
        startupCmdWidget.removeCommandButton.clicked.connect(self.removeStartupCommand)
        self.startupCommandsWidgets[startupCmdWidget.removeCommandButton] = startupCmdWidget
    
    def removeStartupCommand(self):
        logging.debug("VMStartupCmdsDialog: removeStartupCommand(): instantiated")
        logging.debug("VMStartupCmdsDialog: sender info: " + str(self.sender()))
        if self.sender() in self.startupCommandsWidgets:
            widgetToRemove = self.startupCommandsWidgets[self.sender()]
            logging.debug("commands before: "  + str(self.startupCommandsWidgets))
            del self.startupCommandsWidgets[self.sender()]
            logging.debug("commands after: "  + str(self.startupCommandsWidgets))
            self.startupCommandsVertBox.removeWidget(widgetToRemove)
            widgetToRemove.deleteLater()
            widgetToRemove = None

    def getWritableData(self):
        logging.debug("VMStartupCmdsDialog: getWritableData(): instantiated")
        jsondata = {}
        if len(self.startupCommandsWidgets) > 0:
            jsondata = {"cmd": [], "delay": str(self.delaySpinBox.value())}
            for startupcmdwidget in self.startupCommandsWidgets.values():
                jsondata["cmd"].append(startupcmdwidget.getWritableData())
        return jsondata

    def exec_(self):
        logging.debug("VMStartupCmdsDialog(): exec_() instantiated")
        result = super(VMStartupCmdsDialog, self).exec_()
        if str(result) == str(1):
            logging.debug("dialog_response(): OK was pressed")
            return QMessageBox.Ok, self.getWritableData()
        return QMessageBox.Cancel, None
