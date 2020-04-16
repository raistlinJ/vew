from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

import time
import logging
import configparser
from gui.Widgets.VMStartupCmdWidget import VMStartupCmdWidget

class VMStartupCmdsDialog(QDialog):

    def __init__(self, parent, configname, vmName, vmjsondata=None):
        logging.debug("VMStartupCmdsDialog(): instantiated")
        super(VMStartupCmdsDialog, self).__init__(parent)      
        self.parent = parent
        self.setWindowTitle("Startup Commands")
        self.setObjectName("VMStartupCmdWidget")
        self.configname = configname
        self.vmName = vmName

        self.setStyleSheet("QGroupBox { font-weight: bold; }")

        self.startupCommands = {}

        self.setObjectName("VMStartupCmdsDialog")
        self.layoutWidget = QWidget(parent)
        self.layoutWidget.setObjectName("layoutWidget")

        self.outerVertBox = QVBoxLayout()
        self.outerVertBox.setContentsMargins(0, 0, 0, 0)
        self.outerVertBox.setObjectName("outerVertBox")
        
        self.startupCommandsGroupBox = QGroupBox("Startup Commands")       
        self.startupCommandsVertBox = QVBoxLayout()
        self.startupCommandsVertBox.setObjectName("startupCommandsVertBox")
        self.startupCommandsVertBox.setAlignment(Qt.AlignTop)
        self.startupCommandsGroupBox.setLayout(self.startupCommandsVertBox)
        self.outerVertBox.addWidget(self.startupCommandsGroupBox)
        
        self.addStartupCommandButton = QPushButton()
        self.addStartupCommandButton.setObjectName("addStartupCommandButton")
        self.addStartupCommandButton.setText("Add Command")
        self.addStartupCommandButton.clicked.connect(self.buttonAddStartupCommand)
        self.outerVertBox.addWidget(self.addStartupCommandButton, alignment=Qt.AlignHCenter)

        self.setLayout(self.outerVertBox)
        self.retranslateUi(vmjsondata)

    def retranslateUi(self, vmjsondata):
        logging.debug("VMStartupCmdsDialog: retranslateUi(): instantiated")

        if vmjsondata != None and "startup" in vmjsondata and "cmd" in vmjsondata["startup"]:
            startupCmds = {}
            startupcmds = vmjsondata["startup"]["cmd"]
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
        self.startupCommands[startupCmdWidget.removeCommandButton] = startupCmdWidget
    
    def removeStartupCommand(self):
        logging.debug("VMStartupCmdsDialog: removeStartupCommand(): instantiated")
        logging.debug("VMStartupCmdsDialog: sender info: " + str(self.sender()))
        if self.sender() in self.startupCommands:
            widgetToRemove = self.startupCommands[self.sender()]
            logging.debug("commands before: "  + str(self.startupCommands))
            del self.startupCommands[self.sender()]
            logging.debug("commands after: "  + str(self.startupCommands))
            self.startupCommandsVertBox.removeWidget(widgetToRemove)
            widgetToRemove.deleteLater()
            widgetToRemove = None

    def getWritableData(self):
        logging.debug("VMStartupCmdsDialog: getWritableData(): instantiated")
        #build JSON from text entry fields
        logging.debug("VMWidget: getWritableData(): instantiated")
        #build JSON from text entry fields
        jsondata = {}
        jsondata["name"] = {}
        jsondata["name"] = self.nameLineEdit.text()
        jsondata["vrdp-enabled"] = {}
        jsondata["vrdp-enabled"] = self.vrdpEnabledComboBox.currentText()
        jsondata["internalnet-basename"] = [] #may be many
        for netAdaptor in self.netAdaptors.values():
            if isinstance(netAdaptor, NetworkAdaptorWidget):
                jsondata["internalnet-basename"].append(netAdaptor.lineEdit.text())
        return jsondata

        # jsondata = {}
        # jsondata["startup"] = {"cmd": [{}]}
        # jsondata["startup"]["cmd"].append({"seq": 1, 
        #     "hypervisor": "vbox", 
        #     "exec": "run --exe \"/bin/bash\" --username researchdev --password toor --wait-stdout --wait-stderr -- -l -c \"echo toor | sudo -S /usr/bin/find /etc/ | tee /tmp/out.txt | cat && sleep 10 && cat /tmp/out.txt\""
        #     })
        # jsondata["startup"]["cmd"].append({"seq": 2, 
        #     "hypervisor": "vbox", 
        #     "exec": "copyfrom --username researchdev --password toor --verbose --follow -R /tmp/ \"C:\\Users\\Acosta\\Desktop\\tmp\\{{RES_CloneNumber}}\""
        #     })
        return jsondata

    def exec_(self):
        logging.debug("VMStartupCmdsDialog(): exec_() instantiated")
        result = super(VMStartupCmdsDialog, self).exec_()
        if str(result) == str(1):
            logging.debug("dialog_response(): OK was pressed")
                #self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.urlPathLineEdit.text(), self.methodComboBox.currentText(), "1", self.maxConnectionsLineEdit.text(), self.heightLineEdit.text(), self.widthLineEdit.text(), bitDepth]
#use this is we need a "working" dialog cad = ConnectionActioningDialog(self.parent, self.configname, self.actionname, self.args).exec_()
            return (QMessageBox.Ok)
        return (QMessageBox.Cancel)
