# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NetworkAdaptorWidget.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class NetworkAdaptorWidget(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(483, 300)
        self.layoutWidget = QtWidgets.QWidget(Form)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 436, 27))
        self.layoutWidget.setObjectName("layoutWidget")
        self.NetworkAdaptorWidget = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.NetworkAdaptorWidget.setContentsMargins(0, 0, 0, 0)
        self.NetworkAdaptorWidget.setObjectName("NetworkAdaptorWidget")
        self.internalnetButton = QtWidgets.QRadioButton(self.layoutWidget)
        self.internalnetButton.setObjectName("internalnetButton")
        self.NetworkAdaptorWidget.addWidget(self.internalnetButton)
        self.udpTunnelButton = QtWidgets.QRadioButton(self.layoutWidget)
        self.udpTunnelButton.setObjectName("udpTunnelButton")
        self.NetworkAdaptorWidget.addWidget(self.udpTunnelButton)
        self.lineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.NetworkAdaptorWidget.addWidget(self.lineEdit)
        self.removeInetButton = QtWidgets.QPushButton(self.layoutWidget)
        self.removeInetButton.setAutoFillBackground(False)
        self.removeInetButton.setObjectName("removeInetButton")
        self.NetworkAdaptorWidget.addWidget(self.removeInetButton)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.internalnetButton.setText(_translate("Form", "Internalnet"))
        self.udpTunnelButton.setText(_translate("Form", "UDPTunnel"))
        self.lineEdit.setText(_translate("Form", "intnet"))
        self.removeInetButton.setText(_translate("Form", "X"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = NetworkAdaptorWidget()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

# Name: Max Morales
# Undergrad: Computer Science
# Internship: DoD
# Future Job: DoD
# Graduation Date: This December