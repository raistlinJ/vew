from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, qApp, QAction, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QMessageBox, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

from engine.Engine import Engine
from time import sleep

from gui.Widgets.BaseWidget import BaseWidget
from gui.Widgets.VMWidget import VMWidget
from gui.Widgets.MaterialWidget import MaterialWidget
from gui.Widgets.SuperMenu import SuperMenu
from gui.Widgets.ManagerBox import ManagerBox
from engine.Configuration.SystemConfigIO import SystemConfigIO
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO

import sys
import logging

# Handle high resolution displays:
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class MainApp(QMainWindow):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        
###############################
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 15, 668, 565))
        self.tabWidget.setObjectName("tabWidget")
        self.windowBox = QtWidgets.QWidget()
        self.windowBox.setObjectName("windowBox")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.windowBox)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, -1, 658, 521))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.hLayout_windowBox = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.hLayout_windowBox.setContentsMargins(0, 0, 0, 0)
        self.hLayout_windowBox.setObjectName("hLayout_windowBox")
        self.workshopTree = QtWidgets.QTreeWidget(self.horizontalLayoutWidget)
        self.workshopTree.itemClicked.connect(self.onItemSelected)
        self.workshopTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.workshopTree.customContextMenuRequested.connect(self.showContextMenu)

        self.workshopTree.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.workshopTree.sizePolicy().hasHeightForWidth())
        self.workshopTree.setSizePolicy(sizePolicy)
        self.workshopTree.setMaximumSize(200,521)
        self.workshopTree.setObjectName("workshopTree")
        self.hLayout_windowBox.addWidget(self.workshopTree)
        self.actionEventBox = QtWidgets.QHBoxLayout()
        self.actionEventBox.setObjectName("actionEventBox")
        self.actionEventBox.addStretch(1)
        self.hLayout_windowBox.addLayout(self.actionEventBox)
        self.tabWidget.addTab(self.windowBox, "")

        
        # VBox Actions Tab
        self.superMenu = SuperMenu()
        self.superMenu_Form = QtWidgets.QWidget()
        self.superMenu.setupUi(self.superMenu_Form)
        self.superMenu_Form.setObjectName("superMenu")
        self.tabWidget.addTab(self.superMenu_Form, "")
        # self.superMenu = QtWidgets.QWidget()
        # self.superMenu.setObjectName("superMenu")
        # self.tabWidget.addTab(self.superMenu, "")
        

        # Frontend tab
        self.managerBox = ManagerBox()
        self.managerBox_Form = QtWidgets.QWidget()
        self.managerBox.setupUi(self.managerBox_Form)
        self.superMenu_Form.setObjectName("managerBox")
        #self.tabWidget.addTab(self.managerBox_Form, "")
        # self.managerBox = QtWidgets.QWidget()
        # self.managerBox.setObjectName("managerBox")
        # self.tabWidget.addTab(self.managerBox, "")


        # MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        # MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 768, 22))
        self.menubar.setObjectName("menubar")
        # MainWindow.setMenuBar(self.menubar)

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

        # Context menu for blank space
        self.blankTreeContextMenu = QtWidgets.QMenu()
       	self.addWorkshop = self.blankTreeContextMenu.addAction("New Workshop")
       	self.addWorkshop.triggered.connect(self.addWorkshopActionEvent)
        self.importWorkshop = self.blankTreeContextMenu.addAction("Import Workshop from EBX archive")
        self.importWorkshop.triggered.connect(self.importActionEvent)
        self.downloadFromRepo = self.blankTreeContextMenu.addAction("Download Workshop From Repo")
        self.downloadFromRepo.triggered.connect(self.download)

        # Workshop context menu
        self.workshopContextMenu = QtWidgets.QMenu()
        self.addVM = self.workshopContextMenu.addAction("Add VM")
        self.addVM.triggered.connect(self.addVMActionEvent)
        self.addMaterial = self.workshopContextMenu.addAction("Add Material File")
        self.addMaterial.triggered.connect(self.addMaterialActionEvent)
        # Add line separator here
        self.createRDP = self.workshopContextMenu.addAction("Create RDP Files")
        self.createRDP.triggered.connect(self.createRDPActionEvent)
        # Add line separator here
        self.createGuac = self.workshopContextMenu.addAction("Create Guacamole Users")
        self.createGuac.triggered.connect(self.createGuacActionEvent)
        self.removeGuac = self.workshopContextMenu.addAction("Remove Guacamole Users")
        self.removeGuac.triggered.connect(self.removeGuacActionEvent)
        # Add line separator here
        self.removeWorkshop = self.workshopContextMenu.addAction("Remove Workshop")
        self.removeWorkshop.triggered.connect(self.removeWorkshopActionEvent)
        self.exportWorkshop = self.workshopContextMenu.addAction("Export Workshop")
        self.exportWorkshop.triggered.connect(self.exportWorkshopActionEvent)

       	# VM/Material context menu
        self.itemContextMenu = QtWidgets.QMenu()
        self.removeItem = self.itemContextMenu.addAction("Remove Workshop Item")
        self.removeItem.triggered.connect(self.removeVMActionEvent)

        mainLayout = QVBoxLayout()
        
        #mainLayout.setVerticalSpacing(0)
        # self.vmManageBox = VMManageBox(self)
        # self.connectionBox = ConnectionBox(self, self.vmManageBox)
        
        self.outerBox = QWidget()
        self.setCentralWidget(self.outerBox)
        
        # mainLayout.addWidget(self.connectionBox)
        # mainLayout.addWidget(self.vmManageBox)
        mainLayout.addWidget(self.tabWidget)
        self.outerBox.setLayout(mainLayout)
     
    def readSystemConfig(self):
        self.cf = SystemConfigIO()
        self.vbox_path = self.cf.getConfig()['VBOX_LINUX']['VBOX_PATH']
        self.experiment_path = self.cf.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH']
    
    def readExperimentConfig(self, configname):
        self.ec = ExperimentConfigIO()
        return self.ec.getExperimentXMLFileData(configname)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        #self.initMenu()
        self.setFixedSize(670,565)
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

        self.setWindowTitle(_translate("MainWindow", "ARL South RES v0.1"))

#####Create the following based on the config file
        jsondata = self.readExperimentConfig("sample")

        vms = jsondata["xml"]["testbed-setup"]["vm-set"]
        # for name in vms["vm"]:    

        item_0 = QtWidgets.QTreeWidgetItem(self.workshopTree)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_2 = QtWidgets.QTreeWidgetItem(item_0)
        item_3 = QtWidgets.QTreeWidgetItem(item_0)
        item_4 = QtWidgets.QTreeWidgetItem(item_0)
        item_5 = QtWidgets.QTreeWidgetItem(self.workshopTree)


        # Base Config Widget 
        self.baseWidget = BaseWidget()
        self.baseWidget_Form = QtWidgets.QWidget()
        self.baseWidget.setupUi(self.baseWidget_Form)
        # self.actionEventBox.addWidget(Form)

        # VM Config Widget
        self.vmWidget = VMWidget()
        self.vmWidget_Form = QtWidgets.QWidget()
        self.vmWidget.setupUi(self.vmWidget_Form)
        self.vmWidget.addAdaptorButton.clicked.connect(self.addAdaptorEventHandler)
        # self.actionEventBox.addWidget(Form)

        # Material Config Widget
        self.materialWidget = MaterialWidget()
        self.materialWidget_Form = QtWidgets.QWidget()
        self.materialWidget.setupUi(self.materialWidget_Form)
        # self.actionEventBox.addWidget(Form)

###############################

        self.workshopTree.headerItem().setText(0, _translate("MainWindow", "Workshops"))
        __sortingEnabled = self.workshopTree.isSortingEnabled()
        self.workshopTree.setSortingEnabled(False)
        self.workshopTree.topLevelItem(0).setText(0, _translate("MainWindow", "sample"))
        self.workshopTree.topLevelItem(0).child(0).setText(0, _translate("MainWindow", "M: exercise.doc"))
        self.workshopTree.topLevelItem(0).child(1).setText(0, _translate("MainWindow", "V: defaulta"))
        self.workshopTree.topLevelItem(0).child(2).setText(0, _translate("MainWindow", "V: defaultb"))
        self.workshopTree.topLevelItem(0).child(3).setText(0, _translate("MainWindow", "V: defaultc"))
        self.workshopTree.topLevelItem(1).setText(0, "Workshop 2")
        self.workshopTree.setSortingEnabled(__sortingEnabled)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.windowBox), _translate("MainWindow", "Configuration"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.superMenu_Form), _translate("MainWindow", "VBox Actions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.managerBox_Form), _translate("MainWindow", "Frontend"))

    def onItemSelected(self):
    	# Removes widget on the right side
    	rightPaneItem = self.actionEventBox.itemAt(0)
    	self.actionEventBox.removeItem(rightPaneItem)

    	# Set parent to none, if the removed widget wasn't a spacer item 
    	if(not isinstance(rightPaneItem, QtWidgets.QSpacerItem)):
    		rightPaneItem.widget().setParent(None)

    	# Places the widget on the right 
    	selectedItem = self.workshopTree.currentItem()
    	if(selectedItem.parent() == None):
    		self.baseWidget.baseGroupNameLineEdit.setText(selectedItem.text(0))
    		self.actionEventBox.addWidget(self.baseWidget_Form)
    	elif(selectedItem.text(0)[0] == "V"):
    		self.actionEventBox.addWidget(self.vmWidget_Form)
    	elif(selectedItem.text(0)[0] == "M"):
    		self.actionEventBox.addWidget(self.materialWidget_Form)

    def showContextMenu(self, position):
    	
    	if(self.workshopTree.itemAt(position) == None):
    		self.blankTreeContextMenu.popup(self.workshopTree.mapToGlobal(position))
    	elif(self.workshopTree.itemAt(position).parent() == None):
    		self.workshopContextMenu.popup(self.workshopTree.mapToGlobal(position))
    	else:
    		self.itemContextMenu.popup(self.workshopTree.mapToGlobal(position))

    def addAdaptorEventHandler(self):
    	networkAdaptor = self.vmWidget.addAdaptor()
    
    def addWorkshopActionEvent(self):
    	pass

    def importActionEvent(self):
    	pass

    def download(self):
    	pass

    def addVMActionEvent(self):
    	pass

    def addMaterialActionEvent(self):
    	pass

    def createRDPActionEvent(self):
    	pass

    def createGuacActionEvent(self):
    	pass

    def removeGuacActionEvent(self):
    	pass

    def removeWorkshopActionEvent(self):
    	pass

    def exportWorkshopActionEvent(self):
    	pass

    def removeVMActionEvent(self):
    	pass


    def closeEvent(self, event):
        logging.debug("closeEvent(): instantiated")
        e = Engine.getInstance()
        # res = e.execute("pptp status " + ConnectionBox.CONNECTION_NAME)
        # logging.debug("delete_event(): result: " + str(res))
        # if res == -1:
        #     self.destroy()
        #     #continue with any other destruction
        #     logging.debug("closeEvent(): accept()")
        #     self.connectionBox.killConnThread()
        #     event.accept()
        #     qApp.quit()
        #     return
        # result = res["connStatus"]
        # if result == Connection.NOT_CONNECTED:
        #     #continue with any other destruction
        #     logging.debug("closeEvent(): returning accept()")
        #     self.connectionBox.killConnThread()
        #     qApp.quit()
        #     event.accept()
        #     return
        # if result == Connection.CONNECTING:
        #     close = QMessageBox.warning(self,
        #                                  "Busy",
        #                                  "Connection is busy, try again later",
        #                                  QMessageBox.Ok)            
        # elif result == Connection.CONNECTED:
        #     close = QMessageBox.question(self,
        #                                  "QUIT",
        #                                  "Disconnect and quit?",
        #                                  QMessageBox.Yes | QMessageBox.No)
        #     if close == QMessageBox.Yes:
        #         logging.debug("closeEvent(): opening disconnect dialog")
        #         #need to create a thread (probably a dialog box with disabled ok button until connection either times out (5 seconds), connection good
        #         e = Engine.getInstance()
        #         e.execute("pptp stop " + ConnectionBox.CONNECTION_NAME)
        #         s = DisconnectingDialog(None, ConnectionBox.CONNECTION_NAME).exec_()
        #         if s["connStatus"] == Connection.NOT_CONNECTED:
        #             self.connectionBox.killConnThread()
        #             event.accept()
        #             qApp.quit()
        #             return
        #         else:
        #             close = QMessageBox.warning(self,
        #                                  "Busy",
        #                                  "Connection is busy, try again later",
        #                                  QMessageBox.Ok)            
        #             event.ignore()
        #             return
        #logging.debug("closeEvent(): returning ignore")
        #event.ignore()
        logging.debug("closeEvent(): returning accept")
        event.accept()
        qApp.quit()
        return
    
    def initMenu(self):               
        
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    appctxt = ApplicationContext()
    app = MainApp()
    QApplication.setStyle(QStyleFactory.create('Fusion'))
    #changePalette()
   
    app.show()
    sys.exit(appctxt.app.exec_())
