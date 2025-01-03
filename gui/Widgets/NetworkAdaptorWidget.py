from PyQt5 import QtCore, QtGui, QtWidgets
import logging

class NetworkAdaptorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logging.debug("NetworkAdaptorWidget instantiated")
        QtWidgets.QWidget.__init__(self, parent=None)
        self.setWindowTitle("NetworkAdaptorWidget")
        self.setObjectName("NetworkAdaptorWidget")

        self.networkAdaptorHLayout = QtWidgets.QHBoxLayout()
        self.networkAdaptorHLayout.setObjectName("NetworkAdaptorHLayout")

        self.internalnetLabel = QtWidgets.QLabel()
        self.internalnetLabel.setObjectName("internalnetButton")

        self.networkAdaptorHLayout.addWidget(self.internalnetLabel)
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setObjectName("lineEdit")
        self.networkAdaptorHLayout.addWidget(self.lineEdit)

        self.removeInetButton = QtWidgets.QPushButton()
        self.removeInetButton.setAutoFillBackground(False)
        self.removeInetButton.setObjectName("removeInetButton")
        self.networkAdaptorHLayout.addWidget(self.removeInetButton)
        
        self.setLayout(self.networkAdaptorHLayout)

        self.retranslateUi()

    def retranslateUi(self):
        logging.debug("NetworkAdaptorWidget: retranslateUi(): instantiated")
        self.internalnetLabel.setText("Adaptor Basename")
        self.lineEdit.setText("intnet")
        self.removeInetButton.setText("X")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = NetworkAdaptorWidget()
    ui.show()
    sys.exit(app.exec_())