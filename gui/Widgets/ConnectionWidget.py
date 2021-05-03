from PyQt5 import QtCore, QtGui, QtWidgets
import logging
from gui.Dialogs.ConnectionActionDialog import ConnectionActionDialog

class ConnectionWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, statusBar=None, baseWidgets=None):
        logging.debug("ConnectionWidget instantiated")
        QtWidgets.QWidget.__init__(self, parent=None)
        self.statusBar = statusBar
        self.baseWidgets = baseWidgets
        self.connectionItemNames = {}
        self.outerVertBox = QtWidgets.QVBoxLayout()
        self.outerVertBox.setObjectName("outerVertBox")

        self.setObjectName("ConnectionWidget")
        self.treeWidget = QtWidgets.QTreeWidget(parent)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().resizeSection(0, 150)
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.showContextMenu)
        self.outerVertBox.addWidget(self.treeWidget)

        # Context menu
        self.connsContextMenu = QtWidgets.QMenu()
        self.createGuac = self.connsContextMenu.addAction("Create Users")
        self.createGuac.triggered.connect(self.createGuacActionEvent)
        self.removeGuac = self.connsContextMenu.addAction("Remove Users")
        self.removeGuac.triggered.connect(self.removeGuacActionEvent)
        self.clearGuac = self.connsContextMenu.addAction("Clear All Entries")
        self.clearGuac.triggered.connect(self.clearGuacActionEvent)

        self.setLayout(self.outerVertBox)
        self.retranslateUi()

    def retranslateUi(self):
        logging.debug("ConnectionWidget: retranslateUi(): instantiated")
        self.setWindowTitle("ConnectionWidget")
        self.treeWidget.headerItem().setText(0, "Experiment Name")
        self.treeWidget.headerItem().setText(1, "Status")
        self.treeWidget.setSortingEnabled(False)
    
    def addConnectionItem(self, configname):
        logging.debug("addConnectionItem(): retranslateUi(): instantiated")
        if configname in self.connectionItemNames:
            logging.error("addConnectionItem(): Item already exists in tree: " + str(configname))
            return
        configTreeWidgetItem = QtWidgets.QTreeWidgetItem(self.treeWidget)
        configTreeWidgetItem.setText(0,configname)
        configTreeWidgetItem.setText(1,"Unknown")
        self.connectionItemNames[configname] = configTreeWidgetItem
        logging.debug("addConnectionItem(): retranslateUi(): Completed")

    def removeConnectionItem(self, configname):
        logging.debug("removeConnectionItem(): retranslateUi(): instantiated")
        if configname not in self.connectionItemNames:
            logging.error("removeConnectionItem(): Item does not exist in tree: " + str(configname))
            return
        configTreeWidgetItem = self.connectionItemNames[configname]
        self.treeWidget.invisibleRootItem().removeChild(configTreeWidgetItem)
        del self.connectionItemNames[configname]
        logging.debug("removeConnectionItem(): Completed")

    def showContextMenu(self, position):
        logging.debug("ConnectionWidget(): showContextMenu(): instantiated")
        self.connsContextMenu.popup(self.treeWidget.mapToGlobal(position))

    def createGuacActionEvent(self):
        logging.debug("MainApp:addMaterialActionEvent() instantiated")
        selectedItem = self.treeWidget.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:createGuacActionEvent no configuration selected")
            self.statusBar.showMessage("Could complete connection action. No configuration items selected or available.")
            return
        selectedItemName = selectedItem.text(0)
        connResult = ConnectionActionDialog(self, selectedItemName, "Add", self.baseWidgets[selectedItemName]["BaseWidget"].vmServerIPLineEdit.text(), self.baseWidgets[selectedItemName]["BaseWidget"].rdpBrokerLineEdit.text()).exec_()

    def removeGuacActionEvent(self):
        logging.debug("MainApp:removeGuacActionEvent() instantiated")
        selectedItem = self.treeWidget.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:removeGuacActionEvent no configuration selected")
            self.statusBar.showMessage("Could complete connection action. No configuration items selected or available.")
            return
        selectedItemName = selectedItem.text(0)
        connResult = ConnectionActionDialog(self, selectedItemName, "Remove", self.baseWidgets[selectedItemName]["BaseWidget"].vmServerIPLineEdit.text(), self.baseWidgets[selectedItemName]["BaseWidget"].rdpBrokerLineEdit.text()).exec_()

    def clearGuacActionEvent(self):
        logging.debug("MainApp:clearGuacActionEvent() instantiated")
        selectedItem = self.treeWidget.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:clearGuacActionEvent no configuration selected")
            self.statusBar.showMessage("Could complete connection action. No configuration items selected or available.")
            return
        selectedItemName = selectedItem.text(0)
        connResult = ConnectionActionDialog(self, selectedItemName, "Clear", self.baseWidgets[selectedItemName]["BaseWidget"].vmServerIPLineEdit.text(), self.baseWidgets[selectedItemName]["BaseWidget"].rdpBrokerLineEdit.text()).exec_()
