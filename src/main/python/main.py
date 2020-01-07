from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, qApp, QAction, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QMessageBox, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QStackedWidget)

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
import json

# Handle high resolution displays:
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class MainApp(QMainWindow):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        self.baseWidgets = {}
        self.vmWidgets = {}
        self.materialWidgets = {}

        self.setFixedSize(670,565)
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)
        self.setWindowTitle("ARL South RES v0.1")

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setGeometry(QtCore.QRect(0, 15, 668, 565))
        self.tabWidget.setObjectName("tabWidget")

        # Configuration Window (windowBox) contains:
        ## windowBoxHLayout contains:
        ###treeWidget (Left)
        ###basedataBoxHLayout (Right)
        self.windowBox = QtWidgets.QWidget()
        self.windowBox.setObjectName("windowBox")
        self.windowBoxHLayout = QtWidgets.QHBoxLayout(self.windowBox)
        self.windowBoxHLayout.setContentsMargins(0, 0, 0, 0)
        self.windowBoxHLayout.setObjectName("windowBoxHLayout")
        self.workshopTree = QtWidgets.QTreeWidget(self.windowBox)
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
        self.workshopTree.headerItem().setText(0, "Workshops")
        self.workshopTree.setSortingEnabled(False)
        self.windowBoxHLayout.addWidget(self.workshopTree)
        
        self.basedataStackedWidget = QStackedWidget(self)
        self.basedataStackedWidget.setObjectName("basedataStackedWidget")
        self.windowBoxHLayout.addWidget(self.basedataStackedWidget)
        self.tabWidget.addTab(self.windowBox, "Configuration")

        # VBox Actions Tab
        self.superMenu = SuperMenu()
        self.superMenu_Form = QtWidgets.QWidget()
        self.superMenu.setupUi(self.superMenu_Form)
        self.superMenu_Form.setObjectName("superMenu")
        self.tabWidget.addTab(self.superMenu_Form, "VBox Actions")      

        # Frontend tab
        self.managerBox = ManagerBox()
        self.managerBox_Form = QtWidgets.QWidget()
        self.managerBox.setupUi(self.managerBox_Form)
        self.superMenu_Form.setObjectName("managerBox")
        #self.tabWidget.addTab(self.managerBox_Form, "Frontend")

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 768, 22))
        self.menubar.setObjectName("menubar")

        self.populateUi()
        self.tabWidget.setCurrentIndex(0)

    # Context menu for blank space
        self.blankTreeContextMenu = QtWidgets.QMenu()
       	self.addWorkshop = self.blankTreeContextMenu.addAction("New Workshop")
       	self.addWorkshop.triggered.connect(self.addWorkshopActionEvent)
        self.importWorkshop = self.blankTreeContextMenu.addAction("Import Workshop from EBX archive")
        self.importWorkshop.triggered.connect(self.importActionEvent)

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
        mainLayout.addWidget(self.tabWidget)

        self.saveButton = QtWidgets.QPushButton("Save All")
        mainLayout.addWidget(self.saveButton, alignment=QtCore.Qt.AlignRight)

        self.outerBox = QWidget()
        self.outerBox.setLayout(mainLayout)
        self.setCentralWidget(self.outerBox)
        
    def readSystemConfig(self):
        self.cf = SystemConfigIO()
        self.vbox_path = self.cf.getConfig()['VBOX_LINUX']['VBOX_PATH']
        self.experiment_path = self.cf.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH']
    
    def readExperimentConfig(self, configname):
        self.ec = ExperimentConfigIO()
        return self.ec.getExperimentXMLFileData(configname)

    def populateUi(self):

#####Create the following based on the config file
        confignametmp = "sample"
        configTreeWidgetItem = QtWidgets.QTreeWidgetItem(self.workshopTree)
        configTreeWidgetItem.setText(0,confignametmp)

        jsondata = self.readExperimentConfig(confignametmp)      

    ##########testbed-setup data######
        basejsondata = jsondata["xml"]
        # Base Config Widget 
        self.baseWidget = BaseWidget(self, basejsondata)
        self.baseWidgets[(confignametmp)] = self.baseWidget
        self.basedataStackedWidget.addWidget(self.baseWidget)

    ##########vm data######
        vmsjsondata = jsondata["xml"]["testbed-setup"]["vm-set"]["vm"]
        if isinstance(vmsjsondata, list):
            for vm in vmsjsondata:
                vm_item = QtWidgets.QTreeWidgetItem(configTreeWidgetItem)
                vmlabel = "V: " + vm["name"]
                vm_item.setText(0,vmlabel)
                # VM Config Widget
                vmWidget = VMWidget(self, vm)
                self.vmWidgets[(confignametmp, vmlabel)] = vmWidget
                self.basedataStackedWidget.addWidget(vmWidget)
        else:
            vm_item = QtWidgets.QTreeWidgetItem(configTreeWidgetItem)
            vmlabel = "V: " + vmsjsondata["name"]
            vm_item.setText(0,vmlabel)
            # VM Config Widget
            vmWidget = VMWidget(self, vm)
            self.vmWidgets[(confignametmp, vmlabel)] = vmWidget
            self.basedataStackedWidget.addWidget(vmWidget)

    ##########material data######
        materialsjsondata = jsondata["xml"]["testbed-setup"]["vm-set"]["material"]
        if isinstance(materialsjsondata, list):
            for material in materialsjsondata["material"]:
                material_item = QtWidgets.QTreeWidgetItem(configTreeWidgetItem)
                materiallabel = "M: " + material["name"]
                material_item.setText(0,materiallabel)
                # Material Config Widget
                materialWidget = MaterialWidget(self, material)
                self.materialWidgets[(confignametmp, materiallabel)] = materialWidget
                self.basedataStackedWidget.addWidget(materialWidget)
        else:
            material_item = QtWidgets.QTreeWidgetItem(configTreeWidgetItem)
            materiallabel = "M: " + materialsjsondata["name"]
            material_item.setText(0,materiallabel)
            # Material Config Widget
            materialWidget = MaterialWidget(self, materialsjsondata)
            self.materialWidgets[(confignametmp, materiallabel)] = materialWidget
            self.basedataStackedWidget.addWidget(materialWidget)

###############################

    def onItemSelected(self):
    	# Places the widget on the right 
        selectedItem = self.workshopTree.currentItem()
        #Check if it's the case that an experiment name was selected
        parentSelectedItem = selectedItem.parent()
        if(parentSelectedItem == None):
            #A base widget was selected
            self.baseWidget.baseGroupNameLineEdit.setText(selectedItem.text(0))
            self.basedataStackedWidget.setCurrentWidget(self.baseWidgets[selectedItem.text(0)])
        else:
            #Check if it's the case that a VM Name was selected
            if(selectedItem.text(0)[0] == "V"):
                print("Setting right widget: " + str(self.vmWidgets[(parentSelectedItem.text(0), selectedItem.text(0))]))
                self.basedataStackedWidget.setCurrentWidget(self.vmWidgets[(parentSelectedItem.text(0), selectedItem.text(0))])
            #Check if it's the case that a Material Name was selected
            elif(selectedItem.text(0)[0] == "M"):
                print("Setting right widget: " + str(self.materialWidgets[(parentSelectedItem.text(0), selectedItem.text(0))]))
                self.basedataStackedWidget.setCurrentWidget(self.materialWidgets[(parentSelectedItem.text(0), selectedItem.text(0))])

    def showContextMenu(self, position):
    	
    	if(self.workshopTree.itemAt(position) == None):
    		self.blankTreeContextMenu.popup(self.workshopTree.mapToGlobal(position))
    	elif(self.workshopTree.itemAt(position).parent() == None):
    		self.workshopContextMenu.popup(self.workshopTree.mapToGlobal(position))
    	else:
    		self.itemContextMenu.popup(self.workshopTree.mapToGlobal(position))
    
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
