from PyQt5 import QtCore, QtGui, QtWidgets
import logging
from gui.Dialogs.ExperimentActionDialog import ExperimentActionDialog

class ExperimentActionsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, statusBar=None):
        logging.debug("ExperimentActionsWidget instantiated")
        QtWidgets.QWidget.__init__(self, parent=None)
        self.statusBar = statusBar
        self.experimentItemNames = {}
        self.outerVertBox = QtWidgets.QVBoxLayout()
        self.outerVertBox.setObjectName("outerVertBox")

        self.setObjectName("ExperimentActionsWidget")
        self.treeWidget = QtWidgets.QTreeWidget(parent)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().resizeSection(0, 150)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.showContextMenu)
        self.outerVertBox.addWidget(self.treeWidget)

        # Context menu for blank space
        self.experimentMenu = QtWidgets.QMenu()

        self.cloneExperiment = self.experimentMenu.addAction("Signal - Create Clones")
        self.cloneExperiment.triggered.connect(self.cloneExperimentActionEvent)
        
        self.startVMs = self.experimentMenu.addAction("Signal - Start VMs (headless)")
        self.startVMs.triggered.connect(self.startVMsActionEvent)
        
        self.poweroffVMs = self.experimentMenu.addAction("Signal - Power Off VMs")
        self.poweroffVMs.triggered.connect(self.poweroffVMsActionEvent)

        self.restoreSnapshots = self.experimentMenu.addAction("Signal - Restore Snapshots")
        self.restoreSnapshots.triggered.connect(self.restoreSnapshotsActionEvent)
        
        self.deleteClones = self.experimentMenu.addAction("Signal - Delete Clones")
        self.deleteClones.triggered.connect(self.deleteClonesActionEvent)
        self.setLayout(self.outerVertBox)

        self.retranslateUi()

    def retranslateUi(self):
        logging.debug("ExperimentActionsWidget: retranslateUi(): instantiated")
        self.setWindowTitle("ExperimentActionsWidget")
        self.treeWidget.headerItem().setText(0, "Experiment Name")
        self.treeWidget.headerItem().setText(1, "Status")
        self.treeWidget.setSortingEnabled(False)
    
    def addExperimentItem(self, configname):
        logging.debug("addExperimentItem(): retranslateUi(): instantiated")
        if configname in self.experimentItemNames:
            logging.error("addExperimentItem(): Item already exists in tree: " + str(configname))
            return
        configTreeWidgetItem = QtWidgets.QTreeWidgetItem(self.treeWidget)
        configTreeWidgetItem.setText(0,configname)
        configTreeWidgetItem.setText(1,"Unknown")
        self.experimentItemNames[configname] = configTreeWidgetItem
        logging.debug("addExperimentItem(): retranslateUi(): Completed")

    def removeExperimentItem(self, configname):
        logging.debug("removeExperimentItem(): retranslateUi(): instantiated")
        if configname not in self.experimentItemNames:
            logging.error("removeExperimentItem(): Item does not exist in tree: " + str(configname))
            return
        configTreeWidgetItem = self.experimentItemNames[configname]
        self.treeWidget.invisibleRootItem().removeChild(configTreeWidgetItem)
        del self.experimentItemNames[configname]
        logging.debug("removeExperimentItem(): Completed")

    def showContextMenu(self, position):
        logging.debug("removeExperimentItem(): showContextMenu(): instantiated")
        self.experimentMenu.popup(self.treeWidget.mapToGlobal(position))

            # if self.action == "Create Experiment":
            #     e.execute("experiment create " + str(self.configname))
            # elif self.action == "Start Experiment":
            #     e.execute("experiment start " + str(self.configname))
            # elif self.action == "Stop Experiment":
            #     e.execute("experiment stop " + str(self.configname))
            # elif self.action == "Restore Experiment":
            #     e.execute("experiment restore " + str(self.configname))
            # elif self.action == "Remove Experiment":
            #     e.execute("experiment remove " + str(self.configname))

    def cloneExperimentActionEvent(self):
        logging.debug("cloneExperimentActionEvent(): showContextMenu(): instantiated")
        #Now allow the user to choose the VM:
        ExperimentActionDialog().experimentActionDialog(self.treeWidget.currentItem().text(0), "Create Experiment")
        self.statusBar.showMessage("Finished executing Create Experiment " + str(self.treeWidget.currentItem().text(0)))

    def startVMsActionEvent(self):
        logging.debug("startVMsActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.treeWidget.currentItem().text(0), "Start Experiment")
        self.statusBar.showMessage("Finished executing Start Experiment " + str(self.treeWidget.currentItem().text(0)))

    def poweroffVMsActionEvent(self):
        logging.debug("poweroffVMsActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.treeWidget.currentItem().text(0), "Stop Experiment")
        self.statusBar.showMessage("Finished executing Stop Experiment " + str(self.treeWidget.currentItem().text(0)))

    def restoreSnapshotsActionEvent(self):
        logging.debug("restoreSnapshotsActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.treeWidget.currentItem().text(0), "Restore Experiment")
        self.statusBar.showMessage("Finished executing Restore Experiment " + str(self.treeWidget.currentItem().text(0)))

    def deleteClonesActionEvent(self):
        logging.debug("deleteClonesActionEvent(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(self.treeWidget.currentItem().text(0), "Remove Experiment")
        self.statusBar.showMessage("Finished executing Remove Experiment " + str(self.treeWidget.currentItem().text(0)))
