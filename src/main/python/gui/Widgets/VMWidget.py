# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'VMWidget.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from gui.Widgets.NetworkAdaptorWidget import NetworkAdaptorWidget

class VMWidget(object):
    def setupUi(self, Form):
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
        self.vrdpEnabledComboBox.addItem("")
        self.vrdpEnabledComboBox.addItem("")
        self.vrdpEnabledHorBox.addWidget(self.vrdpEnabledComboBox)
        self.outerVertBox.addLayout(self.vrdpEnabledHorBox)
        self.iNetVertBox = QtWidgets.QVBoxLayout()
        self.iNetVertBox.setObjectName("iNetVertBox")
        self.outerVertBox.addLayout(self.iNetVertBox)
        self.addAdaptorButton = QtWidgets.QPushButton(self.layoutWidget)
        self.addAdaptorButton.setObjectName("addAdaptorButton")
        self.outerVertBox.addWidget(self.addAdaptorButton)
        self.paddingRow1 = QtWidgets.QWidget(self.layoutWidget)
        self.paddingRow1.setObjectName("paddingRow1")
        # self.outerVertBox.addWidget(self.paddingRow1)
        self.paddingRow2 = QtWidgets.QWidget(self.layoutWidget)
        self.paddingRow2.setObjectName("paddingRow2")
        # self.outerVertBox.addWidget(self.paddingRow2)
        self.saveButton = QtWidgets.QPushButton(self.layoutWidget)
        self.saveButton.setObjectName("saveButton")
        self.outerVertBox.addWidget(self.saveButton)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.networkadaptorWidget = NetworkAdaptorWidget()
        Form = QtWidgets.QWidget()
        self.networkadaptorWidget.setupUi(Form)
        self.iNetVertBox.addWidget(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.nameLabel.setText(_translate("Form", "Name:"))
        self.nameLineEdit.setText(_translate("Form", "Ubuntu"))
        self.vrdpEnabledLabel.setText(_translate("Form", "VRDP Enabled:"))
        self.vrdpEnabledComboBox.setItemText(0, _translate("Form", "False"))
        self.vrdpEnabledComboBox.setItemText(1, _translate("Form", "True"))
        self.addAdaptorButton.setText(_translate("Form", "Add Network Adaptor"))
        self.saveButton.setText(_translate("Form", "Save Changes"))

    def addAdaptor(self):

        networkAdaptor = NetworkAdaptorWidget()
        Form = QtWidgets.QWidget()
        networkAdaptor.setupUi(Form)

        
        networkAdaptor.lineEdit.setText("default__net")

        self.iNetVertBox.addWidget(Form)
        return networkAdaptor


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = VMWidget()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
