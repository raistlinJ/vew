from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtWidgets, uic
from gui.Widgets.NetworkAdaptorWidget import NetworkAdaptorWidget
import logging

class VMWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, vmjsondata=None):
        logging.debug("VMWidget instantiated")
        QtWidgets.QWidget.__init__(self, parent=None)
        self.setStyleSheet("QGroupBox { font-weight: bold; }")

        self.netAdaptors = {}

        self.setObjectName("VMWidget")
        self.layoutWidget = QtWidgets.QWidget(parent)
        self.layoutWidget.setObjectName("layoutWidget")

        self.outerVertBox = QtWidgets.QVBoxLayout()
        self.outerVertBox.setContentsMargins(0, 0, 0, 0)
        self.outerVertBox.setObjectName("outerVertBox")

        self.nameHLayout = QtWidgets.QHBoxLayout()
        self.nameHLayout.setObjectName("nameHLayout")
        self.nameLabel = QtWidgets.QLabel()
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Name:")
        self.nameHLayout.addWidget(self.nameLabel)

        self.nameLineEdit = QtWidgets.QLineEdit()
        self.nameLineEdit.setAcceptDrops(False)
        self.nameLineEdit.setReadOnly(True)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameHLayout.addWidget(self.nameLineEdit)
        self.outerVertBox.addLayout(self.nameHLayout)
        
        self.vrdpEnabledHorBox = QtWidgets.QHBoxLayout()
        self.vrdpEnabledHorBox.setObjectName("vrdpEnabledHorBox")
        self.vrdpEnabledLabel = QtWidgets.QLabel()
        self.vrdpEnabledLabel.setText("VRDP Enabled:")
        self.vrdpEnabledLabel.setObjectName("vrdpEnabledLabel")
        self.vrdpEnabledHorBox.addWidget(self.vrdpEnabledLabel)

        self.vrdpEnabledComboBox = QtWidgets.QComboBox()
        self.vrdpEnabledComboBox.setObjectName("vrdpEnabledComboBox")
        self.vrdpEnabledComboBox.addItem("false")
        self.vrdpEnabledComboBox.addItem("true")
        self.vrdpEnabledHorBox.addWidget(self.vrdpEnabledComboBox)
        self.outerVertBox.addLayout(self.vrdpEnabledHorBox)

        self.iNetGroupBox = QtWidgets.QGroupBox("Internal Network Adaptors")       
        self.iNetVertBox = QtWidgets.QVBoxLayout()
        self.iNetVertBox.setObjectName("iNetVertBox")
        self.iNetVertBox.setAlignment(QtCore.Qt.AlignTop)
        self.iNetGroupBox.setLayout(self.iNetVertBox)
        self.outerVertBox.addWidget(self.iNetGroupBox)
        
        self.addAdaptorButton = QtWidgets.QPushButton()
        self.addAdaptorButton.setObjectName("addAdaptorButton")
        self.addAdaptorButton.setText("Add Network Adaptor")
        self.addAdaptorButton.clicked.connect(self.buttonAddAdaptor)
        self.outerVertBox.addWidget(self.addAdaptorButton, alignment=QtCore.Qt.AlignHCenter)
        self.setLayout(self.outerVertBox)
        self.retranslateUi(vmjsondata)

    def retranslateUi(self, vmjsondata):
        logging.debug("VMWidget: retranslateUi(): instantiated")
        self.nameLineEdit.setText(vmjsondata["name"])
        self.vrdpEnabledComboBox.setCurrentIndex(self.vrdpEnabledComboBox.findText(vmjsondata["vrdp-enabled"]))

        ###Add Adaptors from File
        if "internalnet-basename" in vmjsondata:
            if isinstance(vmjsondata["internalnet-basename"], list):
                for adaptor in vmjsondata["internalnet-basename"]:
                    self.addAdaptor(adaptor)
            else:
                self.addAdaptor(vmjsondata["internalnet-basename"])

    def buttonAddAdaptor(self):
        logging.debug("VMWidget: buttonAddAdaptor(): instantiated")
        #This additional function is needed because otherwise the parameters sent by the button clicked signal mess things up
        self.addAdaptor()

    def addAdaptor(self, adaptorname="intnet", adaptortype="intnet"):
        logging.debug("VMWidget: addAdaptor(): instantiated: " + str(adaptorname) + " " + str(adaptortype))
        networkAdaptor = NetworkAdaptorWidget()
        networkAdaptor.lineEdit.setText(adaptorname)
        #self.iNetVertBox.addWidget(networkAdaptor, alignment=QtCore.Qt.AlignTop)
        self.iNetVertBox.addWidget(networkAdaptor)

        #need to keep track for easy removal later
        networkAdaptor.removeInetButton.clicked.connect(self.removeAdaptor)
        self.netAdaptors[networkAdaptor.removeInetButton] = networkAdaptor

    
    def removeAdaptor(self):
        logging.debug("VMWidget: removeAdaptor(): instantiated")
        logging.debug("VMWidget: sender info: " + str(self.sender()))
        if self.sender() in self.netAdaptors:
            widgetToRemove = self.netAdaptors[self.sender()]
            print("adaptors before: "  + str(self.netAdaptors))
            del self.netAdaptors[self.sender()]
            print("adaptors after: "  + str(self.netAdaptors))
            self.iNetVertBox.removeWidget(widgetToRemove)
            widgetToRemove.deleteLater()
            widgetToRemove = None

    def getWritableData(self):
        logging.debug("VMWidget: getWritableData(): instantiated")
        #build JSON from text entry fields
        jsondata = {}
        jsondata["name"] = {}
        jsondata["name"] = self.nameLineEdit.text()
        jsondata["vrdp-enabled"] = {}
        jsondata["vrdp-enabled"] = self.vrdpEnabledComboBox.currentText()
        jsondata["internalnet-basename"] = [] #may be many
        for netAdaptor in self.netAdaptors.values():
            if isinstance(netAdaptor, NetworkAdaptorWidget):
                jsondata["internalnet-basename"].append(netAdaptor.lineEdit.text())
        return jsondata

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = VMWidget()
    ui.show()
    sys.exit(app.exec_())