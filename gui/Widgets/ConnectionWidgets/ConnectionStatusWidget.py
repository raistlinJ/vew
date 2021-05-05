from gui.Helpers.ConnectionActions import ConnectionActions
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

class ConnectionStatusWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, configname=None, widgetname="", rolledoutjson=None, interest_vmnames = [], vmuser_mapping={}, status_bar=None):
        logging.debug("ConnectionStatusWidget instantiated")
        if configname == None:
            logging.error("configname cannot be empty")
            return None
        QtWidgets.QWidget.__init__(self, parent=None)
        self.statusBar = status_bar
        self.widgetname = widgetname
        self.configname = configname
        self.rolledoutjson = rolledoutjson

        self.setWindowTitle("ConnectionStatusWidget")
        self.setObjectName("ConnectionStatusWidget")
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
        self.vmStatusTable.setColumnCount(5)
        self.vmStatusTable.setHorizontalHeaderLabels(("Connection Name", "Generated User", "Generated Pass", "User Status", "Conn Status"))

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
        logging.debug("ConnectionStatusWidget: retranslateUi(): instantiated")
        
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
                    connStatusCell = QTableWidgetItem(str("refresh req."))
                    username = "vrdp disabled"
                    if vmuser_mapping != {} and vmName in vmuser_mapping:
                        username = vmuser_mapping[vmName]
                    password = "vrdp disabled"
                    if vmuser_mapping != {} and vmName in vmuser_mapping:
                        password = vmuser_mapping[vmName]
                    usernameCell = QTableWidgetItem(username)
                    passwordCell = QTableWidgetItem(password)
                    userStatusCell = QTableWidgetItem(str("refresh req."))
                    # statusCell.setFlags(Qt.ItemIsEnabled)
                    self.vmStatusTable.setItem(rowPos, 0, vmCell)
                    self.vmStatusTable.setItem(rowPos, 1, usernameCell)
                    self.vmStatusTable.setItem(rowPos, 2, passwordCell)
                    self.vmStatusTable.setItem(rowPos, 3, userStatusCell)
                    self.vmStatusTable.setItem(rowPos, 4, connStatusCell)
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
        ConnectionActions().connectionActionEvent(self.configname, actionlabelname, "vm", vmName)
        self.statusBar.showMessage("Executed " + str(actionlabelname) + " on " + self.configname)

    def updateConnStatus(self, usersConnsStatus):
        logging.debug("updateConnStatus(): instantiated")
        #format: [(username, connName): {"user_status": user_perm, "connStatus": active}]
        for cell in range(0,self.vmStatusTable.rowCount()):
            tableConnName = self.vmStatusTable.item(cell, 0).text()
            tableUserName = self.vmStatusTable.item(cell, 1).text()
            userStatusCellItem = self.vmStatusTable.item(cell, 2)
            connStatusCellItem = self.vmStatusTable.item(cell, 3)
            userStatus = "not_found"
            connStatus = "not_found"
            if (tableUserName, tableConnName) in usersConnsStatus:
                if "user_status" in usersConnsStatus[(tableUserName, tableConnName)] and usersConnsStatus[(tableUserName, tableConnName)]["user_status"] != None:
                    userStatus = usersConnsStatus[(tableUserName, tableConnName)]["user_status"]
                if "connStatus" in usersConnsStatus[(tableUserName, tableConnName)] and usersConnsStatus[(tableUserName, tableConnName)]["connStatus"] != None:
                    connStatus = usersConnsStatus[(tableUserName, tableConnName)]["connStatus"]
            userStatusCellItem.setText(userStatus)
            connStatusCellItem.setText(connStatus)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = ConnectionStatusWidget()
    ui.show()
    sys.exit(app.exec_())
