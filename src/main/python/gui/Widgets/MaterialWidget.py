# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MaterialWidget.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class MaterialWidget(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(444, 387)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 10, 445, 510))#391, 281))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.nameLabel = QtWidgets.QLabel(self.layoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.horizontalLayout.addWidget(self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.nameLineEdit.setAcceptDrops(False)
        self.nameLineEdit.setReadOnly(True)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.horizontalLayout.addWidget(self.nameLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.paddingRow1 = QtWidgets.QWidget(self.layoutWidget)
        self.paddingRow1.setObjectName("paddingRow1")
        self.verticalLayout.addWidget(self.paddingRow1)
        self.paddingRow2 = QtWidgets.QWidget(self.layoutWidget)
        self.paddingRow2.setObjectName("paddingRow2")
        self.verticalLayout.addWidget(self.paddingRow2)
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.nameLabel.setText(_translate("Form", "Name:"))
        self.nameLineEdit.setText(_translate("Form", "exercise.doc"))
        self.pushButton.setText(_translate("Form", "Save Changes"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = MaterialWidget()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())