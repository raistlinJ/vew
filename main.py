import sys
import logging
import json
import os

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, qApp, QAction, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QMessageBox, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QStackedWidget, QStatusBar, QMenuBar)

from engine.Engine import Engine
import time

from gui.Widgets.BaseWidget import BaseWidget
from gui.Widgets.VMWidget import VMWidget
from gui.Widgets.MaterialWidget import MaterialWidget
from gui.Widgets.ExperimentActionsWidgets.ExperimentActionsWidget import ExperimentActionsWidget
from gui.Widgets.ConnectionWidgets.ConnectionWidget import ConnectionWidget
from gui.Widgets.ManagerBox import ManagerBox
from engine.Configuration.SystemConfigIO import SystemConfigIO
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from gui.Dialogs.MaterialAddFileDialog import MaterialAddFileDialog
from gui.Dialogs.MaterialRemoveFileDialog import MaterialRemoveFileDialog
from gui.Dialogs.ExperimentRemoveFileDialog import ExperimentRemoveFileDialog
from gui.Dialogs.VMRetreiveDialog import VMRetrieveDialog
from gui.Dialogs.ExperimentAddDialog import ExperimentAddDialog
from gui.Dialogs.PackageImportDialog import PackageImportDialog
from gui.Dialogs.PackageExportDialog import PackageExportDialog
from gui.Dialogs.HypervisorOpenDialog import HypervisorOpenDialog
from gui.Dialogs.ConfigurationDialog import ConfigurationDialog

from plugins.ctfi2.gui.CTFi2GUI import CTFi2GUI

# Handle high resolution displays:
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class MainApp(QWidget):
    def __init__(self, parent=None):
        logging.debug("MainApp:init() instantiated")
        super().__init__()
        self.baseWidgets = {}
        self.vmWidgets = {}
        self.materialWidgets = {}
        self.cf = SystemConfigIO()
        self.ec = ExperimentConfigIO()
        self.statusBar = QStatusBar()
        
        self.setMinimumSize(670,565)
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)
        self.setWindowTitle("ARL South RES v0.1")

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setGeometry(QtCore.QRect(0, 15, 668, 565))
        self.tabWidget.setObjectName("tabWidget")

        # Configuration Window (windowBox) contains:
        ## windowBoxHLayout contains:
        ###experimentTree (Left)
        ###basedataStackedWidget (Right)
        self.windowWidget = QtWidgets.QWidget()
        self.windowWidget.setObjectName("windowWidget")
        self.windowBoxHLayout = QtWidgets.QHBoxLayout()
        #self.windowBoxHLayout.setContentsMargins(0, 0, 0, 0)
        self.windowBoxHLayout.setObjectName("windowBoxHLayout")
        self.windowWidget.setLayout(self.windowBoxHLayout)

        self.experimentTree = QtWidgets.QTreeWidget()
        self.experimentTree.itemSelectionChanged.connect(self.onItemSelected)
        self.experimentTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.experimentTree.customContextMenuRequested.connect(self.showContextMenu)
        self.experimentTree.setEnabled(True)
        self.experimentTree.setMinimumSize(200,521)
        self.experimentTree.setMaximumWidth(350)
        self.experimentTree.setObjectName("experimentTree")
        self.experimentTree.headerItem().setText(0, "Experiments")
        self.experimentTree.setSortingEnabled(False)
        self.windowBoxHLayout.addWidget(self.experimentTree)
        
        self.basedataStackedWidget = QStackedWidget()
        self.basedataStackedWidget.setObjectName("basedataStackedWidget")
        self.basedataStackedWidget.setEnabled(False)
        self.windowBoxHLayout.addWidget(self.basedataStackedWidget)
        self.tabWidget.addTab(self.windowWidget, "Configuration")

        # VBox Actions Tab
        self.experimentActionsWidget = ExperimentActionsWidget(statusBar=self.statusBar)
        self.experimentActionsWidget.setObjectName("experimentActionsWidget")
        self.tabWidget.addTab(self.experimentActionsWidget, "Experiment Actions")      

        # Remote Connections Tab
        self.connectionWidget = ConnectionWidget(statusBar=self.statusBar)
        self.connectionWidget.setObjectName("connectionsWidget")
        self.tabWidget.addTab(self.connectionWidget, "Remote Connections")

        #Create the bottom layout so that we can access the status bar
        self.bottomLayout = QHBoxLayout()
        self.statusBar.showMessage("Loading GUI...")
        self.bottomLayout.addWidget(self.statusBar)
        self.saveButton = QtWidgets.QPushButton("Save Current")
        self.saveButton.clicked.connect(self.saveExperimentButton)
        self.saveButton.setEnabled(False)
        self.bottomLayout.addWidget(self.saveButton)

        self.populateUi()
        self.setupContextMenus()

        self.initMenu()
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.mainMenu)
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addLayout(self.bottomLayout)
        
        self.setLayout(self.mainLayout)
        #self.setCentralWidget(self.outerBox)
        self.tabWidget.setCurrentIndex(0)

        #self.statusBar.showMessage("Finished Loading GUI Components")

        # Plugin Section
        self.tabWidget.addTab(CTFi2GUI(), "CTFi2")

    def readSystemConfig(self):
        logging.debug("MainApp:readSystemConfig() instantiated")
        self.vboxPath = self.cf.getConfig()['VBOX']['VMANAGE_PATH']
        self.experimentPath = self.cf.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH']
        self.statusBar.showMessage("Finished reading system config")
    
    def setupContextMenus(self):
        logging.debug("MainApp:setupContextMenus() instantiated")
    # Context menu for blank space
        self.blankTreeContextMenu = QtWidgets.QMenu()
       	self.addExperiment = self.blankTreeContextMenu.addAction("New Experiment")
       	self.addExperiment.triggered.connect(self.addExperimentActionEvent)
        self.importExperiment = self.blankTreeContextMenu.addAction("Import Experiment from RES archive")
        self.importExperiment.triggered.connect(self.importActionEvent)

    # Experiment context menu
        self.experimentContextMenu = QtWidgets.QMenu()
        self.addVMContextSubMenu = QtWidgets.QMenu()
        self.experimentContextMenu.addMenu(self.addVMContextSubMenu)
        self.addVMContextSubMenu.setTitle("Add")
        self.addVM = self.addVMContextSubMenu.addAction("Virtual Machines")
        self.addVM.triggered.connect(self.addVMActionEvent)
        self.addMaterial = self.addVMContextSubMenu.addAction("Material Files")
        self.addMaterial.triggered.connect(self.addMaterialActionEvent)

        # Add line separator here
        self.removeExperiment = self.experimentContextMenu.addAction("Remove Experiment")
        self.removeExperiment.triggered.connect(self.removeExperimentItemActionEvent)
        self.exportExperiment = self.experimentContextMenu.addAction("Export Experiment")
        self.exportExperiment.triggered.connect(self.exportActionEvent)

    # VM/Material context menu
        self.itemContextMenu = QtWidgets.QMenu()
        self.removeItem = self.itemContextMenu.addAction("Remove Experiment Item")
        self.removeItem.triggered.connect(self.removeExperimentItemActionEvent)

    def populateUi(self):
        logging.debug("MainApp:populateUi() instantiated")
        self.statusBar.showMessage("Populating UI")
        self.readSystemConfig()
#####Create the following based on the config file
        result = self.ec.getExperimentXMLFilenames()
        if result == None:
            return
        [xmlExperimentFilenames, xmlExperimentNames] = result
        if xmlExperimentFilenames == [] or xmlExperimentNames == []:
            self.statusBar.showMessage("No configs found")
            return

        #For all experiment files found
        for configname in xmlExperimentNames:
        ####Read Experiment Config Data and Populate Tree
            self.loadConfigname(configname)
        self.statusBar.showMessage("Completed populating the User Interface from " + str(len(xmlExperimentNames)) + " config files read", 6000)
    ###############################

    def loadConfigname(self, configname):
        logging.debug("MainApp(): loadConfigname instantiated")
        logging.info("Reading XML data for " + str(configname))
        jsondata = self.ec.getExperimentXMLFileData(configname)
        self.statusBar.showMessage("Finished reading experiment config")

    ##########testbed-setup data######
        if jsondata == None:
            jsondata = {}
        if "xml" not in jsondata or jsondata["xml"] == None or str(jsondata["xml"]).strip() == "":
            jsondata["xml"] = {}
        if "testbed-setup" not in jsondata["xml"]:
            jsondata["xml"]["testbed-setup"] = {}
        if "vm-set" not in jsondata["xml"]["testbed-setup"]:
            jsondata["xml"]["testbed-setup"]["vm-set"] = {}
        #Temporary fix for older xml/json files.
        if "users-filename" not in jsondata["xml"]["testbed-setup"]["vm-set"]:
            jsondata["xml"]["testbed-setup"]["vm-set"]["users-filename"] = ""
        if "rdp-broker-ip" not in jsondata["xml"]["testbed-setup"]["vm-set"]:
            jsondata["xml"]["testbed-setup"]["vm-set"]["rdp-broker-ip"] = ""
        if "chat-server-ip" not in jsondata["xml"]["testbed-setup"]["vm-set"]:
            jsondata["xml"]["testbed-setup"]["vm-set"]["chat-server-ip"] = ""

        configTreeWidgetItem = QtWidgets.QTreeWidgetItem(self.experimentTree)
        configTreeWidgetItem.setText(0,configname)
        self.experimentActionsWidget.addExperimentItem(configname, config_jsondata=jsondata)
        self.connectionWidget.addExperimentItem(configname, config_jsondata=jsondata)
        basejsondata = jsondata["xml"]
        # Base Config Widget 
        self.baseWidget = BaseWidget(self, configname, configname, basejsondata)
        self.baseWidgets[configname] = {"BaseWidget": {}, "VMWidgets": {}, "MaterialWidgets": {} }
        self.baseWidgets[configname]["BaseWidget"] = self.baseWidget
        self.basedataStackedWidget.addWidget(self.baseWidget)

    ##########vm data######
        if "vm" in jsondata["xml"]["testbed-setup"]["vm-set"]:
            vmsjsondata = jsondata["xml"]["testbed-setup"]["vm-set"]["vm"]
            if isinstance(vmsjsondata, list):
                for vm in vmsjsondata:
                    vm_item = QtWidgets.QTreeWidgetItem(configTreeWidgetItem)
                    vmlabel = "V: " + vm["name"]
                    vm_item.setText(0,vmlabel)
                    # VM Config Widget
                    vmWidget = VMWidget(None, configname, vm["name"], vm)
                    self.baseWidgets[configname]["VMWidgets"][vmlabel] = vmWidget
                    self.basedataStackedWidget.addWidget(vmWidget)
            else:
                vm_item = QtWidgets.QTreeWidgetItem(configTreeWidgetItem)
                vmlabel = "V: " + vmsjsondata["name"]
                vm_item.setText(0,vmlabel)
                # VM Config Widget
                vmWidget = VMWidget(None, configname, vmsjsondata["name"], vmsjsondata)
                self.baseWidgets[configname]["VMWidgets"][vmlabel] = vmWidget
                self.basedataStackedWidget.addWidget(vmWidget)

    ##########material data######
        if "material" in jsondata["xml"]["testbed-setup"]["vm-set"]:
            materialsjsondata = jsondata["xml"]["testbed-setup"]["vm-set"]["material"]
            if isinstance(materialsjsondata, list):
                for material in materialsjsondata:
                    material_item = QtWidgets.QTreeWidgetItem(configTreeWidgetItem)
                    materiallabel = "M: " + material["name"]
                    material_item.setText(0,materiallabel)
                    # Material Config Widget
                    materialWidget = MaterialWidget(None, configname, material["name"], material)
                    self.baseWidgets[configname]["MaterialWidgets"][materiallabel] = materialWidget
                    self.basedataStackedWidget.addWidget(materialWidget)
            else:
                material_item = QtWidgets.QTreeWidgetItem(configTreeWidgetItem)
                materiallabel = "M: " + materialsjsondata["name"]
                material_item.setText(0,materiallabel)
                # Material Config Widget
                materialWidget = MaterialWidget(None, configname, materialsjsondata["name"], materialsjsondata)
                self.baseWidgets[configname]["MaterialWidgets"][materiallabel] = materialWidget
                self.basedataStackedWidget.addWidget(materialWidget)
        logging.debug("MainApp(): Finished loading configname: " + str(configname))

    def onItemSelected(self):
        logging.debug("MainApp:onItemSelected instantiated")
    	# Get the selected item
        selectedItem = self.experimentTree.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:onItemSelected no configurations left")
            self.statusBar.showMessage("No configuration items selected or available.")
            return
        self.basedataStackedWidget.setEnabled(True)
        # Now enable the save button
        self.saveButton.setEnabled(True)
        self.saveExperimentMenuButton.setEnabled(True)
        #Check if it's the case that an experiment name was selected
        parentSelectedItem = selectedItem.parent()
        if(parentSelectedItem == None):
            #A base widget was selected
            self.basedataStackedWidget.setCurrentWidget(self.baseWidgets[selectedItem.text(0)]["BaseWidget"])
        else:
            #Check if it's the case that a VM Name was selected
            if(selectedItem.text(0)[0] == "V"):
                logging.debug("Setting right widget: " + str(self.baseWidgets[parentSelectedItem.text(0)]["VMWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.baseWidgets[parentSelectedItem.text(0)]["VMWidgets"][selectedItem.text(0)])
            #Check if it's the case that a Material Name was selected
            elif(selectedItem.text(0)[0] == "M"):
                logging.debug("Setting right widget: " + str(self.baseWidgets[parentSelectedItem.text(0)]["MaterialWidgets"][selectedItem.text(0)]))
                self.basedataStackedWidget.setCurrentWidget(self.baseWidgets[parentSelectedItem.text(0)]["MaterialWidgets"][selectedItem.text(0)])

    def showContextMenu(self, position):
    	logging.debug("MainApp:showContextMenu() instantiated: " + str(position))
    	if(self.experimentTree.itemAt(position) == None):
    		self.blankTreeContextMenu.popup(self.experimentTree.mapToGlobal(position))
    	elif(self.experimentTree.itemAt(position).parent() == None):
    		self.experimentContextMenu.popup(self.experimentTree.mapToGlobal(position))
    	else:
    		self.itemContextMenu.popup(self.experimentTree.mapToGlobal(position))
    
    def addExperimentActionEvent(self):
        logging.debug("MainApp:addExperimentActionEvent() instantiated")
        configname = ExperimentAddDialog().experimentAddDialog(self, self.baseWidgets.keys())
        
        if configname != None:
            logging.debug("configureVM(): OK pressed and valid configname entered: " + str(configname))
        else:
            logging.debug("configureVM(): Cancel pressed or no VM selected")
            return
        
        ##Now add the item to the tree widget and create the baseWidget
        configTreeWidgetItem = QtWidgets.QTreeWidgetItem(self.experimentTree)
        configTreeWidgetItem.setText(0,configname)
        self.experimentActionsWidget.addExperimentItem(configname)
        self.connectionWidget.addExperimentItem(configname)
        # Base Config Widget 
        self.baseWidget = BaseWidget(self, configname, configname)
        self.baseWidgets[configname] = {"BaseWidget": {}, "VMWidgets": {}, "MaterialWidgets": {} }
        self.baseWidgets[configname]["BaseWidget"] = self.baseWidget
        self.basedataStackedWidget.addWidget(self.baseWidget)
        self.statusBar.showMessage("Added new experiment: " + str(configname))

    def importActionEvent(self):
        logging.debug("MainApp:importActionEvent() instantiated")
        #Check if it's the case that an experiment name was selected
        confignamesChosen = PackageImportDialog().packageImportDialog(self, self.baseWidgets.keys())
        if confignamesChosen == []:
            logging.debug("importActionEvent(): Canceled or a file could not be imported. make sure file exists.")
            return
        #for fileChosen in filesChosen:
        logging.debug("MainApp: importActionEvent(): Files choosen (getting only first): " + confignamesChosen)
        firstConfignameChosen = confignamesChosen
        self.loadConfigname(firstConfignameChosen)
        #Add the items to the tree
        self.statusBar.showMessage("Imported " + firstConfignameChosen)

    def addVMActionEvent(self):
        logging.debug("MainApp:addVMActionEvent() instantiated")
        selectedItem = self.experimentTree.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:addVMActionEvent no configurations left")
            self.statusBar.showMessage("Could not add VM. No configuration items selected or available.")
            return
        selectedItemName = selectedItem.text(0)
        #Now allow the user to choose the VM:
        (response, vmsChosen) = VMRetrieveDialog(self).exec_()
        
        if response == QMessageBox.Ok and vmsChosen != None:
            logging.debug("configureVM(): OK pressed and VMs selected " + str(vmsChosen))
        else:
            logging.debug("configureVM(): Cancel pressed or no VM selected")
            return

        if vmsChosen == []:
            logging.debug("configureVM(): Canceled or a file could not be added. Try again later or check permissions")
            return

        for vmChosen in vmsChosen:
            logging.debug("MainApp: addVMActionEvent(): File choosen: " + str(vmChosen))
            #Add the item to the tree
            vmItem = QtWidgets.QTreeWidgetItem(selectedItem)
            vmlabel = "V: " + vmChosen
            vmItem.setText(0,vmlabel)
            # VM Config Widget
            #Now add the item to the stack and list of baseWidgets
            vmjsondata = {"name": vmChosen}
            vmWidget = VMWidget(self, selectedItemName, vmChosen, vmjsondata)
            self.baseWidgets[selectedItemName]["VMWidgets"][vmlabel] = vmWidget
            self.basedataStackedWidget.addWidget(vmWidget)
        #Now add data to the experimentActionWidget associated with the current config
        #Check if it's the case that an experiment name was selected
        parentSelectedItem = selectedItem.parent()
        if parentSelectedItem != None:
            selectedItem = parentSelectedItem
        configname = selectedItem.text(0)
        config_jsondata = self.getWritableData(configname)
        self.experimentActionsWidget.resetExperiment(configname, config_jsondata=config_jsondata)
        self.connectionWidget.resetExperiment(configname, config_jsondata=config_jsondata)
        self.statusBar.showMessage("Added " + str(len(vmsChosen)) + " VM files to experiment: " + str(selectedItemName))

    def startHypervisorActionEvent(self):
        logging.debug("MainApp:startHypervisorActionEvent() instantiated")
        logging.debug("MainApp:startHypervisorActionEvent no configurations left")

        # Try to open the hypervisor and check if it worked or not
        result = HypervisorOpenDialog().hypervisorOpenDialog(self)
        if result != "success":
            logging.debug("startHypervisorActionEvent(): Could not start the hypervisor")
            self.statusBar.showMessage("Hypervisor could not be started.")
            return
        
        self.statusBar.showMessage("Started hypervisor.")

    def addMaterialActionEvent(self):
        logging.debug("MainApp:addMaterialActionEvent() instantiated")
        selectedItem = self.experimentTree.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:addMaterialActionEvent no configurations left")
            self.statusBar.showMessage("Could not add item. No configuration items selected or available.")
            return

        selectedItemName = selectedItem.text(0)
        #Check if it's the case that an experiment name was selected
        filesChosen = MaterialAddFileDialog().materialAddFileDialog(selectedItemName)
        if filesChosen == []:
            logging.debug("addMaterialActionEvent(): Canceled or a file could not be added. Try again later or check permissions")
            return
        for fileChosen in filesChosen:
            fileChosen = os.path.basename(fileChosen)
            logging.debug("MainApp: addMaterialActionEvent(): File choosen: " + fileChosen)
            #Add the item to the tree
            material_item = QtWidgets.QTreeWidgetItem(selectedItem)
            materiallabel = "M: " + fileChosen
            material_item.setText(0,materiallabel)
            # Material Config Widget
            #Now add the item to the stack and list of baseWidgets
            materialsjsondata = {"name": fileChosen}
            materialWidget = MaterialWidget(self, selectedItemName, fileChosen, materialsjsondata)
            self.baseWidgets[selectedItem.text(0)]["MaterialWidgets"][materiallabel] = materialWidget
            self.basedataStackedWidget.addWidget(materialWidget)
        self.statusBar.showMessage("Added " + str(len(filesChosen)) + " material files to experiment: " + str(selectedItemName))


    def removeExperimentItemActionEvent(self):
        logging.debug("MainApp:removeExperimentItemActionEvent() instantiated")
        selectedItem = self.experimentTree.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:onItemSelected no configurations left")
            self.statusBar.showMessage("Could not remove. No configuration items selected or available.")
            return

        selectedItemName = selectedItem.text(0)
        #Check if it's the case that an experiment name was selected
        parentSelectedItem = selectedItem.parent()
        if(parentSelectedItem == None):
            #A base widget was selected
            successfilenames = ExperimentRemoveFileDialog().experimentRemoveFileDialog(selectedItemName)
            if successfilenames == [] or successfilenames == "":
                logging.debug("removeExperimentItemActionEvent(): Canceled or a file could not be removed. Try again later or check permissions")
                return

            self.experimentTree.invisibleRootItem().removeChild(selectedItem)
            self.basedataStackedWidget.removeWidget(self.baseWidgets[selectedItemName]["BaseWidget"])
            del self.baseWidgets[selectedItemName]
            self.experimentActionsWidget.removeExperimentItem(selectedItemName)
            self.experimentActionsWidget.removeExperimentItem(selectedItemName)
            self.statusBar.showMessage("Removed experiment: " + str(selectedItemName))
        else:
            #Check if it's the case that a VM Name was selected
            if(selectedItem.text(0)[0] == "V"):
                parentSelectedItem.removeChild(selectedItem)
                configname = parentSelectedItem.text(0)
                self.basedataStackedWidget.removeWidget(self.baseWidgets[configname]["VMWidgets"][selectedItem.text(0)])
                del self.baseWidgets[configname]["VMWidgets"][selectedItem.text(0)]
                self.statusBar.showMessage("Removed VM: " + str(selectedItemName) + " from experiment: " + str(parentSelectedItem.text(0)))
                #Also remove from the experiment action widget:
                config_jsondata = self.getWritableData(configname)
                self.experimentActionsWidget.resetExperiment(configname, config_jsondata=config_jsondata)
                self.connectionWidget.resetExperiment(configname, config_jsondata=config_jsondata)

            #Check if it's the case that a Material Name was selected
            elif(selectedItem.text(0)[0] == "M"):
                materialName = selectedItemName.split("M: ")[1]
                successfilenames = MaterialRemoveFileDialog().materialRemoveFileDialog(parentSelectedItem.text(0), materialName)
                if successfilenames == []:
                    logging.debug("Canceled or a file could not be removed. Try again later or check permissions")
                    return
                parentSelectedItem.removeChild(selectedItem)
                self.basedataStackedWidget.removeWidget(self.baseWidgets[parentSelectedItem.text(0)]["MaterialWidgets"][selectedItem.text(0)])
                del self.baseWidgets[parentSelectedItem.text(0)]["MaterialWidgets"][selectedItem.text(0)]
                self.statusBar.showMessage("Removed Material: " + str(materialName) + " from experiment: " + str(parentSelectedItem.text(0)))
        
    def exportActionEvent(self):
        logging.debug("MainApp:exportActionEvent() instantiated")
        #Check if it's the case that an experiment name was selected
        selectedItem = self.experimentTree.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:exportActionEvent no configurations left")
            self.statusBar.showMessage("Could not export experiment. No configuration items selected or available.")
            return
        selectedItemName = selectedItem.text(0)

        folderChosen = PackageExportDialog().packageExportDialog(self, selectedItemName)
        if folderChosen == []:
            logging.debug("exportActionEvent(): Canceled or the experiment could not be exported. Check folder permissions.")
            return
        folderChosen = os.path.basename(folderChosen[0])
        
        logging.debug("MainApp: exportActionEvent(): File choosen: " + folderChosen)
        #Add the items to the tree

        self.statusBar.showMessage("Exported to " + folderChosen)

    def editPathActionEvent(self):
        logging.debug("MainApp:editPathActionEvent() instantiated")
        result = ConfigurationDialog(self).exec_()
        

    def closeEvent(self, event):
        logging.debug("MainApp:closeEvent(): instantiated")
        logging.debug("closeEvent(): returning accept")
        event.accept()
        qApp.quit()
        return
    
    def initMenu(self):               
        
        self.mainMenu = QMenuBar()
        self.fileMenu = self.mainMenu.addMenu("File")
        self.editMenu = self.mainMenu.addMenu("Edit")
        self.hypervisorMenu = self.mainMenu.addMenu("Hypervisor")
        
        self.newExperimentMenuButton = QAction(QIcon(), "New Experiment", self)
        self.newExperimentMenuButton.setShortcut("Ctrl+N")
        self.newExperimentMenuButton.setStatusTip("Create New Experiment")
        self.newExperimentMenuButton.triggered.connect(self.addExperimentActionEvent)
        self.fileMenu.addAction(self.newExperimentMenuButton)

        self.importExperimentMenuButton = QAction(QIcon(), "Import Experiment", self)
        self.importExperimentMenuButton.setShortcut("Ctrl+I")
        self.importExperimentMenuButton.setStatusTip("Import Experiment from RES File")
        self.importExperimentMenuButton.triggered.connect(self.importActionEvent)
        self.fileMenu.addAction(self.importExperimentMenuButton)

        self.saveExperimentMenuButton = QAction(QIcon(), "Save Experiment", self)
        self.saveExperimentMenuButton.setShortcut("Ctrl+I")
        self.saveExperimentMenuButton.setStatusTip("Save currently selected experiment")
        self.saveExperimentMenuButton.triggered.connect(self.saveExperimentButton)
        self.saveExperimentMenuButton.setEnabled(False)
        self.fileMenu.addAction(self.saveExperimentMenuButton)

        self.exitMenuButton = QAction(QIcon("exit24.png"), "Exit", self)
        self.exitMenuButton.setShortcut("Ctrl+Q")
        self.exitMenuButton.setStatusTip("Exit application")
        self.exitMenuButton.triggered.connect(self.close)
        self.fileMenu.addAction(self.exitMenuButton)

        self.pathMenuButton = QAction(QIcon(), "Edit Paths", self)
        self.pathMenuButton.setShortcut("Ctrl+E")
        self.pathMenuButton.setStatusTip("Edit Paths")
        self.pathMenuButton.triggered.connect(self.editPathActionEvent)
        self.editMenu.addAction(self.pathMenuButton)

        self.startHypervisorMenuButton = QAction(QIcon(), "Instantiate Hypervisor", self)
        self.startHypervisorMenuButton.setShortcut("Ctrl+O")
        self.startHypervisorMenuButton.setStatusTip("Start the hypervisor that is currently configured")
        self.startHypervisorMenuButton.triggered.connect(self.startHypervisorActionEvent)
        self.hypervisorMenu.addAction(self.startHypervisorMenuButton)

    def getWritableData(self, configname):
        logging.debug("MainApp: getWritableData() instantiated")
        jsondata = {}
        jsondata["xml"] = {}
        #get baseWidget data
        baseWidget = self.baseWidgets[configname]["BaseWidget"]
        ###TODO: make this work for multiple experiments (current testing assumes only one)
        if isinstance(baseWidget, BaseWidget):
            jsondata["xml"] = baseWidget.getWritableData()
        ###Setup the dictionary
        if "testbed-setup" not in jsondata["xml"]:
            jsondata["xml"]["testbed-setup"] = {}
        if "vm-set" not in jsondata["xml"]["testbed-setup"]:
            jsondata["xml"]["testbed-setup"]["vm-set"] = {}
        if "vm" not in jsondata["xml"]["testbed-setup"]["vm-set"]:
            jsondata["xml"]["testbed-setup"]["vm-set"]["vm"] = []
        if "material" not in jsondata["xml"]["testbed-setup"]["vm-set"]:
            jsondata["xml"]["testbed-setup"]["vm-set"]["material"] = []

        for vmData in self.baseWidgets[configname]["VMWidgets"].values():
            jsondata["xml"]["testbed-setup"]["vm-set"]["vm"].append(vmData.getWritableData())
        for materialData in self.baseWidgets[configname]["MaterialWidgets"].values():
            jsondata["xml"]["testbed-setup"]["vm-set"]["material"].append(materialData.getWritableData())
        return jsondata

    def saveExperimentButton(self):
        logging.debug("MainApp: saveExperiment() instantiated")
        self.saveExperiment()

    def saveExperiment(self, configname=None):
        logging.debug("MainApp: saveExperiment() instantiated")
        selectedItem = self.experimentTree.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:onItemSelected no configurations left")
            self.statusBar.showMessage("Could not save. No configuration items selected or available.")
            return
        #Check if it's the case that an experiment name was selected
        parentSelectedItem = selectedItem.parent()
        if parentSelectedItem != None:
            selectedItem = parentSelectedItem
        configname = selectedItem.text(0)
        jsondata = self.getWritableData(configname)
        
        self.ec.writeExperimentXMLFileData(jsondata, configname)
        self.ec.writeExperimentJSONFileData(jsondata, configname)
        self.ec.getExperimentVMRolledOut(configname, jsondata, force_refresh=True)
        res = self.ec.getExperimentServerInfo(configname)
        #Now reset the experimentActions view
        self.experimentActionsWidget.resetExperiment(configname, jsondata)
        self.connectionWidget.resetExperiment(configname, jsondata)
        self.statusBar.showMessage("Succesfully saved experiment file for " + str(configname), 2000)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    appctxt = QApplication(sys.argv)
    gui = MainApp()
    QApplication.setStyle(QStyleFactory.create('Fusion')) 
    gui.show()
    exit_code = appctxt.exec_()
    sys.exit(exit_code)