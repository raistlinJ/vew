from PyQt5 import QtCore, QtGui, QtWidgets
import logging

class MaterialWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, configname=None, widgetname="", materialjsondata=None):
        logging.debug("MaterialWidget instantiated")
        QtWidgets.QWidget.__init__(self, parent=None)
        if configname == None or widgetname == "":
            logging.error("configname and widgetname must be provided")
            return None
        self.widgetname = widgetname
        self.configname = configname

        self.setWindowTitle("MaterialWidget")
        self.setObjectName("MaterialWidget")

        self.outerVertBox = QtWidgets.QVBoxLayout()
        self.outerVertBox.setObjectName("outerVertBox")
        self.nameHorBox = QtWidgets.QHBoxLayout()
        self.nameHorBox.setObjectName("nameHorBox")
        self.nameLabel = QtWidgets.QLabel()
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Name:")
        self.nameHorBox.addWidget(self.nameLabel)

        self.nameLineEdit = QtWidgets.QLineEdit()
        self.nameLineEdit.setAcceptDrops(False)
        self.nameLineEdit.setReadOnly(True)
        self.nameLineEdit.setObjectName("nameLineEdit")      
        self.nameHorBox.addWidget(self.nameLineEdit)

        self.outerVertBox.addLayout(self.nameHorBox)
        self.outerVertBox.addStretch()
        
        self.setLayout(self.outerVertBox)
        if materialjsondata == None:
            materialjsondata = self.createDefaultJSONData() 
        self.retranslateUi(materialjsondata)
        
    def retranslateUi(self, materialjsondata):
        logging.debug("MaterialWidget: retranslateUi(): instantiated")
        if materialjsondata == None:
            materialjsondata = {}
        if "name" not in materialjsondata:
            materialjsondata["name"] = self.widgetname
        self.nameLineEdit.setText(materialjsondata["name"])

    def getWritableData(self):
        logging.debug("MaterialWidget: getWritableData(): instantiated")
        #build JSON from text entry fields
        jsondata = {}
        jsondata["name"] = self.nameLineEdit.text()
        return jsondata

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = MaterialWidget()
    ui.show()
    sys.exit(app.exec_())