from gui.Helpers.ExperimentActions import ExperimentActions
from engine.Configuration.UserPool import UserPool
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QTableView, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

import logging

class ExperimentActionsVMStatusWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, configname=None, widgetname="", rolledoutjson=None, interest_vmnames = [], vmuser_mapping={}, status_bar=None):
        logging.debug("ExperimentActionsBaseWidgets instantiated")
        if configname == None:
            logging.error("configname cannot be empty")
            return None
        QtWidgets.QWidget.__init__(self, parent=None)
        self.statusBar = status_bar
        self.widgetname = widgetname
        self.configname = configname
        self.rolledoutjson = rolledoutjson

        self.setWindowTitle("ExperimentActionsBaseWidgets")
        self.setObjectName("ExperimentActionsBaseWidgets")
        self.layoutWidget = QtWidgets.QWidget()
        self.layoutWidget.setObjectName("layoutWidget")
        self.outerVertBox = QtWidgets.QVBoxLayout()
        self.outerVertBox.setObjectName("outerVertBox")
        self.layoutWidget.setLayout(self.outerVertBox)

        self.vmStatusTable = QtWidgets.QTableWidget(parent)
        self.vmStatusTable.setObjectName("vmStatusTable")
        self.vmStatusTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vmStatusTable.setSelectionBehavior(QTableView.SelectRows)
        self.vmStatusTable.setSelectionMode(QTableView.SingleSelection)
        
        self.vmStatusTable.setRowCount(0)
        self.vmStatusTable.setColumnCount(4)
        self.vmStatusTable.setHorizontalHeaderLabels(("VM Name", "UUID", "Generated User", "Status"))

        # Context menus
        self.vmStatusTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.vmStatusTable.customContextMenuRequested.connect(self.showContextMenu)
        self.experimentMenu = QtWidgets.QMenu()
        self.startupContextMenu = QtWidgets.QMenu("Startup")
        self.shutdownContextMenu = QtWidgets.QMenu("Shutdown")
        self.stateContextMenu = QtWidgets.QMenu("State")
        self.experimentMenu.addMenu(self.startupContextMenu)
        self.experimentMenu.addMenu(self.shutdownContextMenu)
        self.experimentMenu.addMenu(self.stateContextMenu)

        self.cloneExperiment = self.startupContextMenu.addAction("Signal - Create Clone")
        self.cloneExperiment.triggered.connect(self.menuItemSelected)
        
        self.startVMs = self.startupContextMenu.addAction("Signal - Start VM (headless)")
        self.startVMs.triggered.connect(self.menuItemSelected)

        self.restoreSnapshots = self.startupContextMenu.addAction("Signal - Restore Snapshot")
        self.restoreSnapshots.triggered.connect(self.menuItemSelected)

        self.pauseVMs = self.shutdownContextMenu.addAction("Signal - Pause VM")
        self.pauseVMs.triggered.connect(self.menuItemSelected)

        self.suspendVMs = self.shutdownContextMenu.addAction("Signal - Suspend & Save State")
        self.suspendVMs.triggered.connect(self.menuItemSelected)

        self.poweroffVMs = self.shutdownContextMenu.addAction("Signal - Power Off VM")
        self.poweroffVMs.triggered.connect(self.menuItemSelected)

        self.deleteClones = self.shutdownContextMenu.addAction("Signal - Delete Clone")
        self.deleteClones.triggered.connect(self.menuItemSelected)
        self.shutdownContextMenu.addAction(self.deleteClones)

        self.snapshotVMs = self.stateContextMenu.addAction("Signal - Snapshot VM")
        self.snapshotVMs.triggered.connect(self.menuItemSelected)

        self.vmStatusTable.setSortingEnabled(True)
        self.outerVertBox.addWidget(self.vmStatusTable)

        self.setLayout(self.outerVertBox)
        self.retranslateUi(rolledoutjson, interest_vmnames, vmuser_mapping)

    def retranslateUi(self, rolledoutjson, interest_vmnames, vmuser_mapping):
        logging.debug("ExperimentActionsVMStatusWidget: retranslateUi(): instantiated")
        
        if rolledoutjson == None:
            return
        (template_vms, num_clones) = rolledoutjson
        for template_vm in template_vms:
            for cloned_vm in template_vms[template_vm]:
                if interest_vmnames == [] or cloned_vm["name"] in interest_vmnames:
                    rowPos = self.vmStatusTable.rowCount()
                    self.vmStatusTable.insertRow(rowPos)
                    vmName = str(cloned_vm["name"])
                    vmCell = QTableWidgetItem(vmName)
                    uuidCell = QTableWidgetItem(str("refresh req."))
                    username = "vrdp disabled"
                    if vmuser_mapping != {} and vmName in vmuser_mapping:
                        username = vmuser_mapping[vmName]
                    usernameCell = QTableWidgetItem(username)
                    statusCell = QTableWidgetItem(str("refresh req."))
                    # statusCell.setFlags(Qt.ItemIsEnabled)
                    self.vmStatusTable.setItem(rowPos, 0, vmCell)
                    self.vmStatusTable.setItem(rowPos, 1, uuidCell)
                    self.vmStatusTable.setItem(rowPos, 2, usernameCell)
                    self.vmStatusTable.setItem(rowPos, 3, statusCell)
                    self.vmStatusTable.resizeColumnToContents(0)

    def showContextMenu(self, position):
        logging.debug("showContextMenu() instantiated")
        self.experimentMenu.popup(self.vmStatusTable.mapToGlobal(position))

    def menuItemSelected(self):
        logging.debug("menuItemSelected(): instantiated")
        vmRow = self.vmStatusTable.currentRow()
        if vmRow == None:
            logging.error("menuItemSelected(): No Row is Selected.")
            return
        vmName = self.vmStatusTable.item(vmRow,0).text()
        actionlabelname = self.sender().text()
        ExperimentActions().experimentActionEvent(self.configname, actionlabelname, "vm", vmName)
        self.statusBar.showMessage("Executed " + str(actionlabelname) + " on " + self.configname)

    def updateVMStatus(self, vmStatus):
        logging.debug("updateVMStatus(): instantiated")
        
        for cell in range(0,self.vmStatusTable.rowCount()):
            tableVMName = self.vmStatusTable.item(cell, 0).text()
            tmpCellItem = self.vmStatusTable.item(cell, 3)
            if tableVMName in vmStatus:
                tmpCellItem.setText(vmStatus[tableVMName]["vmState"])
            else:
                tmpCellItem.setText("missing")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = ExperimentActionsVMStatusWidget()
    ui.show()
    sys.exit(app.exec_())
