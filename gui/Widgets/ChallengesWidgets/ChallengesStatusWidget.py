from gui.Helpers.ChallengesActions import ChallengesActions
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

class ChallengesStatusWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, configname=None, widgetname="", rolledoutjson=None, interest_vmnames = [], vmuser_mapping={}, status_bar=None):
        logging.debug("ChallengesStatusWidget instantiated")
        if configname == None:
            logging.error("configname cannot be empty")
            return None
        QtWidgets.QWidget.__init__(self, parent=None)
        self.parent = parent
        self.statusBar = status_bar
        self.widgetname = widgetname
        self.configname = configname
        self.rolledoutjson = rolledoutjson
        self.eco = ExperimentConfigIO.getInstance()

        self.setWindowTitle("ChallengesStatusWidget")
        self.setObjectName("ChallengesStatusWidget")
        self.layoutWidget = QtWidgets.QWidget()
        self.layoutWidget.setObjectName("layoutWidget")
        self.outerVertBox = QtWidgets.QVBoxLayout()
        self.outerVertBox.setObjectName("outerVertBox")
        self.layoutWidget.setLayout(self.outerVertBox)

        self.challengeStatusTable = QtWidgets.QTableWidget(parent)
        self.challengeStatusTable.setObjectName("challengeStatusTable")
        self.challengeStatusTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.challengeStatusTable.setSelectionBehavior(QTableView.SelectRows)
        self.challengeStatusTable.setSelectionMode(QTableView.SingleSelection)
        
        self.challengeStatusTable.setRowCount(0)
        self.challengeStatusTable.setColumnCount(8)
        self.challengeStatusTable.setHorizontalHeaderLabels(("VM Name", "Generated User", "Generated Pass", "Connection Status", "Team Name", "Rank", "Score Indiv", "Score Team"))

        # Context menus
        self.challengeStatusTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.challengeStatusTable.customContextMenuRequested.connect(self.showContextMenu)
        self.challengesContextMenu = QtWidgets.QMenu()
        self.createGuac = self.challengesContextMenu.addAction("Create Users")
        self.createGuac.triggered.connect(self.menuItemSelected)
        self.removeGuac = self.challengesContextMenu.addAction("Remove Users")
        self.removeGuac.triggered.connect(self.menuItemSelected)
        self.clearGuac = self.challengesContextMenu.addAction("Clear All Entries")
        self.clearGuac.triggered.connect(self.menuItemSelected)
        self.openGuac = self.challengesContextMenu.addAction("Open User Stats")
        self.openGuac.triggered.connect(self.menuItemSelected)

        self.challengeStatusTable.setSortingEnabled(True)
        self.outerVertBox.addWidget(self.challengeStatusTable)

        self.setLayout(self.outerVertBox)
        self.retranslateUi(rolledoutjson, interest_vmnames, vmuser_mapping)

    def retranslateUi(self, rolledoutjson, interest_vmnames, vmuser_mapping):
        logging.debug("ChallengesStatusWidget: retranslateUi(): instantiated")
        user_num = 1
        if rolledoutjson == None:
            return
        (template_vms, num_clones) = rolledoutjson
        for template_vm in template_vms:
            for cloned_vm in template_vms[template_vm]:
                if interest_vmnames == [] or cloned_vm["name"] in interest_vmnames:
                    rowPos = self.challengeStatusTable.rowCount()
                    self.challengeStatusTable.insertRow(rowPos)
                    vmName = str(cloned_vm["name"])
                    vmCell = QTableWidgetItem(vmName)
                    connStatusCell = QTableWidgetItem(str("refresh req."))
                    teamCell = QTableWidgetItem(str("refresh req."))
                    rankCell = QTableWidgetItem(str("refresh req."))
                    scoreIndivCell = QTableWidgetItem(str("refresh req."))
                    scoreTeamCell = QTableWidgetItem(str("refresh req."))
                    username = "vrdp disabled"
                    password = "vrdp disabled"
                    if vmuser_mapping != {} and vmName in vmuser_mapping:
                        if vmuser_mapping[vmName] == "userfile_not_found":
                            (username, password) = ("userfile_not_found"+str(user_num), "userfile_not_found"+str(user_num))
                            user_num+=1
                        else:
                            (username, password) = vmuser_mapping[vmName]
                    usernameCell = QTableWidgetItem(username)
                    passwordCell = QTableWidgetItem(password)
                    userStatusCell = QTableWidgetItem(str("refresh req."))
                    # statusCell.setFlags(Qt.ItemIsEnabled)
                    self.challengeStatusTable.setItem(rowPos, 0, vmCell)
                    self.challengeStatusTable.setItem(rowPos, 1, usernameCell)
                    self.challengeStatusTable.setItem(rowPos, 2, passwordCell)
                    self.challengeStatusTable.setItem(rowPos, 3, userStatusCell)
                    self.challengeStatusTable.setItem(rowPos, 4, connStatusCell)
                    self.challengeStatusTable.setItem(rowPos, 5, teamCell)
                    self.challengeStatusTable.setItem(rowPos, 6, rankCell)
                    self.challengeStatusTable.setItem(rowPos, 7, scoreIndivCell)
                    self.challengeStatusTable.setItem(rowPos, 8, scoreTeamCell)
                    self.challengeStatusTable.resizeColumnToContents(0)

    def showContextMenu(self, position):
        logging.debug("showContextMenu() instantiated")
        self.challengesContextMenu.popup(self.challengeStatusTable.mapToGlobal(position))

    def menuItemSelected(self):
        logging.debug("menuItemSelected(): instantiated")
        challengeRow = self.challengeStatusTable.currentRow()
        if challengeRow == None:
            logging.error("menuItemSelected(): No Row is Selected.")
            return
        challengeName = self.challengeStatusTable.item(challengeRow,0).text()
        actionlabelname = self.sender().text()
        vmserverip, rdpbroker, chatserver, challengesserver, users_file = self.eco.getExperimentServerInfo(self.configname)
        #parent, configname, actionlabelname, vmHostname, rdpBrokerHostname, users_file="", itype="", name=""
        ChallengesActions().challengesActionEvent(self.parent, self.configname, actionlabelname, challengesserver, users_file, "vm", challengeName)
        self.statusBar.showMessage("Executed " + str(actionlabelname) + " on " + self.configname)

    def updateConnStatus(self, usersConnsStatus):
        logging.debug("updateConnStatus(): instantiated")
        #format: [(username, challengeName): {"user_status": user_perm, "connStatus": active}]
        for cell in range(0,self.challengeStatusTable.rowCount()):
            tableConnName = self.challengeStatusTable.item(cell, 0).text()
            tableUserName = self.challengeStatusTable.item(cell, 1).text()
            userStatusCellItem = self.challengeStatusTable.item(cell, 3)
            connStatusCellItem = self.challengeStatusTable.item(cell, 4)
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
    ui = ChallengesStatusWidget()
    ui.show()
    sys.exit(app.exec_())
