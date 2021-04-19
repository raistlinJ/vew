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
        parentSelectedItem = selectedItem.parent()
        if(parentSelectedItem == None):
            #A base widget was selected
            self.basedataStackedWidget.setCurrentWidget(self.experimentActionsBaseWidgets[selectedItem.text(0)]["ExperimentActionsBaseWidget"])
            self.experimentTree.resizeColumnToContents(0)
        else:
            #Check if it's the case that a VM Name was selected
            if(selectedItem.text(0)[0] == "V"):
                logging.debug("Setting right widget: " + str(self.experimentActionsBaseWidgets[parentSelectedItem.text(0)]["ExperimentActionsVMWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.experimentActionsBaseWidgets[parentSelectedItem.text(0)]["ExperimentActionsVMWidgets"][selectedItem.text(0)])
            if(selectedItem.text(0)[0] == "S"):
                logging.debug("Setting right widget: " + str(self.experimentActionsBaseWidgets[parentSelectedItem.text(0)]["ExperimentActionsSetWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.experimentActionsBaseWidgets[parentSelectedItem.text(0)]["ExperimentActionsSetWidgets"][selectedItem.text(0)])

    def addExperimentItem(self, configname, config_jsondata):
        logging.debug("addExperimentItem(): retranslateUi(): instantiated")
        if configname in self.experimentItemNames:
            logging.error("addExperimentItem(): Item already exists in tree: " + str(configname))
            return
        
        ##Now add the item to the tree widget and create the baseWidget
        experimentTreeWidgetItem = QtWidgets.QTreeWidgetItem(self.experimentTree)
        experimentTreeWidgetItem.setText(0,configname)

        self.experimentItemNames[configname] = experimentTreeWidgetItem
        #get all rolled out and then get them by VM
        
        rolledoutjson = self.eco.getExperimentVMRolledOut(configname, config_jsondata)
        #Base Config Widget ("all view")
        self.experimentActionsBaseWidget = ExperimentActionsVMStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=[])
        self.experimentActionsBaseWidgets[configname] = {"ExperimentActionsBaseWidget": {}, "ExperimentActionsSetWidgets": {}, "ExperimentActionsVMWidgets": {} }
        self.experimentActionsBaseWidgets[configname]["ExperimentActionsBaseWidget"] = self.experimentActionsBaseWidget
        self.basedataStackedWidget.addWidget(self.experimentActionsBaseWidget)
        #Set-based view

        (template_vms, num_clones) = rolledoutjson
        #First create the sets from the rolled out data
        sets = {}
        for template_vm in template_vms:
            for clone_num in range(num_clones):
                if str(clone_num+1) not in sets:
                    sets[str(clone_num+1)] = []
                sets[str(clone_num+1)].append(template_vms[template_vm][clone_num]["name"])

        for set in sets:
            set_item = QtWidgets.QTreeWidgetItem(experimentTreeWidgetItem)
            setlabel = "S: Set " + set
            set_item.setText(0,setlabel)
            # Set Widget
            experimentActionsSetStatusWidget = ExperimentActionsVMStatusWidget(self, configname, rolledoutjson=rolledoutjson, interest_vmnames=sets[set])
            self.experimentActionsBaseWidgets[configname]["ExperimentActionsSetWidgets"][setlabel] = experimentActionsSetStatusWidget
            self.basedataStackedWidget.addWidget(experimentActionsSetStatusWidget)

        #Individual VM-based view
        (template_vms, num_clones) = rolledoutjson
        for template_vm in template_vms:
            for cloned_vm in template_vms[template_vm]:
                vmname = cloned_vm["name"]
                vm_item = QtWidgets.QTreeWidgetItem(experimentTreeWidgetItem)
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

    def cloneExperimentActionEvent(self):
        logging.debug("cloneExperimentActionEvent(): showContextMenu(): instantiated")
        #Now allow the user to choose the VM:
        ExperimentActionDialog().experimentActionDialog(self.experimentTree.currentItem().text(0), "Create Experiment")
        self.statusBar.showMessage("Finished executing Create Experiment " + str(self.experimentTree.currentItem().text(0)))

    def startVMsActionEvent(self):
        logging.debug("startVMsActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.experimentTree.currentItem().text(0), "Start Experiment")
        self.statusBar.showMessage("Finished executing Start Experiment " + str(self.experimentTree.currentItem().text(0)))

    def suspendVMsActionEvent(self):
        logging.debug("suspendVMsActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.experimentTree.currentItem().text(0), "Suspend Experiment")
        self.statusBar.showMessage("Finished executing Suspend Experiment " + str(self.experimentTree.currentItem().text(0)))

    def pauseVMsActionEvent(self):
        logging.debug("pauseVMsActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.experimentTree.currentItem().text(0), "Pause Experiment")
        self.statusBar.showMessage("Finished executing Pause Experiment " + str(self.experimentTree.currentItem().text(0)))

    def snapshotVMsActionEvent(self):
        logging.debug("snapshotVMsActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.experimentTree.currentItem().text(0), "Snapshot Experiment")
        self.statusBar.showMessage("Finished executing Snapshot Experiment " + str(self.experimentTree.currentItem().text(0)))

    def poweroffVMsActionEvent(self):
        logging.debug("poweroffVMsActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.experimentTree.currentItem().text(0), "Stop Experiment")
        self.statusBar.showMessage("Finished executing Stop Experiment " + str(self.experimentTree.currentItem().text(0)))

    def restoreSnapshotsActionEvent(self):
        logging.debug("restoreSnapshotsActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.experimentTree.currentItem().text(0), "Restore Experiment")
        self.statusBar.showMessage("Finished executing Restore Experiment " + str(self.experimentTree.currentItem().text(0)))

    def deleteClonesActionEvent(self):
        logging.debug("deleteClonesActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.experimentTree.currentItem().text(0), "Remove Experiment")
        self.statusBar.showMessage("Finished executing Remove Experiment " + str(self.experimentTree.currentItem().text(0)))
