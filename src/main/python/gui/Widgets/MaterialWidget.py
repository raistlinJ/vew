from PyQt5 import QtCore, QtGui, QtWidgets
import logging

class MaterialWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, materialjsondata=None):
        QtWidgets.QWidget.__init__(self, parent=None)
        self.setObjectName("MaterialWidget")
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
        
        self.saveButton = QtWidgets.QPushButton(self.layoutWidget)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setText("Save Changes")
        self.outerVertBox.addWidget(self.saveButton)
        
        self.setLayout(self.outerVertBox)
        self.retranslateUi(materialjsondata)
        
    def retranslateUi(self, materialjsondata):
        self.setWindowTitle("MaterialWidget")

        self.nameLineEdit.setText(materialjsondata["name"])

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = MaterialWidget()
    ui.show()
    sys.exit(app.exec_())