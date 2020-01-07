from PyQt5 import QtCore, QtGui, QtWidgets
import logging

class BaseWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, basejsondata=None):
        QtWidgets.QWidget.__init__(self, parent=None)

        self.setObjectName("BaseWidget")
        self.resize(444, 387)
        self.layoutWidget = QtWidgets.QWidget(parent)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 10, 445, 372))
        self.layoutWidget.setObjectName("layoutWidget")
        self.outerVertBox = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.outerVertBox.setContentsMargins(0, 0, 0, 0)
        self.outerVertBox.setObjectName("outerVertBox")
        self.vBoxManageHorBox = QtWidgets.QHBoxLayout()
        self.vBoxManageHorBox.setObjectName("vBoxManageHorBox")
        self.vBoxManageLabel = QtWidgets.QLabel(self.layoutWidget)
        self.vBoxManageLabel.setObjectName("vBoxManageLabel")
        self.vBoxManageLabel.setText("Path to VBox Manager:")
        self.vBoxManageHorBox.addWidget(self.vBoxManageLabel)
        self.chooseVBoxPathButton = QtWidgets.QToolButton(self.layoutWidget)
        self.chooseVBoxPathButton.setObjectName("chooseVBoxPathButton")
        self.chooseVBoxPathButton.setText("...")

        self.vBoxManageHorBox.addWidget(self.chooseVBoxPathButton)
        self.vBoxMangeLineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.vBoxMangeLineEdit.setObjectName("vBoxMangeLineEdit")

        self.vBoxManageHorBox.addWidget(self.vBoxMangeLineEdit)
        self.outerVertBox.addLayout(self.vBoxManageHorBox)
        self.ipAddressHorBox = QtWidgets.QHBoxLayout()
        self.ipAddressHorBox.setObjectName("ipAddressHorBox")
        self.ipAddressLabel = QtWidgets.QLabel(self.layoutWidget)
        self.ipAddressLabel.setObjectName("ipAddressLabel")
        self.ipAddressLabel.setText("IP Address:")

        self.ipAddressHorBox.addWidget(self.ipAddressLabel)
        self.ipAddressLineEdit = QtWidgets.QLineEdit(self.layoutWidget)

        self.ipAddressLineEdit.setObjectName("ipAddressLineEdit")
        self.ipAddressHorBox.addWidget(self.ipAddressLineEdit)
        self.outerVertBox.addLayout(self.ipAddressHorBox)
        self.baseGroupNameHorBox = QtWidgets.QHBoxLayout()
        self.baseGroupNameHorBox.setObjectName("baseGroupNameHorBox")
        self.baseGroupNameLabel = QtWidgets.QLabel(self.layoutWidget)
        self.baseGroupNameLabel.setObjectName("baseGroupNameLabel")
        self.baseGroupNameLabel.setText("Base Group Name:")

        self.baseGroupNameHorBox.addWidget(self.baseGroupNameLabel)
        self.baseGroupNameLineEdit = QtWidgets.QLineEdit(self.layoutWidget)

        # self.baseGroupNameLineEdit.setReadOnly(True)
        self.baseGroupNameLineEdit.setObjectName("baseGroupNameLineEdit")
        self.baseGroupNameHorBox.addWidget(self.baseGroupNameLineEdit)
        self.outerVertBox.addLayout(self.baseGroupNameHorBox)
        self.numClonesHorBox = QtWidgets.QHBoxLayout()
        self.numClonesHorBox.setObjectName("numClonesHorBox")
        self.numClonesLabel = QtWidgets.QLabel(self.layoutWidget)
        self.numClonesLabel.setObjectName("numClonesLabel")
        self.numClonesLabel.setText("Number of Clones:")
        self.numClonesHorBox.addWidget(self.numClonesLabel)
        self.numClonesEntry = QtWidgets.QSpinBox()
        self.numClonesEntry.setRange(1, 50)

        self.numClonesHorBox.addWidget(self.numClonesEntry)
        self.outerVertBox.addLayout(self.numClonesHorBox)
        self.linkedClonesHorBox = QtWidgets.QHBoxLayout()
        self.linkedClonesHorBox.setObjectName("linkedClonesHorBox")
        self.linkedClonesLabel = QtWidgets.QLabel(self.layoutWidget)
        self.linkedClonesLabel.setObjectName("linkedClonesLabel")
        self.linkedClonesLabel.setText("Linked Clones:")

        self.linkedClonesHorBox.addWidget(self.linkedClonesLabel)
        self.linkedClonesComboBox = QtWidgets.QComboBox(self.layoutWidget)
        self.linkedClonesComboBox.setObjectName("linkedClonesComboBox")

        self.linkedClonesComboBox.addItem("true")
        self.linkedClonesComboBox.addItem("false")
        
        self.linkedClonesHorBox.addWidget(self.linkedClonesComboBox)
        self.outerVertBox.addLayout(self.linkedClonesHorBox)
        self.cloneSnapshotsHorBox = QtWidgets.QHBoxLayout()
        self.cloneSnapshotsHorBox.setObjectName("cloneSnapshotsHorBox")
        self.cloneSnapshotsLabel = QtWidgets.QLabel(self.layoutWidget)
        self.cloneSnapshotsLabel.setObjectName("cloneSnapshotsLabel")
        self.cloneSnapshotsLabel.setText("Clone Snapshots:")
        self.cloneSnapshotsHorBox.addWidget(self.cloneSnapshotsLabel)
        self.cloneSnapshotComboBox = QtWidgets.QComboBox(self.layoutWidget)
        self.cloneSnapshotComboBox.setObjectName("cloneSnapshotComboBox")

        self.cloneSnapshotComboBox.addItem("true")
        self.cloneSnapshotComboBox.addItem("false")
        self.cloneSnapshotsHorBox.addWidget(self.cloneSnapshotComboBox)
        self.outerVertBox.addLayout(self.cloneSnapshotsHorBox)
        self.baseOutnameHorBox = QtWidgets.QHBoxLayout()
        self.baseOutnameHorBox.setObjectName("baseOutnameHorBox")
        self.baseOutnameLabel = QtWidgets.QLabel(self.layoutWidget)
        self.baseOutnameLabel.setObjectName("baseOutnameLabel")
        self.baseOutnameLabel.setText("Base Outname:")
        self.baseOutnameHorBox.addWidget(self.baseOutnameLabel)
        self.baseOutnameLineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.baseOutnameLineEdit.setObjectName("baseOutnameLineEdit")

        self.baseOutnameHorBox.addWidget(self.baseOutnameLineEdit)
        self.outerVertBox.addLayout(self.baseOutnameHorBox)
        self.vrdpBaseportHorBox = QtWidgets.QHBoxLayout()
        self.vrdpBaseportHorBox.setObjectName("vrdpBaseportHorBox")
        self.vrdpBaseportLabel = QtWidgets.QLabel(self.layoutWidget)
        self.vrdpBaseportLabel.setObjectName("vrdpBaseportLabel")
        self.vrdpBaseportLabel.setText("VRDP Baseport:")
        self.vrdpBaseportHorBox.addWidget(self.vrdpBaseportLabel)
        self.vrdpBaseportLineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.vrdpBaseportLineEdit.setObjectName("vrdpBaseportLineEdit")

        self.vrdpBaseportHorBox.addWidget(self.vrdpBaseportLineEdit)
        self.outerVertBox.addLayout(self.vrdpBaseportHorBox)

        self.paddingWidget1 = QtWidgets.QWidget(self.layoutWidget)
        self.paddingWidget1.setObjectName("paddingWidget1")
        self.outerVertBox.addWidget(self.paddingWidget1)
        self.paddingWidget2 = QtWidgets.QWidget(self.layoutWidget)
        self.paddingWidget2.setObjectName("paddingWidget2")
        self.outerVertBox.addWidget(self.paddingWidget2)
        self.paddingWidget3 = QtWidgets.QWidget(self.layoutWidget)
        self.paddingWidget3.setObjectName("paddingWidget3")
        self.outerVertBox.addWidget(self.paddingWidget3)

        self.setLayout(self.outerVertBox)
        self.retranslateUi(basejsondata)

    def retranslateUi(self, basejsondata):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle("BaseWidget")

        ###Fill in data from json
        self.vBoxMangeLineEdit.setText(basejsondata["vbox-setup"]["path-to-vboxmanage"])
        ###
        self.ipAddressLineEdit.setText(basejsondata["testbed-setup"]["network-config"]["ip-address"])
        ###
        self.baseGroupNameLineEdit.setText(basejsondata["testbed-setup"]["vm-set"]["base-groupname"])
        ###
        self.numClonesEntry.setValue(int(basejsondata["testbed-setup"]["vm-set"]["num-clones"]))
        ###
        self.linkedClonesComboBox.setCurrentIndex(self.linkedClonesComboBox.findText(basejsondata["testbed-setup"]["vm-set"]["linked-clones"]))
        ###
        self.cloneSnapshotComboBox.setCurrentIndex(self.cloneSnapshotComboBox.findText(basejsondata["testbed-setup"]["vm-set"]["clone-snapshots"]))
        ###
        self.baseOutnameLineEdit.setText(basejsondata["testbed-setup"]["vm-set"]["base-outname"])
        ###
        self.vrdpBaseportLineEdit.setText(basejsondata["testbed-setup"]["vm-set"]["vrdp-baseport"])

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = BaseWidget()
    ui.show()
    sys.exit(app.exec_())
