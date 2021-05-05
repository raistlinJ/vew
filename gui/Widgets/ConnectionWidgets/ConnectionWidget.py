from gui.Dialogs.ConnectionActionDialog import ConnectionActionDialog
from gui.Dialogs.ConnectionActioningDialog import ConnectionActioningDialog
from gui.Dialogs.GUIFunctionExecutingDialog import GUIFunctionExecutingDialog
from gui.Dialogs.ConnectionRetrievingDialog import ConnectionRetrievingDialog
from PyQt5 import QtCore, QtGui, QtWidgets
import logging
from gui.Dialogs.ExperimentActionDialog import ExperimentActionDialog
from gui.Widgets.ConnectionWidgets.ConnectionStatusWidget import ConnectionStatusWidget
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from engine.Configuration.UserPool import UserPool
from PyQt5.QtWidgets import (QApplication, qApp, QAction, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QMessageBox, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QStackedWidget, QStatusBar, QMenuBar)
from gui.Helpers.ConnectionActions import ConnectionActions
import os

class ConnectionWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, statusBar=None):
        logging.debug("ConnectionWidget instantiated")
        QtWidgets.QWidget.__init__(self, parent=None)
        self.statusBar = statusBar
        self.experimentItemNames = {}
        self.connectionBaseWidgets = {}
        self.eco = ExperimentConfigIO.getInstance()

        self.setObjectName("ConnectionWidget")

        self.windowWidget = QtWidgets.QWidget()
        self.windowWidget.setObjectName("windowWidget")
        self.windowBoxHLayout = QtWidgets.QHBoxLayout()
        #self.windowBoxHLayout.setContentsMargins(0, 0, 0, 0)
        self.windowBoxHLayout.setObjectName("windowBoxHLayout")
        self.windowWidget.setLayout(self.windowBoxHLayout)

        self.experimentTree = QtWidgets.QTreeWidget(parent)
        self.experimentTree.setObjectName("experimentTree")    
        self.experimentTree.header().resizeSection(0, 150)
        self.experimentTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.experimentTree.customContextMenuRequested.connect(self.showContextMenu)
        self.experimentTree.itemSelectionChanged.connect(self.onItemSelected)
        self.experimentTree.setEnabled(True)
        self.experimentTree.setMinimumSize(200,521)
        self.experimentTree.setMaximumWidth(350)
        self.experimentTree.setObjectName("experimentTree")
        self.experimentTree.headerItem().setText(0, "Experiments New")
        self.experimentTree.setSortingEnabled(False)
        self.windowBoxHLayout.addWidget(self.experimentTree)

        self.windowBoxVLayout = QtWidgets.QVBoxLayout()
        #self.windowBoxHLayout.setContentsMargins(0, 0, 0, 0)
        self.windowBoxVLayout.setObjectName("windowBoxVLayout")

        self.basedataStackedWidget = QStackedWidget()
        self.basedataStackedWidget.setObjectName("basedataStackedWidget")
        self.basedataStackedWidget.setEnabled(False)
        self.windowBoxVLayout.addWidget(self.basedataStackedWidget)

        self.refreshConnsButton = QtWidgets.QPushButton("Refresh Status")
        self.refreshConnsButton.clicked.connect(self.refreshConnsStatus)
        self.refreshConnsButton.setEnabled(False)
        self.windowBoxVLayout.addWidget(self.refreshConnsButton)

        self.windowBoxHLayout.addLayout(self.windowBoxVLayout)
        
        # Context menu
        self.connsContextMenu = QtWidgets.QMenu()
        self.createGuac = self.connsContextMenu.addAction("Create Users")
        self.createGuac.triggered.connect(self.menuItemSelected)
        self.removeGuac = self.connsContextMenu.addAction("Remove Users")
        self.removeGuac.triggered.connect(self.menuItemSelected)
        self.clearGuac = self.connsContextMenu.addAction("Clear All Entries")
        self.clearGuac.triggered.connect(self.menuItemSelected)

        self.setLayout(self.windowBoxHLayout)
        self.retranslateUi()

    def retranslateUi(self):
        logging.debug("ConnectionWidget: retranslateUi(): instantiated")
        self.setWindowTitle("ConnectionWidget")
        self.experimentTree.headerItem().setText(0, "Experiments")
        self.experimentTree.setSortingEnabled(False)
    
    def onItemSelected(self):
        logging.debug("MainApp:onItemSelected instantiated")
        self.basedataStackedWidget.setEnabled(True)
        self.refreshConnsButton.setEnabled(True)
    	# Get the selected item
        selectedItem = self.experimentTree.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:onItemSelected no configurations left")
            self.statusBar.showMessage("No configuration items selected or available.")
            return

        #Check if it's the case that an experiment name was selected
        parentparentSelectedItem = None
        parentSelectedItem = selectedItem.parent()
        if parentSelectedItem != None:
            parentparentSelectedItem = selectedItem.parent().parent()
            
        if parentSelectedItem == None:
            #A base widget was selected
            self.basedataStackedWidget.setCurrentWidget(self.connectionBaseWidgets[selectedItem.text(0)]["ExperimentActionsBaseWidget"])
            self.experimentTree.resizeColumnToContents(0)
        elif parentparentSelectedItem == None:
            #A base widget was selected
            self.basedataStackedWidget.setCurrentWidget(self.connectionBaseWidgets[parentSelectedItem.text(0)]["ExperimentActionsBaseWidget"])
            self.experimentTree.resizeColumnToContents(0)
        else:
            #Check if it's the case that a VM Name was selected
            if(selectedItem.text(0)[0] == "V"):
                logging.debug("Setting right widget: " + str(self.connectionBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsVMWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.connectionBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsVMWidgets"][selectedItem.text(0)])
            if(selectedItem.text(0)[0] == "S"):
                logging.debug("Setting right widget: " + str(self.connectionBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsSetWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.connectionBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsSetWidgets"][selectedItem.text(0)])
            if(selectedItem.text(0)[0] == "T"):
                logging.debug("Setting right widget: " + str(self.connectionBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsTemplateWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.connectionBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsTemplateWidgets"][selectedItem.text(0)])
            if(selectedItem.text(0)[0] == "U"):
                logging.debug("Setting right widget: " + str(self.connectionBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsUserWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.connectionBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsUserWidgets"][selectedItem.text(0)])


    def getExperimentVMRolledOut(self, configname, config_json):
        logging.debug("ConnectionWidget(): getExperimentVMRolledOut(): retranslateUi(): instantiated")
        self.rolledoutjson = self.eco.getExperimentVMRolledOut(configname, config_json)

    def addExperimentItem(self, configname, config_jsondata=None):
        logging.debug("addExperimentItem(): retranslateUi(): instantiated")
        if configname in self.experimentItemNames:
            logging.error("addExperimentItem(): Item already exists in tree: " + str(configname))
            return
        userpool = UserPool()
        ##Now add the item to the tree widget and create the baseWidget
        experimentTreeWidgetItem = QtWidgets.QTreeWidgetItem(self.experimentTree)
        experimentTreeWidgetItem.setText(0,configname)
        button = QPushButton("connect")
        experimentTreeWidgetItem.setText(0,configname)
        experimentTreeWidgetItem.setText(1,"connect")

        experimentSetTreeItem = QtWidgets.QTreeWidgetItem(experimentTreeWidgetItem)
        experimentSetTreeItem.setText(0,"Sets")

        experimentCloneTreeItem = QtWidgets.QTreeWidgetItem(experimentTreeWidgetItem)
        experimentCloneTreeItem.setText(0,"Templates")

        experimentVMTreeItem = QtWidgets.QTreeWidgetItem(experimentTreeWidgetItem)
        experimentVMTreeItem.setText(0,"VMs/Conns")

        experimentUserTreeItem = QtWidgets.QTreeWidgetItem(experimentTreeWidgetItem)
        experimentUserTreeItem.setText(0,"Users")

        self.experimentItemNames[configname] = experimentTreeWidgetItem
        #get all rolled out and then get them by VM
        funcs = []
        funcs.append((self.getExperimentVMRolledOut, configname, config_jsondata))
        GUIFunctionExecutingDialog(None, "Processing Conns for " + str(configname), funcs).exec_()
        rolledoutjson = self.rolledoutjson

        if rolledoutjson != None:
            #get the usersConn associations first:
            # if file was specified, but it doesn't exist, prepend usernames
            invalid_userfile = False
            users_filename = config_jsondata["xml"]["testbed-setup"]["vm-set"]["users-filename"]
            if users_filename != None and users_filename.strip() != "":
                if os.path.exists(users_filename) == False:
                    invalid_userfile = True
            
            usersConns = userpool.generateUsersConns(configname, creds_file=users_filename, rolledout_json=rolledoutjson)
            vmuser_mapping = {}
            for (username, password) in usersConns:
                for conn in usersConns[(username, password)]:
                    cloneVMName = conn[0]
                    if invalid_userfile == False:
                        vmuser_mapping[cloneVMName] = username
                    else:
                        vmuser_mapping[cloneVMName] = "userfile_not_found"
                    
            #create the status widgets (tables)
            self.experimentActionsBaseWidget = ConnectionStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=[], vmuser_mapping=vmuser_mapping, status_bar=self.statusBar)
            self.connectionBaseWidgets[configname] = {"ExperimentActionsBaseWidget": {}, "ExperimentActionsSetWidgets": {}, "ExperimentActionsTemplateWidgets": {}, "ExperimentActionsVMWidgets": {}, "ExperimentActionsUserWidgets": {} }
            self.connectionBaseWidgets[configname]["ExperimentActionsBaseWidget"] = self.experimentActionsBaseWidget
            self.basedataStackedWidget.addWidget(self.experimentActionsBaseWidget)
            #Set-based view
            (template_vms, num_clones) = rolledoutjson
            #First create the sets from the rolled out data
            sets = self.eco.getExperimentSetDictFromRolledOut(configname, rolledoutjson)
            for set in sets:
                set_item = QtWidgets.QTreeWidgetItem(experimentSetTreeItem)
                setlabel = "S: Set " + set
                set_item.setText(0,setlabel)
                # Set Widget
                experimentActionsSetStatusWidget = ConnectionStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=sets[set], vmuser_mapping=vmuser_mapping, status_bar=self.statusBar)
                self.connectionBaseWidgets[configname]["ExperimentActionsSetWidgets"][setlabel] = experimentActionsSetStatusWidget
                self.basedataStackedWidget.addWidget(experimentActionsSetStatusWidget)

            templates = self.eco.getExperimentVMNamesFromTemplateFromRolledOut(configname, rolledoutjson)
            for templatename in templates:
                template_item = QtWidgets.QTreeWidgetItem(experimentCloneTreeItem)
                templatelabel = "T: " + templatename
                template_item.setText(0,templatelabel)
                # Set Widget
                experimentActionsTemplateStatusWidget = ConnectionStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=templates[templatename], vmuser_mapping=vmuser_mapping, status_bar=self.statusBar)
                self.connectionBaseWidgets[configname]["ExperimentActionsTemplateWidgets"][templatelabel] = experimentActionsTemplateStatusWidget
                self.basedataStackedWidget.addWidget(experimentActionsTemplateStatusWidget)

            #Individual VM-based view
            vms_list = self.eco.getExperimentVMListsFromRolledOut(configname, rolledoutjson)
            for vm in vms_list:
                vmname = vm["name"]
                vm_item = QtWidgets.QTreeWidgetItem(experimentVMTreeItem)
                vmlabel = "V: " + vmname
                vm_item.setText(0,vmlabel)
                # VM Config Widget
                connectionStatusWidget = ConnectionStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=[vmname], vmuser_mapping=vmuser_mapping, status_bar=self.statusBar)
                self.connectionBaseWidgets[configname]["ExperimentActionsVMWidgets"][vmlabel] = connectionStatusWidget
                self.basedataStackedWidget.addWidget(connectionStatusWidget)

            #Individual Users-based view
            num = 1
            for (username, password) in usersConns:
                vmnames = [tuple[0] for tuple in usersConns[(username, password)] ]
                user_item = QtWidgets.QTreeWidgetItem(experimentUserTreeItem)
                user_label = "U: " + username + " (Set " + str(num) + ")"
                num+=1
                user_item.setText(0,user_label)
                # VM Config Widget
                experimentActionsUserStatusWidget = ConnectionStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=vmnames, vmuser_mapping=vmuser_mapping, status_bar=self.statusBar)
                self.connectionBaseWidgets[configname]["ExperimentActionsUserWidgets"][user_label] = experimentActionsUserStatusWidget
                self.basedataStackedWidget.addWidget(experimentActionsUserStatusWidget)

        self.statusBar.showMessage("Added new experiment: " + str(configname))
        logging.debug("addExperimentItem(): retranslateUi(): Completed")

    def resetExperiment(self, configname, config_jsondata):
        logging.debug("updateExperimentItem(): retranslateUi(): instantiated")
        if configname not in self.experimentItemNames:
            logging.error("removeExperimentItem(): Item does not exist in tree: " + str(configname))
            return
        self.removeExperimentItem(configname)
        self.addExperimentItem(configname, config_jsondata)

    def removeExperimentItem(self, configname):
        logging.debug("removeExperimentItem(): retranslateUi(): instantiated")
        if configname not in self.experimentItemNames:
            logging.error("removeExperimentItem(): Item does not exist in tree: " + str(configname))
            return
        experimentTreeWidgetItem = self.experimentItemNames[configname]
        self.experimentTree.invisibleRootItem().removeChild(experimentTreeWidgetItem)
        del self.experimentItemNames[configname]
        logging.debug("removeExperimentItem(): Completed")

    def showContextMenu(self, position):
        logging.debug("ConnectionWidget(): showContextMenu(): instantiated")
        self.connsContextMenu.popup(self.experimentTree.mapToGlobal(position))

    def getTypeNameFromSelection(self, currentItem):
        configname = ""
        itype = ""
        name = ""
        #configname selected
        if self.experimentTree.currentItem().parent() == None:
            configname = self.experimentTree.currentItem().text(0)
            itype = "set"
            name = "all"
        #sets, clones, or VMs label selected
        elif self.experimentTree.currentItem().parent().parent() == None:
            configname = self.experimentTree.currentItem().parent().text(0)
            itype = "set"
            name = "all"
        #specific item selected
        elif self.experimentTree.currentItem().parent().parent().parent() == None:
            configname = self.experimentTree.currentItem().parent().parent().text(0)
            currItemText = self.experimentTree.currentItem().text(0)
            if currItemText.startswith("S: Set "):
                itype = "set"
                name = currItemText.split("S: Set ")[1:]
                name = " ".join(name)
            elif currItemText.startswith("V: "):
                itype = "vm"
                name = currItemText.split("V: ")[1:]
                name = "\"" + " ".join(name) + "\""
            elif currItemText.startswith("T: "):
                itype = "template"
                name = currItemText.split("T: ")[1:]
                name = "\"" + " ".join(name) + "\""
            elif currItemText.startswith("U: "):
                itype = "set"
                name = currItemText.split("(Set ")[1].split(")")[0]
                name = " ".join(name)
        return configname, itype, name

    def menuItemSelected(self):
        logging.debug("menuItemSelected(): instantiated")
        actionlabelname = self.sender().text()
        configname, itype, name = self.getTypeNameFromSelection(self.experimentTree.currentItem())
        
        ##get server info
        vmHostname, rdpBrokerHostname, chatServerIP, users_file = self.eco.getExperimentServerInfo(configname)
        if vmHostname != None and rdpBrokerHostname != None:
            if users_file == None:
                ConnectionActions().connectionActionEvent(self, configname, actionlabelname, vmHostname, rdpBrokerHostname, users_file="", itype=itype, name=name)
            else:
                ConnectionActions().connectionActionEvent(self, configname, actionlabelname, vmHostname, rdpBrokerHostname, users_file, itype, name)
        self.statusBar.showMessage("Executed " + str(actionlabelname) + " for " + configname)

    def refreshConnsStatus(self):
        logging.debug("refreshVMStatus(): instantiated")

        #Get the configname based on selected item:
        selectedItem = self.experimentTree.currentItem()
        #Check if an experiment name is selected
        if selectedItem == None:
            logging.error("No experiment label was selected.")
            return

        #If so, get the configname associated with it
        while selectedItem.parent() != None:
            selectedItem = selectedItem.parent()
        configname = selectedItem.text(0)

        vmHostname, rdpBrokerHostname, chatServerIP, users_file = self.eco.getExperimentServerInfo(configname)
        s = ConnectionActionDialog(self, configname, "Refresh", vmHostname, rdpBrokerHostname).exec_()
        #format: {"readStatus" : self.readStatus, "writeStatus" : self.writeStatus, "usersConnsStatus" : [(username, connName): {"user_status": user_perm, "connStatus": active}] }
        if s == QMessageBox.Cancel:
            logging.debug("Cancel pressed")
            return
        if s == None or s == -1:
            logging.error("Could not retrieve connection status: " + str(s))
            QMessageBox.warning(self,
                        "No Results",
                        "Incorrect credentials or no connectivity",
                        QMessageBox.Ok)
            return

        self.usersConnsStatus = s["usersConnsStatus"]
        
        #Update all vm status in the subtrees
        #First the "all" view
        for widget in self.connectionBaseWidgets[configname].values():
            if isinstance(widget, ConnectionStatusWidget):
                widget.updateConnStatus(self.usersConnsStatus)
        #The Sets:
        for widget in self.connectionBaseWidgets[configname]["ExperimentActionsSetWidgets"].values():
            if isinstance(widget, ConnectionStatusWidget):
                widget.updateConnStatus(self.usersConnsStatus)
        #The Templates:
        for widget in self.connectionBaseWidgets[configname]["ExperimentActionsTemplateWidgets"].values():
            if isinstance(widget, ConnectionStatusWidget):
                widget.updateConnStatus(self.usersConnsStatus)
        #The VMs
        for widget in self.connectionBaseWidgets[configname]["ExperimentActionsVMWidgets"].values():
            if isinstance(widget, ConnectionStatusWidget):
                widget.updateConnStatus(self.usersConnsStatus)
        #The Users
        for widget in self.connectionBaseWidgets[configname]["ExperimentActionsUserWidgets"].values():
            if isinstance(widget, ConnectionStatusWidget):
                widget.updateConnStatus(self.usersConnsStatus)