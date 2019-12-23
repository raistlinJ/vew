# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VMWidget.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from gui.Widgets.NetworkAdaptorWidget import NetworkAdaptorWidget
import logging

class VMWidget(object):

    def __init__(self, Form, vmjsondata):
        Form.setObjectName("Form")
        Form.resize(444, 387) #Form.resize(472, 353)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 10, 445, 510))#471, 331))
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
        self.outerVertBox.addLayout(self.iNetVertBox)
        self.addAdaptorButton = QtWidgets.QPushButton(self.layoutWidget)
        self.addAdaptorButton.setObjectName("addAdaptorButton")
        self.addAdaptorButton.setText("Add Network Adaptor")
        self.addAdaptorButton.clicked.connect(self.addAdaptor)
        self.outerVertBox.addWidget(self.addAdaptorButton)
        self.paddingRow1 = QtWidgets.QWidget(self.layoutWidget)
        self.paddingRow1.setObjectName("paddingRow1")
        # self.outerVertBox.addWidget(self.paddingRow1)
        self.paddingRow2 = QtWidgets.QWidget(self.layoutWidget)
        self.paddingRow2.setObjectName("paddingRow2")
        # self.outerVertBox.addWidget(self.paddingRow2)
        self.saveButton = QtWidgets.QPushButton(self.layoutWidget)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setText("Save Changes")
        self.outerVertBox.addWidget(self.saveButton)
        
        self.retranslateUi(Form, vmjsondata)

    def retranslateUi(self, Form, vmjsondata):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

        self.nameLineEdit.setText(_translate("Form", vmjsondata["name"]))
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
        networkAdaptor.lineEdit.setText(adaptorname)

        self.iNetVertBox.addWidget(Form)
        return networkAdaptor

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = VMWidget()
    #ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
