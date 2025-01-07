from PyQt5 import QtCore, QtGui, QtWidgets
import logging

class VMStartupCmdWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, cmdjson=None):
        logging.debug("VMStartupCmdWidget instantiated")
        QtWidgets.QWidget.__init__(self, parent=None)

        self.setWindowTitle("VMStartupCmdWidget")
        self.setObjectName("VMStartupCmdWidget")

        self.VMStartupCmdsHLayout = QtWidgets.QHBoxLayout()
        self.VMStartupCmdsHLayout.setObjectName("VMStartupCmdsHLayout")

        self.enabledCheckBox = QtWidgets.QCheckBox()
        self.enabledCheckBox.setObjectName("enabledCheckBox")
        self.enabledCheckBox.setEnabled(True)
        self.VMStartupCmdsHLayout.addWidget(self.enabledCheckBox)

        self.cmdSpinBox = QtWidgets.QSpinBox()
        self.cmdSpinBox.setObjectName("cmdSpinBox")
        self.cmdSpinBox.setRange(1, 25)
        self.VMStartupCmdsHLayout.addWidget(self.cmdSpinBox)

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setStyleSheet("QLineEdit { qproperty-cursorPosition: 0; }")
        self.VMStartupCmdsHLayout.addWidget(self.lineEdit)

        self.removeCommandButton = QtWidgets.QPushButton()
        self.removeCommandButton.setAutoFillBackground(False)
        self.removeCommandButton.setObjectName("removeCommandButton")
        self.VMStartupCmdsHLayout.addWidget(self.removeCommandButton)
        
        self.setLayout(self.VMStartupCmdsHLayout)

        if cmdjson == None:
            cmdjson = self.createDefaultJSONData() 

        self.retranslateUi(cmdjson)

    def retranslateUi(self, cmdjson):
        logging.debug("VMStartupCmdWidget: retranslateUi(): instantiated")
        self.lineEdit.setPlaceholderText("enter your command here, e.g., run --exe \"/bin/bash\" --username user --password pass --wait-stdout --wait-stderr -- -l -c \"echo toor | sudo -S /usr/bin/find /etc/")
        hypervisor = "unset"
        delay = 0
        seq = "0"
        execText = ""
        ena = "0"
        if hypervisor in cmdjson:
            hypervisor = cmdjson["hypervisor"]
        if "seq" in cmdjson:
            seq = cmdjson["seq"]
        self.cmdSpinBox.setValue(int(seq))
        if "exec" in cmdjson:
            execText = cmdjson["exec"]
        if execText.strip() != "":
            self.lineEdit.setText(execText)
        if "enabled" in cmdjson:
            ena = cmdjson["enabled"]
        self.enabledCheckBox.setCheckState(int(ena))
        
        self.removeCommandButton.setText("X")

    def createDefaultJSONData(self):
        logging.debug("VMStartupCmdsDialog: createDefaultJSONData(): instantiated")

        jsondata = {"seq": 0, 
            "hypervisor": "unset", 
            "exec": "",
            "enabled": "2"
            }

        return jsondata

    def getWritableData(self):
        logging.debug("VMStartupCmdsDialog: getWritableData(): instantiated")
        #build JSON from text entry fields

        jsondata = {"seq": str(self.cmdSpinBox.value()), "hypervisor": "unset", "exec": self.lineEdit.text(), "enabled": str(self.enabledCheckBox.checkState())}
        return jsondata

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = VMStartupCmdWidget()
    ui.show()
    sys.exit(app.exec_())