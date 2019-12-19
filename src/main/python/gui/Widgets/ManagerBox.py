# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ManagerBox.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class ManagerBox(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(763, 529)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(Form)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 720, 521))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.manager_selection = QtWidgets.QHBoxLayout()
        self.manager_selection.setObjectName("manager_selection")
        self.manager_label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.manager_label.setObjectName("manager_label")
        self.manager_selection.addWidget(self.manager_label)
        self.padding1 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding1.setObjectName("padding1")
        self.manager_selection.addWidget(self.padding1)
        self.padding2 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding2.setObjectName("padding2")
        self.manager_selection.addWidget(self.padding2)
        self.padding3 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding3.setObjectName("padding3")
        self.manager_selection.addWidget(self.padding3)
        self.padding4 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding4.setObjectName("padding4")
        self.manager_selection.addWidget(self.padding4)
        self.padding5 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding5.setObjectName("padding5")
        self.manager_selection.addWidget(self.padding5)
        self.padding6 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding6.setObjectName("padding6")
        self.manager_selection.addWidget(self.padding6)
        self.checkBox = QtWidgets.QCheckBox(self.verticalLayoutWidget_2)
        self.checkBox.setText("")
        self.checkBox.setObjectName("checkBox")
        self.manager_selection.addWidget(self.checkBox)
        self.verticalLayout_2.addLayout(self.manager_selection)
        self.clients_row = QtWidgets.QHBoxLayout()
        self.clients_row.setObjectName("clients_row")
        self.num_clients_label_header = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.num_clients_label_header.setObjectName("num_clients_label_header")
        self.clients_row.addWidget(self.num_clients_label_header)
        self.num_clients_label_footer = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.num_clients_label_footer.setObjectName("num_clients_label_footer")
        self.clients_row.addWidget(self.num_clients_label_footer)
        self.padding7 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding7.setObjectName("padding7")
        self.clients_row.addWidget(self.padding7)
        self.verticalLayout_2.addLayout(self.clients_row)
        self.workshops_row = QtWidgets.QHBoxLayout()
        self.workshops_row.setObjectName("workshops_row")
        self.padding8 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding8.setObjectName("padding8")
        self.workshops_row.addWidget(self.padding8)
        self.workshops_running_label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.workshops_running_label.setObjectName("workshops_running_label")
        self.workshops_row.addWidget(self.workshops_running_label)
        self.padding9 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding9.setObjectName("padding9")
        self.workshops_row.addWidget(self.padding9)
        self.verticalLayout_2.addLayout(self.workshops_row)
        self.padding_row1 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding_row1.setObjectName("padding_row1")
        self.verticalLayout_2.addWidget(self.padding_row1)
        self.padding_row2 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding_row2.setObjectName("padding_row2")
        self.verticalLayout_2.addWidget(self.padding_row2)
        self.padding_row3 = QtWidgets.QWidget(self.verticalLayoutWidget_2)
        self.padding_row3.setObjectName("padding_row3")
        self.verticalLayout_2.addWidget(self.padding_row3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.manager_label.setText(_translate("Form", "Manager"))
        self.num_clients_label_header.setText(_translate("Form", "Participants viewing Frontend:"))
        self.num_clients_label_footer.setText(_translate("Form", "0"))
        self.workshops_running_label.setText(_translate("Form", "Workshops Running:"))
