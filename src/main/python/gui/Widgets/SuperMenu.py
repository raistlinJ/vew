# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SuperMenu.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class SuperMenu(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(336, 281)
        self.treeWidget = QtWidgets.QTreeWidget(Form)
        self.treeWidget.setGeometry(QtCore.QRect(0, 0, 660, 520))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().resizeSection(0, 150)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.showContextMenu)

        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)

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


        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)


    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.treeWidget.headerItem().setText(0, _translate("Form", "Workshop"))
        self.treeWidget.headerItem().setText(1, _translate("Form", "Status"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("Form", "Workshop 1"))
        self.treeWidget.topLevelItem(0).setText(1, _translate("Form", "Clones Not Created"))
        self.treeWidget.setSortingEnabled(__sortingEnabled)

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
