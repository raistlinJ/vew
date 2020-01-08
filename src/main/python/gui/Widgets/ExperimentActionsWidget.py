from PyQt5 import QtCore, QtGui, QtWidgets
import logging

class ExperimentActionsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logging.debug("ExperimentActionsWidget instantiated")
        QtWidgets.QWidget.__init__(self, parent=None)

        self.outerVertBox = QtWidgets.QVBoxLayout()
        self.outerVertBox.setContentsMargins(0, 0, 0, 0)
        self.outerVertBox.setObjectName("outerVertBox")

        self.setObjectName("ExperimentActionsWidget")
        self.resize(336, 281)
        self.treeWidget = QtWidgets.QTreeWidget(parent)
        self.treeWidget.setGeometry(QtCore.QRect(0, 0, 660, 520))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().resizeSection(0, 150)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.showContextMenu)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        self.outerVertBox.addWidget(self.treeWidget)

        # Context menu for blank space
        self.workshopMenu = QtWidgets.QMenu()

        self.cloneWorkshop = self.workshopMenu.addAction("Signal - Create Clones")
        self.cloneWorkshop.triggered.connect(self.cloneWorkshopActionEvent)
        
        self.startVMs = self.workshopMenu.addAction("Signal - Start VMs (headless)")
        self.startVMs.triggered.connect(self.startVMsActionEvent)
        
        self.poweroffVMs = self.workshopMenu.addAction("Signal - Power Off VMs")
        self.poweroffVMs.triggered.connect(self.poweroffVMsActionEvent)

        self.restoreSnapshots = self.workshopMenu.addAction("Signal - Restore Snapshots")
        self.restoreSnapshots.triggered.connect(self.restoreSnapshotsActionEvent)
        
        self.deleteClones = self.workshopMenu.addAction("Signal - Delete Clones")
        self.deleteClones.triggered.connect(self.deleteClonesActionEvent)
        self.setLayout(self.outerVertBox)

        self.retranslateUi()

    def retranslateUi(self):
        logging.debug("ExperimentActionsWidget: retranslateUi(): instantiated")
        # self.setWindowTitle("ExperimentActionsWidget")
        # self.treeWidget.headerItem().setText(0, "Workshop")
        # self.treeWidget.headerItem().setText(1, "Status")
        # sortingEnabled = self.treeWidget.isSortingEnabled()
        # self.treeWidget.setSortingEnabled(False)
        # self.treeWidget.topLevelItem(0).setText(0, "Workshop 1")
        # self.treeWidget.topLevelItem(0).setText(1, "Clones Not Created")
        # self.treeWidget.setSortingEnabled(sortingEnabled)

    def showContextMenu(self, position):
        self.workshopMenu.popup(self.treeWidget.mapToGlobal(position))

    def cloneWorkshopActionEvent(self):
        pass

    def startVMsActionEvent(self):
        pass

    def poweroffVMsActionEvent(self):
        pass

    def restoreSnapshotsActionEvent(self):
        pass

    def deleteClonesActionEvent(self):
        pass
