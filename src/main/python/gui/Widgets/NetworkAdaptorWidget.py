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
        # self.internalnetButton = QtWidgets.QRadioButton(self.layoutWidget)
        # self.internalnetButton.setObjectName("internalnetButton")

        self.internalnetLabel = QtWidgets.QLabel()
        self.internalnetLabel.setObjectName("internalnetButton")

        self.networkAdaptorHLayout.addWidget(self.internalnetLabel)
        # self.udpTunnelButton = QtWidgets.QRadioButton(self.layoutWidget)
        # self.udpTunnelButton.setObjectName("udpTunnelButton")
        # self.networkAdaptorHLayout.addWidget(self.udpTunnelButton)
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
        # self.internalnetButton.setText(_translate("Form", "Internalnet"))
        # self.udpTunnelButton.setText(_translate("Form", "UDPTunnel"))
        self.lineEdit.setText("intnet")
        self.removeInetButton.setText("X")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = NetworkAdaptorWidget()
    ui.show()
    sys.exit(app.exec_())