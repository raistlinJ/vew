from engine.Configuration.SystemConfigIO import SystemConfigIO
from gui.Dialogs.ChallengesStatsRetrieveDialog import ChallengesStatsRetrieveDialog
from gui.Dialogs.ChallengesOpeningDialog import ChallengesOpeningDialog
from gui.Dialogs.ChallengesRetrievingDialog import ChallengesRetrievingDialog
from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

from engine.Engine import Engine
from engine.Manager.ChallengesManage.ChallengesManage import ChallengesManage
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from gui.Dialogs.ChallengesActioningDialog import ChallengesActioningDialog
import logging
from engine.Configuration.UserPool import UserPool

class ChallengesActionDialog(QDialog):

    def __init__(self, parent, configname, actionname, challengesServerHostname="<unspecified>", users_file="", itype="", name=""):
        logging.debug("ChallengesActionDialog(): instantiated")
        super(ChallengesActionDialog, self).__init__(parent)
        self.parent = parent
        self.eco = ExperimentConfigIO.getInstance()
        self.s = SystemConfigIO()
        self.configname = configname
        self.actionname = actionname
        self.usersFile = users_file
        self.itype = itype
        self.name = name
        if challengesServerHostname.strip() == "":
            self.challengesServerHostname = "<unspecified>"
            self.setEnabled(False)
        else:
            self.challengesServerHostname = challengesServerHostname
        self.cm = ChallengesManage()
        self.setMinimumWidth(450)

        self.createFormGroupBox()
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        
        self.setWindowTitle(str(actionname) + " Challenges")
        
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Challenges Information")
        self.layout = QFormLayout()
        self.hostnameLineEdit = QLineEdit(self.challengesServerHostname)
        self.hostnameLineEdit.setEnabled(False)
        self.layout.addRow(QLabel("Challenge Server Hostname/IP:"), self.hostnameLineEdit)
        mgmusername = ""
        mgmpassword = ""
        method = "HTTPS"
        cachedCreds = self.eco.getConfigChallengeSysCreds(self.configname)
        if cachedCreds != None:
            mgmusername = cachedCreds[0]
            mgmpassword = cachedCreds[1]
            method = cachedCreds[2]
        self.usernameLineEdit = QLineEdit(mgmusername)
        self.passwordLineEdit = QLineEdit(mgmpassword)
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        if self.actionname != "Open":
            self.layout.addRow(QLabel("Management Username:"), self.usernameLineEdit)
            self.layout.addRow(QLabel("Management Password:"), self.passwordLineEdit)

        self.methodComboBox = QComboBox()
        self.methodComboBox.addItem("HTTP")
        self.methodComboBox.addItem("HTTPS")
        if method == "HTTP":
            self.methodComboBox.setCurrentIndex(0)
        else:
            self.methodComboBox.setCurrentIndex(1)
        self.layout.addRow(QLabel("Method:"), self.methodComboBox)
        
        self.usersFileLabel = QLineEdit(self.usersFile)
        self.usersFileLabel.setEnabled(False)
        if self.actionname == "Add":
            #Need to make a function to create more than one user to a single instance 
            self.layout.addRow(QLabel("Users File: "), self.usersFileLabel)
        if self.actionname == "Remove":
            self.layout.addRow(QLabel("Users File: "), self.usersFileLabel)
        self.formGroupBox.setLayout(self.layout)

    def exec_(self):
        logging.debug("ChallengesActionDialog(): exec_() instantiated")
        result = super(ChallengesActionDialog, self).exec_()
        if str(result) == str(1):
            logging.debug("dialog_response(): OK was pressed")
            if self.actionname == "Add":
                self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.methodComboBox.currentText(), self.usersFileLabel.text(), self.itype, self.name]
            elif self.actionname == "Remove":
                self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.methodComboBox.currentText(), self.usersFileLabel.text(), self.itype, self.name]
            elif self.actionname == "Clear":
                self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.methodComboBox.currentText()]
            elif self.actionname == "Refresh":
                self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.methodComboBox.currentText()]
            elif self.actionname == "OpenUsers":
                #get all of the challenges from the currently selected item
                userpool = UserPool()
                usersConns = userpool.generateUsersConns(self.configname, creds_file=self.usersFile)
                vmuser_mapping = {}
                for (username, password) in usersConns:
                    for conn in usersConns[(username, password)]:
                        cloneVMName = conn[0]
                        vmuser_mapping[cloneVMName] = (username, password)
                #get all vms based on what's selected
                tentativeVMs = self.eco.getValidVMsFromTypeName(self.configname, self.itype, self.name)
                #get user/password from selected vms and store those in the list of users to open
                usersToOpen = {}
                for vm in tentativeVMs:
                    if vm in vmuser_mapping:
                        usersToOpen[vmuser_mapping[vm]] = True
                logging.debug(str(usersToOpen))
            elif self.actionname == "ViewChallStats":
                self.args = [self.hostnameLineEdit.text(), self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.methodComboBox.currentText()]
            else:
                pass
            if self.actionname == "Refresh":
                self.eco.storeConfigChallengeSysCreds(self.configname, self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.methodComboBox.currentText())
                crd = ChallengesRetrievingDialog(self.parent, self.args).exec_()
                return crd
            elif self.actionname == "OpenUsers":
                self.eco.storeConfigChallengeSysCreds(self.configname, self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.methodComboBox.currentText())
                pathToBrowser = self.s.getConfig()["BROWSER"]["BROWSER_PATH"]
                browserArgs = self.s.getConfig()["BROWSER"]["ARGS"]
                url = self.challengesServerHostname + "/admin/users/"+str(username)
                cod = ChallengesOpeningDialog(self.parent, pathToBrowser, browserArgs, usersToOpen, url, self.methodComboBox.currentText()).exec_()
                return cod
            elif self.actionname == "ViewChallStats":
                self.eco.storeConfigChallengeSysCreds(self.configname, self.usernameLineEdit.text(), self.passwordLineEdit.text(), self.methodComboBox.currentText())
                                #Here open the dialog to show all challenges stats
                #QMessageBox(QMessageBox.Information, "Challenges Stats", "Challenges Stats", QMessageBox.Ok).exec_()
                csr = ChallengesStatsRetrieveDialog(self.parent, self.args).exec_()
            else:
                cad = ChallengesActioningDialog(self.parent, self.configname, self.actionname, self.args).exec_()
                #Open dialog here showing all challenges stats
                return (QMessageBox.Ok)
        return (QMessageBox.Cancel)