import sys
import logging
import json
import os

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
from gui.Widgets.ExperimentActionsWidget import ExperimentActionsWidget
from gui.Widgets.ManagerBox import ManagerBox
from engine.Configuration.SystemConfigIO import SystemConfigIO
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from gui.Dialogs.MaterialAddFileDialog import MaterialAddFileDialog
from gui.Dialogs.MaterialRemoveFileDialog import MaterialRemoveFileDialog
from gui.Dialogs.ExperimentRemoveFileDialog import ExperimentRemoveFileDialog
from gui.Dialogs.VMRetreiveDialog import VMRetrieveDialog
from gui.Dialogs.ExperimentAddDialog import ExperimentAddDialog
from gui.Dialogs.ConnectionActionDialog import ConnectionActionDialog
from gui.Dialogs.PackageImportDialog import PackageImportDialog
from gui.Dialogs.PackageExportDialog import PackageExportDialog

# Handle high resolution displays:
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

class MainApp(QMainWindow):
    def __init__(self, parent=None):
        logging.debug("MainApp:init() instantiated")
        super(MainApp, self).__init__(parent)
        self.baseWidgets = {}
        self.vmWidgets = {}
        self.materialWidgets = {}
        self.cf = SystemConfigIO()
        self.ec = ExperimentConfigIO()
        self.statusBar = self.statusBar()
        
        self.setFixedSize(670,565)
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
        self.windowBoxHLayout.setContentsMargins(0, 0, 0, 0)
        self.windowBoxHLayout.setObjectName("windowBoxHLayout")
        self.windowWidget.setLayout(self.windowBoxHLayout)

        self.experimentTree = QtWidgets.QTreeWidget()
        self.experimentTree.itemSelectionChanged.connect(self.onItemSelected)
        self.experimentTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.experimentTree.customContextMenuRequested.connect(self.showContextMenu)
        self.experimentTree.setEnabled(True)
        self.experimentTree.setMaximumSize(200,521)
        self.experimentTree.setObjectName("experimentTree")
        self.experimentTree.headerItem().setText(0, "Experiments")
        self.experimentTree.setSortingEnabled(False)
        self.windowBoxHLayout.addWidget(self.experimentTree)
        
        self.basedataStackedWidget = QStackedWidget()
        self.basedataStackedWidget.setObjectName("basedataStackedWidget")
        self.windowBoxHLayout.addWidget(self.basedataStackedWidget)
        self.tabWidget.addTab(self.windowWidget, "Configuration")

        # VBox Actions Tab
        self.experimentActionsWidget = ExperimentActionsWidget(statusBar=self.statusBar)
        self.experimentActionsWidget.setObjectName("experimentActionsWidget")
        self.tabWidget.addTab(self.experimentActionsWidget, "Experiment Actions")      

        ##Create the bottom layout so that we can access the status bar
        self.bottomLayout = QHBoxLayout()
        self.statusBar.showMessage("Loading GUI...")
        self.bottomLayout.addWidget(self.statusBar)
        self.saveButton = QtWidgets.QPushButton("Save Current")
        self.saveButton.clicked.connect(self.buttonSaveExperiment)
        self.saveButton.setEnabled(False)
        self.bottomLayout.addWidget(self.saveButton)

        self.populateUi()
        self.setupContextMenus()

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addLayout(self.bottomLayout)

        self.outerBox = QWidget()
        self.outerBox.setLayout(self.mainLayout)
        self.setCentralWidget(self.outerBox)
        self.tabWidget.setCurrentIndex(0)

        #self.statusBar.showMessage("Finished Loading GUI Components")

    def readSystemConfig(self):
        logging.debug("MainApp:readSystemConfig() instantiated")
        self.vboxPath = self.cf.getConfig()['VBOX_LINUX']['VBOX_PATH']
        self.experimentPath = self.cf.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH']
        self.statusBar.showMessage("Finished reading system config")
    
    def setupContextMenus(self):
        logging.debug("MainApp:setupContextMenus() instantiated")
    # Context menu for blank space
        self.blankTreeContextMenu = QtWidgets.QMenu()
       	self.addExperiment = self.blankTreeContextMenu.addAction("New Experiment")
       	self.addExperiment.triggered.connect(self.addExperimentActionEvent)
        self.importExperiment = self.blankTreeContextMenu.addAction("Import Experiment from EBX archive")
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
        self.guacContextSubMenu = QtWidgets.QMenu()
        self.experimentContextMenu.addMenu(self.guacContextSubMenu)
        self.guacContextSubMenu.setTitle("CIT Remote Access")
        self.createGuac = self.guacContextSubMenu.addAction("Create Users")
        self.createGuac.triggered.connect(self.createGuacActionEvent)
        self.removeGuac = self.guacContextSubMenu.addAction("Remove Users")
        self.removeGuac.triggered.connect(self.removeGuacActionEvent)
        self.clearGuac = self.guacContextSubMenu.addAction("Clear All Entries")
        self.clearGuac.triggered.connect(self.clearGuacActionEvent)

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
        [xmlExperimentFilenames, xmlExperimentNames] = self.ec.getExperimentXMLFilenames()
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

        configTreeWidgetItem = QtWidgets.QTreeWidgetItem(self.experimentTree)
        configTreeWidgetItem.setText(0,configname)
        self.experimentActionsWidget.addExperimentItem(configname)
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
                    vmWidget = VMWidget(self, configname, vm["name"], vm)
                    self.baseWidgets[configname]["VMWidgets"][vmlabel] = vmWidget
                    self.basedataStackedWidget.addWidget(vmWidget)
            else:
                vm_item = QtWidgets.QTreeWidgetItem(configTreeWidgetItem)
                vmlabel = "V: " + vmsjsondata["name"]
                vm_item.setText(0,vmlabel)
                # VM Config Widget
                vmWidget = VMWidget(self, configname, vmsjsondata["name"], vmsjsondata)
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
                    materialWidget = MaterialWidget(self, configname, material["name"], material)
                    self.baseWidgets[configname]["MaterialWidgets"][materiallabel] = materialWidget
                    self.basedataStackedWidget.addWidget(materialWidget)
            else:
                material_item = QtWidgets.QTreeWidgetItem(configTreeWidgetItem)
                materiallabel = "M: " + materialsjsondata["name"]
                material_item.setText(0,materiallabel)
                # Material Config Widget
                materialWidget = MaterialWidget(self, configname, materialsjsondata["name"], materialsjsondata)
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
        # Now enable the save button
        self.saveButton.setEnabled(True)
        #Check if it's the case that an experiment name was selected
        parentSelectedItem = selectedItem.parent()
        if(parentSelectedItem == None):
            #A base widget was selected
            self.baseWidget.baseGroupNameLineEdit.setText(selectedItem.text(0))
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
        self.statusBar.showMessage("Added " + str(len(vmsChosen)) + " VM files to experiment: " + str(selectedItemName))


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

    def createGuacActionEvent(self):
        logging.debug("MainApp:addMaterialActionEvent() instantiated")
        selectedItem = self.experimentTree.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:createGuacActionEvent no configuration selected")
            self.statusBar.showMessage("Could complete connection action. No configuration items selected or available.")
            return
        selectedItemName = selectedItem.text(0)
        connResult = ConnectionActionDialog(self, selectedItemName, "Add").exec_()

    def removeGuacActionEvent(self):
        logging.debug("MainApp:removeGuacActionEvent() instantiated")
        selectedItem = self.experimentTree.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:removeGuacActionEvent no configuration selected")
            self.statusBar.showMessage("Could complete connection action. No configuration items selected or available.")
            return
        selectedItemName = selectedItem.text(0)
        connResult = ConnectionActionDialog(self, selectedItemName, "Remove").exec_()

    def clearGuacActionEvent(self):
        logging.debug("MainApp:clearGuacActionEvent() instantiated")
        selectedItem = self.experimentTree.currentItem()
        if selectedItem == None:
            logging.debug("MainApp:clearGuacActionEvent no configuration selected")
            self.statusBar.showMessage("Could complete connection action. No configuration items selected or available.")
            return
        selectedItemName = selectedItem.text(0)
        connResult = ConnectionActionDialog(self, selectedItemName, "Clear").exec_()

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
            self.statusBar.showMessage("Removed experiment: " + str(selectedItemName))
        else:
            #Check if it's the case that a VM Name was selected
            if(selectedItem.text(0)[0] == "V"):
                parentSelectedItem.removeChild(selectedItem)
                self.basedataStackedWidget.removeWidget(self.baseWidgets[parentSelectedItem.text(0)]["VMWidgets"][selectedItem.text(0)])
                del self.baseWidgets[parentSelectedItem.text(0)]["VMWidgets"][selectedItem.text(0)]
                self.statusBar.showMessage("Removed VM: " + str(selectedItemName) + " from experiment: " + str(parentSelectedItem.text(0)))
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

    def closeEvent(self, event):
        logging.debug("MainApp:closeEvent(): instantiated")
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

    def buttonSaveExperiment(self):
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
        self.statusBar.showMessage("Succesfully saved experiment file for " + str(configname), 2000)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    appctxt = ApplicationContext()
    app = MainApp()
    QApplication.setStyle(QStyleFactory.create('Fusion')) 
    app.show()
    sys.exit(appctxt.app.exec_())
