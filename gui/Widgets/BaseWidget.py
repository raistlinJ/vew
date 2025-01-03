from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import logging

class BaseWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, configname=None, widgetname="", basejsondata=None):
        logging.debug("BaseWidget instantiated")
        if configname == None:
            logging.error("configname cannot be empty")
            return None
        QtWidgets.QWidget.__init__(self, parent=None)
        self.widgetname = widgetname
        self.configname = configname
        
        self.setWindowTitle("BaseWidget")
        self.setObjectName("BaseWidget")
        self.layoutWidget = QtWidgets.QWidget()
        self.layoutWidget.setObjectName("layoutWidget")
        self.outerVertBox = QtWidgets.QVBoxLayout()
        self.outerVertBox.setObjectName("outerVertBox")
        self.layoutWidget.setLayout(self.outerVertBox)

        self.vBoxManageHorBox = QtWidgets.QHBoxLayout()
        self.vBoxManageHorBox.setObjectName("vBoxManageHorBox")
        self.vBoxManageLabel = QtWidgets.QLabel()
        self.vBoxManageLabel.setObjectName("vBoxManageLabel")
        self.vBoxManageLabel.setText("Path to VBox Manager:")
        self.vBoxManageHorBox.addWidget(self.vBoxManageLabel)

        self.chooseVBoxPathButton = QtWidgets.QToolButton()
        self.chooseVBoxPathButton.setObjectName("chooseVBoxPathButton")
        self.chooseVBoxPathButton.setText("...")
        self.vBoxManageHorBox.addWidget(self.chooseVBoxPathButton)

        self.vBoxMangeLineEdit = QtWidgets.QLineEdit()
        self.vBoxMangeLineEdit.setObjectName("vBoxMangeLineEdit")
        self.vBoxManageHorBox.addWidget(self.vBoxMangeLineEdit)
        #self.outerVertBox.addLayout(self.vBoxManageHorBox)

        self.vmServerIPHorBox = QtWidgets.QHBoxLayout()
        self.vmServerIPHorBox.setObjectName("vmServerIPHorBox")
        self.vmServerIPLabel = QtWidgets.QLabel()
        self.vmServerIPLabel.setObjectName("vmServerIPLabel")
        self.vmServerIPLabel.setText("VM Server IP:")
        self.vmServerIPHorBox.addWidget(self.vmServerIPLabel)
        self.vmServerIPLineEdit = QtWidgets.QLineEdit() 
        self.vmServerIPLineEdit.setObjectName("vmServerIPLineEdit")
        self.vmServerIPHorBox.addWidget(self.vmServerIPLineEdit)
        self.outerVertBox.addLayout(self.vmServerIPHorBox)

        self.rdpBrokerHorBox = QtWidgets.QHBoxLayout()
        self.rdpBrokerHorBox.setObjectName("rdpBrokerHorBox")
        self.rdpBrokerLabel = QtWidgets.QLabel()
        self.rdpBrokerLabel.setObjectName("rdpBrokerLabel")
        self.rdpBrokerLabel.setText("RDP Broker Address:")
        self.rdpBrokerHorBox.addWidget(self.rdpBrokerLabel)
        self.rdpBrokerLineEdit = QtWidgets.QLineEdit() 
        self.rdpBrokerLineEdit.setObjectName("rdpBrokerLineEdit")
        self.rdpBrokerHorBox.addWidget(self.rdpBrokerLineEdit)
        self.outerVertBox.addLayout(self.rdpBrokerHorBox)

        self.chatServerHorBox = QtWidgets.QHBoxLayout()
        self.chatServerHorBox.setObjectName("chatServerHorBox")
        self.chatServerLabel = QtWidgets.QLabel()
        self.chatServerLabel.setObjectName("chatServerLabel")
        self.chatServerLabel.setText("Chat Server Address:")
        self.chatServerHorBox.addWidget(self.chatServerLabel)
        self.chatServerLineEdit = QtWidgets.QLineEdit() 
        self.chatServerLineEdit.setObjectName("chatServerLineEdit")
        self.chatServerHorBox.addWidget(self.chatServerLineEdit)
        self.outerVertBox.addLayout(self.chatServerHorBox)

        self.baseGroupNameHorBox = QtWidgets.QHBoxLayout()
        self.baseGroupNameHorBox.setObjectName("baseGroupNameHorBox")
        self.baseGroupNameLabel = QtWidgets.QLabel()
        self.baseGroupNameLabel.setObjectName("baseGroupNameLabel")
        self.baseGroupNameLabel.setText("Base Group Name:")

        self.baseGroupNameHorBox.addWidget(self.baseGroupNameLabel)
        self.baseGroupNameLineEdit = QtWidgets.QLineEdit()

        # self.baseGroupNameLineEdit.setReadOnly(True)
        self.baseGroupNameLineEdit.setObjectName("baseGroupNameLineEdit")
        self.baseGroupNameHorBox.addWidget(self.baseGroupNameLineEdit)
        self.outerVertBox.addLayout(self.baseGroupNameHorBox)

        self.numClonesHorBox = QtWidgets.QHBoxLayout()
        self.numClonesHorBox.setObjectName("numClonesHorBox")
        self.numClonesLabel = QtWidgets.QLabel()
        self.numClonesLabel.setObjectName("numClonesLabel")
        self.numClonesLabel.setText("Number of Clones:")
        self.numClonesHorBox.addWidget(self.numClonesLabel)

        self.numClonesEntry = QtWidgets.QSpinBox()
        self.numClonesEntry.setRange(1, 50)
        self.numClonesHorBox.addWidget(self.numClonesEntry)
        self.outerVertBox.addLayout(self.numClonesHorBox)

        self.linkedClonesHorBox = QtWidgets.QHBoxLayout()
        self.linkedClonesHorBox.setObjectName("linkedClonesHorBox")
        self.linkedClonesLabel = QtWidgets.QLabel()
        self.linkedClonesLabel.setObjectName("linkedClonesLabel")
        self.linkedClonesLabel.setText("Linked Clones:")
        self.linkedClonesHorBox.addWidget(self.linkedClonesLabel)

        self.linkedClonesComboBox = QtWidgets.QComboBox()
        self.linkedClonesComboBox.setObjectName("linkedClonesComboBox")
        self.linkedClonesComboBox.addItem("true")
        self.linkedClonesComboBox.addItem("false")     
        self.linkedClonesHorBox.addWidget(self.linkedClonesComboBox)
        self.outerVertBox.addLayout(self.linkedClonesHorBox)

        self.cloneSnapshotsHorBox = QtWidgets.QHBoxLayout()
        self.cloneSnapshotsHorBox.setObjectName("cloneSnapshotsHorBox")
        self.cloneSnapshotsLabel = QtWidgets.QLabel()
        self.cloneSnapshotsLabel.setObjectName("cloneSnapshotsLabel")
        self.cloneSnapshotsLabel.setText("Clone Snapshots:")
        self.cloneSnapshotsHorBox.addWidget(self.cloneSnapshotsLabel)

        self.cloneSnapshotComboBox = QtWidgets.QComboBox()
        self.cloneSnapshotComboBox.setObjectName("cloneSnapshotComboBox")
        self.cloneSnapshotComboBox.addItem("true")
        self.cloneSnapshotComboBox.addItem("false")
        self.cloneSnapshotsHorBox.addWidget(self.cloneSnapshotComboBox)
        self.outerVertBox.addLayout(self.cloneSnapshotsHorBox)

        self.baseOutnameHorBox = QtWidgets.QHBoxLayout()
        self.baseOutnameHorBox.setObjectName("baseOutnameHorBox")
        self.baseOutnameLabel = QtWidgets.QLabel()
        self.baseOutnameLabel.setObjectName("baseOutnameLabel")
        self.baseOutnameLabel.setText("Base Outname:")
        self.baseOutnameHorBox.addWidget(self.baseOutnameLabel)

        self.baseOutnameLineEdit = QtWidgets.QLineEdit()
        self.baseOutnameLineEdit.setObjectName("baseOutnameLineEdit")
        self.baseOutnameHorBox.addWidget(self.baseOutnameLineEdit)
        self.outerVertBox.addLayout(self.baseOutnameHorBox)

        self.vrdpBaseportHorBox = QtWidgets.QHBoxLayout()
        self.vrdpBaseportHorBox.setObjectName("vrdpBaseportHorBox")
        self.vrdpBaseportLabel = QtWidgets.QLabel()
        self.vrdpBaseportLabel.setObjectName("vrdpBaseportLabel")
        self.vrdpBaseportLabel.setText("VRDP Baseport:")
        self.vrdpBaseportHorBox.addWidget(self.vrdpBaseportLabel)

        self.vrdpBaseportLineEdit = QtWidgets.QLineEdit()
        self.vrdpBaseportLineEdit.setObjectName("vrdpBaseportLineEdit")
        self.vrdpBaseportHorBox.addWidget(self.vrdpBaseportLineEdit)
        self.outerVertBox.addLayout(self.vrdpBaseportHorBox)

        self.usersFilenameHorBox = QtWidgets.QHBoxLayout()
        self.usersFilenameHorBox.setObjectName("usersFilenameHorBox")
        self.usersFilenameLabel = QtWidgets.QLabel()
        self.usersFilenameLabel.setObjectName("usersFilenameLabel")
        self.usersFilenameLabel.setText("Users Filename:")
        self.usersFilenameHorBox.addWidget(self.usersFilenameLabel)

        self.usersFilenameLineEdit = QtWidgets.QLineEdit()
        self.usersFilenameLineEdit.setObjectName("usersFilenameLineEdit")
        self.usersFilenameLineEdit.setText("<unspecified>")
        self.usersFilenameHorBox.addWidget(self.usersFilenameLineEdit)

        self.usersFilenamePushButton = QtWidgets.QPushButton("...")
        self.usersFilenamePushButton.setObjectName("usersFilenamePushButton")
        self.usersFilenamePushButton.clicked.connect(self.getUsersFilename)
        self.usersFilenameHorBox.addWidget(self.usersFilenamePushButton)
        self.outerVertBox.addLayout(self.usersFilenameHorBox)

        self.paddingWidget1 = QtWidgets.QWidget()
        self.paddingWidget1.setObjectName("paddingWidget1")
        self.outerVertBox.addWidget(self.paddingWidget1)
        self.paddingWidget2 = QtWidgets.QWidget()
        self.paddingWidget2.setObjectName("paddingWidget2")
        self.outerVertBox.addWidget(self.paddingWidget2)
        self.paddingWidget3 = QtWidgets.QWidget()
        self.paddingWidget3.setObjectName("paddingWidget3")
        self.outerVertBox.addWidget(self.paddingWidget3)

        self.setLayout(self.outerVertBox)
        self.retranslateUi(basejsondata)

    def retranslateUi(self, basejsondata):
        logging.debug("BaseWidget: retranslateUi(): instantiated")

        ###Fill in data from json
        if basejsondata == None:
            basejsondata = {}
        if "testbed-setup" not in basejsondata:
            basejsondata["testbed-setup"] = {}
        if "network-config" not in basejsondata["testbed-setup"]:
            basejsondata["testbed-setup"]["network-config"] = {}
        if "vm-set" not in basejsondata["testbed-setup"]:
            basejsondata["testbed-setup"]["vm-set"] = {}

        if "vm-server-ip" not in basejsondata["testbed-setup"]["network-config"]:
            basejsondata["testbed-setup"]["network-config"]["vm-server-ip"] = "11.0.0.2"
        self.vmServerIPLineEdit.setText(basejsondata["testbed-setup"]["network-config"]["vm-server-ip"])
        ###
        if "rdp-broker-ip" not in basejsondata["testbed-setup"]["network-config"]:
            basejsondata["testbed-setup"]["network-config"]["rdp-broker-ip"] = ""
        self.rdpBrokerLineEdit.setText(basejsondata["testbed-setup"]["network-config"]["rdp-broker-ip"])
        ###
        if "chat-server-ip" not in basejsondata["testbed-setup"]["network-config"]:
            basejsondata["testbed-setup"]["network-config"]["chat-server-ip"] = ""
        self.chatServerLineEdit.setText(basejsondata["testbed-setup"]["network-config"]["chat-server-ip"])
        ###
        if "base-groupname" not in basejsondata["testbed-setup"]["vm-set"]:
            basejsondata["testbed-setup"]["vm-set"]["base-groupname"] = self.configname
        self.baseGroupNameLineEdit.setText(basejsondata["testbed-setup"]["vm-set"]["base-groupname"])
        ###
        if "num-clones" not in basejsondata["testbed-setup"]["vm-set"]:
            basejsondata["testbed-setup"]["vm-set"]["num-clones"] = str(5)
        self.numClonesEntry.setValue(int(basejsondata["testbed-setup"]["vm-set"]["num-clones"]))
        ###
        if "linked-clones" not in basejsondata["testbed-setup"]["vm-set"]:
            basejsondata["testbed-setup"]["vm-set"]["linked-clones"] = "true"
        self.linkedClonesComboBox.setCurrentIndex(self.linkedClonesComboBox.findText(basejsondata["testbed-setup"]["vm-set"]["linked-clones"]))
        ###
        if "clone-snapshots" not in basejsondata["testbed-setup"]["vm-set"]:
            basejsondata["testbed-setup"]["vm-set"]["clone-snapshots"] = "true"
        self.cloneSnapshotComboBox.setCurrentIndex(self.cloneSnapshotComboBox.findText(basejsondata["testbed-setup"]["vm-set"]["clone-snapshots"]))
        ###
        if "base-outname" not in basejsondata["testbed-setup"]["vm-set"]:
            basejsondata["testbed-setup"]["vm-set"]["base-outname"] = "_set_"
        self.baseOutnameLineEdit.setText(basejsondata["testbed-setup"]["vm-set"]["base-outname"])
        ###
        if "vrdp-baseport" not in basejsondata["testbed-setup"]["vm-set"]:
            basejsondata["testbed-setup"]["vm-set"]["vrdp-baseport"] = "1001"
        self.vrdpBaseportLineEdit.setText(basejsondata["testbed-setup"]["vm-set"]["vrdp-baseport"])
        ###
        if "users-filename" not in basejsondata["testbed-setup"]["vm-set"]:
            basejsondata["testbed-setup"]["vm-set"]["users-filename"] = "<unspecified>"
        self.usersFilenameLineEdit.setText(basejsondata["testbed-setup"]["vm-set"]["users-filename"])

    def getWritableData(self):
        logging.debug("BaseWidget: getWritableData(): instantiated")
        #build JSON from text entry fields
        jsondata = {}
        jsondata["testbed-setup"] = {}
        jsondata["testbed-setup"]["network-config"] = {}
        jsondata["testbed-setup"]["network-config"]["vm-server-ip"] = self.vmServerIPLineEdit.text()
        jsondata["testbed-setup"]["network-config"]["rdp-broker-ip"] = self.rdpBrokerLineEdit.text()
        jsondata["testbed-setup"]["network-config"]["chat-server-ip"] = self.rdpBrokerLineEdit.text()
        jsondata["testbed-setup"]["vm-set"] = {}
        jsondata["testbed-setup"]["vm-set"]["base-groupname"] = self.baseGroupNameLineEdit.text()
        jsondata["testbed-setup"]["vm-set"]["num-clones"] = str(self.numClonesEntry.value())
        jsondata["testbed-setup"]["vm-set"]["linked-clones"] = self.linkedClonesComboBox.currentText()
        jsondata["testbed-setup"]["vm-set"]["clone-snapshots"] = self.cloneSnapshotComboBox.currentText()
        jsondata["testbed-setup"]["vm-set"]["base-outname"] = self.baseOutnameLineEdit.text()
        jsondata["testbed-setup"]["vm-set"]["vrdp-baseport"] = self.vrdpBaseportLineEdit.text()
        jsondata["testbed-setup"]["vm-set"]["users-filename"] = str(self.usersFilenameLineEdit.text())
        return jsondata

    def getUsersFilename(self):
        logging.debug("BaseWidget: getUsersFilename(): instantiated")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select Users File", "","All Files (*);;Creds Files (*.csv)", options=options)
        if fileName:
            self.usersFilenameLineEdit.setText(fileName)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = BaseWidget()
    ui.show()
    sys.exit(app.exec_())
