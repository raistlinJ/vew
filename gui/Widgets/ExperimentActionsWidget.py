from PyQt5 import QtCore, QtGui, QtWidgets
import logging
from gui.Dialogs.ExperimentActionDialog import ExperimentActionDialog
from gui.Widgets.ExperimentActionsVMStatusWidget import ExperimentActionsVMStatusWidget
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from PyQt5.QtWidgets import (QApplication, qApp, QAction, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QMessageBox, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QStackedWidget, QStatusBar, QMenuBar)


class ExperimentActionsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, statusBar=None, mainBaseWidgets=None):
        logging.debug("ExperimentActionsWidget instantiated")
        QtWidgets.QWidget.__init__(self, parent=None)
        self.statusBar = statusBar
        self.experimentItemNames = {}
        self.mainBaseWidgets = mainBaseWidgets
        self.experimentActionsBaseWidgets = {}
        self.eco = ExperimentConfigIO()

        self.setObjectName("ExperimentActionsWidget")
#######NEW-TEST
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
        self.experimentTree.setMaximumSize(200,521)
        self.experimentTree.setObjectName("experimentTree")
        self.experimentTree.headerItem().setText(0, "Experiments New")
        self.experimentTree.setSortingEnabled(False)
        self.windowBoxHLayout.addWidget(self.experimentTree)

        self.basedataStackedWidget = QStackedWidget()
        self.basedataStackedWidget.setObjectName("basedataStackedWidget")
        self.windowBoxHLayout.addWidget(self.basedataStackedWidget)
#######END NEW-TEST

        # Context menu for blank space
        self.experimentMenu = QtWidgets.QMenu()
        self.startupContextMenu = QtWidgets.QMenu("Startup")
        self.shutdownContextMenu = QtWidgets.QMenu("Shutdown")
        self.stateContextMenu = QtWidgets.QMenu("State")
        self.experimentMenu.addMenu(self.startupContextMenu)
        self.experimentMenu.addMenu(self.shutdownContextMenu)
        self.experimentMenu.addMenu(self.stateContextMenu)

        self.cloneExperiment = self.startupContextMenu.addAction("Signal - Create Clones")
        self.cloneExperiment.triggered.connect(self.cloneExperimentActionEvent)
        
        self.startVMs = self.startupContextMenu.addAction("Signal - Start VMs (headless)")
        self.startVMs.triggered.connect(self.startVMsActionEvent)

        self.restoreSnapshots = self.startupContextMenu.addAction("Signal - Restore Snapshots")
        self.restoreSnapshots.triggered.connect(self.restoreSnapshotsActionEvent)

        self.pauseVMs = self.shutdownContextMenu.addAction("Signal - Pause VMs")
        self.pauseVMs.triggered.connect(self.pauseVMsActionEvent)
        self.shutdownContextMenu.addAction(self.pauseVMs)

        self.suspendVMs = self.shutdownContextMenu.addAction("Signal - Suspend & Save State")
        self.suspendVMs.triggered.connect(self.suspendVMsActionEvent)
        self.shutdownContextMenu.addAction(self.suspendVMs)

        self.poweroffVMs = self.shutdownContextMenu.addAction("Signal - Power Off VMs")
        self.poweroffVMs.triggered.connect(self.poweroffVMsActionEvent)

        self.deleteClones = self.shutdownContextMenu.addAction("Signal - Delete Clones")
        self.deleteClones.triggered.connect(self.deleteClonesActionEvent)

        self.snapshotVMs = self.stateContextMenu.addAction("Signal - Snapshot VMs")
        self.snapshotVMs.triggered.connect(self.snapshotVMsActionEvent)

        self.setLayout(self.windowBoxHLayout)
        self.retranslateUi()

    def retranslateUi(self):
        logging.debug("ExperimentActionsWidget: retranslateUi(): instantiated")
        self.setWindowTitle("ExperimentActionsWidget")
        self.experimentTree.headerItem().setText(0, "Experiments")
        self.experimentTree.setSortingEnabled(False)
    
    def onItemSelected(self):
        logging.debug("MainApp:onItemSelected instantiated")
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
            self.basedataStackedWidget.setCurrentWidget(self.experimentActionsBaseWidgets[selectedItem.text(0)]["ExperimentActionsBaseWidget"])
            self.experimentTree.resizeColumnToContents(0)
        elif parentparentSelectedItem == None:
            #A base widget was selected
            self.basedataStackedWidget.setCurrentWidget(self.experimentActionsBaseWidgets[parentSelectedItem.text(0)]["ExperimentActionsBaseWidget"])
            self.experimentTree.resizeColumnToContents(0)
        else:
            #Check if it's the case that a VM Name was selected
            if(selectedItem.text(0)[0] == "V"):
                logging.debug("Setting right widget: " + str(self.experimentActionsBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsVMWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.experimentActionsBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsVMWidgets"][selectedItem.text(0)])
            if(selectedItem.text(0)[0] == "S"):
                logging.debug("Setting right widget: " + str(self.experimentActionsBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsSetWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.experimentActionsBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsSetWidgets"][selectedItem.text(0)])
            if(selectedItem.text(0)[0] == "T"):
                logging.debug("Setting right widget: " + str(self.experimentActionsBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsTemplateWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.experimentActionsBaseWidgets[parentparentSelectedItem.text(0)]["ExperimentActionsTemplateWidgets"][selectedItem.text(0)])

    def addExperimentItem(self, configname, config_jsondata):
        logging.debug("addExperimentItem(): retranslateUi(): instantiated")
        if configname in self.experimentItemNames:
            logging.error("addExperimentItem(): Item already exists in tree: " + str(configname))
            return
        
        ##Now add the item to the tree widget and create the baseWidget
        experimentTreeWidgetItem = QtWidgets.QTreeWidgetItem(self.experimentTree)
        experimentTreeWidgetItem.setText(0,configname)

        experimentSetTreeItem = QtWidgets.QTreeWidgetItem(experimentTreeWidgetItem)
        experimentSetTreeItem.setText(0,"Sets")

        experimentCloneTreeItem = QtWidgets.QTreeWidgetItem(experimentTreeWidgetItem)
        experimentCloneTreeItem.setText(0,"Templates")

        experimentVMTreeItem = QtWidgets.QTreeWidgetItem(experimentTreeWidgetItem)
        experimentVMTreeItem.setText(0,"VMs")

        self.experimentItemNames[configname] = experimentTreeWidgetItem
        #get all rolled out and then get them by VM
        
        rolledoutjson = self.eco.getExperimentVMRolledOut(configname, config_jsondata)
        #Base Config Widget ("all view")
        self.experimentActionsBaseWidget = ExperimentActionsVMStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=[])
        self.experimentActionsBaseWidgets[configname] = {"ExperimentActionsBaseWidget": {}, "ExperimentActionsSetWidgets": {}, "ExperimentActionsTemplateWidgets": {}, "ExperimentActionsVMWidgets": {} }
        self.experimentActionsBaseWidgets[configname]["ExperimentActionsBaseWidget"] = self.experimentActionsBaseWidget
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
            experimentActionsSetStatusWidget = ExperimentActionsVMStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=sets[set])
            self.experimentActionsBaseWidgets[configname]["ExperimentActionsSetWidgets"][setlabel] = experimentActionsSetStatusWidget
            self.basedataStackedWidget.addWidget(experimentActionsSetStatusWidget)

        templates = self.eco.getExperimentVMNamesFromTemplateFromRolledOut(configname, rolledoutjson)
        for templatename in templates:
            template_item = QtWidgets.QTreeWidgetItem(experimentCloneTreeItem)
            templatelabel = "T: " + templatename
            template_item.setText(0,templatelabel)
            # Set Widget
            experimentActionsTemplateStatusWidget = ExperimentActionsVMStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=templates[templatename])
            self.experimentActionsBaseWidgets[configname]["ExperimentActionsTemplateWidgets"][templatelabel] = experimentActionsTemplateStatusWidget
            self.basedataStackedWidget.addWidget(experimentActionsTemplateStatusWidget)

        #Individual VM-based view
        vms_list = self.eco.getExperimentVMListsFromRolledOut(configname, rolledoutjson)
        for vm in vms_list:
            vmname = vm["name"]
            vm_item = QtWidgets.QTreeWidgetItem(experimentVMTreeItem)
            vmlabel = "V: " + vmname
            vm_item.setText(0,vmlabel)
            # VM Config Widget
            experimentActionsVMStatusWidget = ExperimentActionsVMStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=[vmname])
            self.experimentActionsBaseWidgets[configname]["ExperimentActionsVMWidgets"][vmlabel] = experimentActionsVMStatusWidget
            self.basedataStackedWidget.addWidget(experimentActionsVMStatusWidget)

        self.statusBar.showMessage("Added new experiment: " + str(configname))
        logging.debug("addExperimentItem(): retranslateUi(): Completed")

    def updateExperimentItem(self, configname):
        logging.debug("updateExperimentItem(): retranslateUi(): instantiated")
        if configname not in self.experimentItemNames:
            logging.error("removeExperimentItem(): Item does not exist in tree: " + str(configname))
            return

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
        logging.debug("ExperimentActionsWidget(): showContextMenu(): instantiated")
        self.experimentMenu.popup(self.experimentTree.mapToGlobal(position))

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
        return configname, itype, name

    def cloneExperimentActionEvent(self):
        logging.debug("cloneExperimentActionEvent(): showContextMenu(): instantiated")
        #Now allow the user to choose the VM:
        configname, itype, name = self.getTypeNameFromSelection(self.experimentTree.currentItem())
        ExperimentActionDialog().experimentActionDialog(configname, "Create Experiment", itype, name)
        self.statusBar.showMessage("Finished executing Create Experiment " + configname)

    def startVMsActionEvent(self):
        logging.debug("startVMsActionEvent(): showContextMenu(): instantiated")
        configname, itype, name = self.getTypeNameFromSelection(self.experimentTree.currentItem())
        ExperimentActionDialog().experimentActionDialog(configname, "Start Experiment", itype, name)
        self.statusBar.showMessage("Finished executing Start Experiment " + configname)

    def suspendVMsActionEvent(self):
        logging.debug("suspendVMsActionEvent(): showContextMenu(): instantiated")
        configname, itype, name = self.getTypeNameFromSelection(self.experimentTree.currentItem())
        ExperimentActionDialog().experimentActionDialog(configname, "Suspend Experiment", itype, name)
        self.statusBar.showMessage("Finished executing Suspend Experiment " + configname)

    def pauseVMsActionEvent(self):
        logging.debug("pauseVMsActionEvent(): showContextMenu(): instantiated")
        configname, itype, name = self.getTypeNameFromSelection(self.experimentTree.currentItem())
        ExperimentActionDialog().experimentActionDialog(configname, "Pause Experiment", itype, name)
        self.statusBar.showMessage("Finished executing Pause Experiment " + configname)

    def snapshotVMsActionEvent(self):
        logging.debug("snapshotVMsActionEvent(): showContextMenu(): instantiated")
        configname, itype, name = self.getTypeNameFromSelection(self.experimentTree.currentItem())
        ExperimentActionDialog().experimentActionDialog(configname, "Snapshot Experiment", itype, name)
        self.statusBar.showMessage("Finished executing Snapshot Experiment " + configname)

    def poweroffVMsActionEvent(self):
        logging.debug("poweroffVMsActionEvent(): showContextMenu(): instantiated")
        configname, itype, name = self.getTypeNameFromSelection(self.experimentTree.currentItem())
        ExperimentActionDialog().experimentActionDialog(configname, "Stop Experiment", itype, name)
        self.statusBar.showMessage("Finished executing Stop Experiment " + configname)

    def restoreSnapshotsActionEvent(self):
        logging.debug("restoreSnapshotsActionEvent(): showContextMenu(): instantiated")
        configname, itype, name = self.getTypeNameFromSelection(self.experimentTree.currentItem())
        ExperimentActionDialog().experimentActionDialog(configname, "Restore Experiment", itype, name)
        self.statusBar.showMessage("Finished executing Restore Experiment " + configname)

    def deleteClonesActionEvent(self):
        logging.debug("deleteClonesActionEvent(): showContextMenu(): instantiated")
        configname, itype, name = self.getTypeNameFromSelection(self.experimentTree.currentItem())
        ExperimentActionDialog().experimentActionDialog(configname, "Remove Experiment", itype, name)
        self.statusBar.showMessage("Finished executing Remove Experiment " + configname)
