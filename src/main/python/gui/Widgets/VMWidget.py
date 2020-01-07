from PyQt5 import QtCore, QtGui, QtWidgets
from gui.Widgets.NetworkAdaptorWidget import NetworkAdaptorWidget
import logging

class VMWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, vmjsondata=None):
        QtWidgets.QWidget.__init__(self, parent=None)
        self.setObjectName("VMWidget")
        self.resize(444, 387)
        self.layoutWidget = QtWidgets.QWidget(parent)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 10, 445, 510))
        self.layoutWidget.setObjectName("layoutWidget")
        self.outerVertBox = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.outerVertBox.setContentsMargins(0, 0, 0, 0)
        self.outerVertBox.setObjectName("outerVertBox")
        self.nameHorBox = QtWidgets.QHBoxLayout()
        self.nameHorBox.setObjectName("nameHorBox")
        self.nameLabel = QtWidgets.QLabel(self.layoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Name:")
        self.nameHorBox.addWidget(self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.nameLineEdit.setAcceptDrops(False)
        self.nameLineEdit.setReadOnly(True)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameHorBox.addWidget(self.nameLineEdit)
        self.outerVertBox.addLayout(self.nameHorBox)
        self.vrdpEnabledHorBox = QtWidgets.QHBoxLayout()
        self.vrdpEnabledHorBox.setObjectName("vrdpEnabledHorBox")
        self.vrdpEnabledLabel = QtWidgets.QLabel(self.layoutWidget)
        self.vrdpEnabledLabel.setText("VRDP Enabled:")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vrdpEnabledLabel.sizePolicy().hasHeightForWidth())
        self.vrdpEnabledLabel.setSizePolicy(sizePolicy)
        self.vrdpEnabledLabel.setObjectName("vrdpEnabledLabel")
        self.vrdpEnabledHorBox.addWidget(self.vrdpEnabledLabel)
        self.vrdpEnabledComboBox = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vrdpEnabledComboBox.sizePolicy().hasHeightForWidth())
        self.vrdpEnabledComboBox.setSizePolicy(sizePolicy)
        self.vrdpEnabledComboBox.setObjectName("vrdpEnabledComboBox")
        self.vrdpEnabledComboBox.addItem("false")
        self.vrdpEnabledComboBox.addItem("true")
        self.vrdpEnabledHorBox.addWidget(self.vrdpEnabledComboBox)
        self.outerVertBox.addLayout(self.vrdpEnabledHorBox)

        self.iNetVertBox = QtWidgets.QVBoxLayout()
        self.iNetVertBox.setObjectName("iNetVertBox")
        self.iNetVertBox.setSpacing(0)
        self.iNetVertBox.setContentsMargins(0,0,0,0)
        self.outerVertBox.addLayout(self.iNetVertBox)
        
        self.addAdaptorButton = QtWidgets.QPushButton(self.layoutWidget)
        self.addAdaptorButton.setObjectName("addAdaptorButton")
        self.addAdaptorButton.setText("Add Network Adaptor")
        self.addAdaptorButton.clicked.connect(self.addAdaptor)
        self.outerVertBox.addWidget(self.addAdaptorButton, alignment=QtCore.Qt.AlignHCenter)
        
        self.setLayout(self.outerVertBox)
        self.retranslateUi(vmjsondata)

    def retranslateUi(self, vmjsondata):
        self.nameLineEdit.setText(vmjsondata["name"])
        self.vrdpEnabledComboBox.setCurrentIndex(self.vrdpEnabledComboBox.findText(vmjsondata["vrdp-enabled"]))

        ###add adaptors
        if "internalnet-basename" in vmjsondata:
            if isinstance(vmjsondata["internalnet-basename"], list):
                for adaptor in vmjsondata["internalnet-basename"]:
                    self.addAdaptor(adaptor)
            else:
                self.addAdaptor(vmjsondata["internalnet-basename"])

    def addAdaptor(self, adaptorname="intnet", type="intnet"):
        logging.debug("addAdaptor() instantiated")
        networkAdaptor = NetworkAdaptorWidget()
        Form = QtWidgets.QWidget()
        networkAdaptor.setupUi(Form)
        networkAdaptor.lineEdit.setText("intnet")

        self.iNetVertBox.addWidget(Form)
        return networkAdaptor

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = VMWidget()
    ui.show()
    sys.exit(app.exec_())