from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QTableView, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

import logging

class VMTreeWidget(QTableWidget):

    def __init__(self, parent):
        
        super(VMTreeWidget, self).__init__()
        logging.debug("Creating VMTreeWidget")

        self.parent = parent
        self.vmList = []
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QTableView.SelectRows)

        self.setRowCount(0)
        self.setColumnCount(2)

        self.setHorizontalHeaderLabels(("VM Name", "VM Status"))
        #header = self.horizontalHeader()
        #header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        #header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        #header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def populateTreeStore(self, vmList):
        self.vmList = vmList
        for vm in self.vmList:
            logging.debug("populateTreeStore(): working with: " + str(vm))
            #adaptor = str("1 - " + self.vmList[vm]["adaptorInfo"]["1"])
            status = self.vmList[vm]["vmState"]
            #adaptors = []
            #QMessageBox.question(self, 'PyQt5 message', str(self.vmList[vm]["adaptorInfo"]), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                               
            rowPos = self.rowCount()
            self.insertRow(rowPos)
            # self.comboBox = QComboBox()
            # self.comboBox.setProperty('vmName',str(vm))
            
            #self.comboBox.currentIndexChanged.connect(self.comboSelectionChanged)
            # atLeastOneAdaptor = False
            # for num,adaptor in self.vmList[vm]["adaptorInfo"].items():
            #     if "none" in adaptor:
            #         adaptor = num + " - *adaptor disabled*"
            #         self.comboBox.addItem(adaptor)
            #         self.comboBox.model().item(self.comboBox.count()-1).setEnabled(False)
            #     else:
            #         atLeastOneAdaptor = True
            #         adaptor = num + " - " + adaptor
            #         self.comboBox.addItem(adaptor)          
            
            self.vmCell = QTableWidgetItem(str(vm))
            self.statusCell = QTableWidgetItem(str(status))
            self.statusCell.setFlags(Qt.ItemIsEnabled)
            
            # if atLeastOneAdaptor == False:
            #     self.vmCell = QTableWidgetItem(str(vm))
            #     self.vmCell.setBackground(Qt.lightGray)
            #     self.statusCell = QTableWidgetItem("No adaptors enabled")
            #     self.statusCell.setFlags(Qt.ItemIsEnabled)
            #     self.statusCell.setBackground(Qt.lightGray)
            
            #     self.alternateAdaptor = QTableWidgetItem("No adaptors enabled")      
            #     self.alternateAdaptor.setBackground(Qt.lightGray)
            #     self.alternateAdaptor.setFlags(Qt.ItemIsEnabled)
                
            #     self.setItem(rowPos, 0, self.vmCell)
            #     self.setItem(rowPos, 1, self.alternateAdaptor)
            #     self.setItem(rowPos, 2, self.statusCell)
            # elif str(status) == "Running (not selectable)":
            #     self.vmCell = QTableWidgetItem(str(vm))
            #     self.vmCell.setBackground(Qt.lightGray)
            #     self.statusCell = QTableWidgetItem(str(status))
            #     self.statusCell.setFlags(Qt.ItemIsEnabled)
            #     self.statusCell.setBackground(Qt.lightGray)
                
            #     self.alternateAdaptor = QTableWidgetItem("VM is running")      
            #     self.alternateAdaptor.setBackground(Qt.lightGray)
            #     self.alternateAdaptor.setFlags(Qt.ItemIsEnabled)
                
            #     self.setItem(rowPos, 0, self.vmCell)
            #     self.setItem(rowPos, 1, self.alternateAdaptor)
            #     self.setItem(rowPos, 2, self.statusCell)
            # else:
            self.vmCell = QTableWidgetItem(str(vm))
            self.statusCell = QTableWidgetItem(str(status))
            self.statusCell.setFlags(Qt.ItemIsEnabled)
        
            self.setItem(rowPos, 0, self.vmCell)
            #self.setCellWidget(rowPos, 1, self.comboBox)
            self.setItem(rowPos, 1, self.statusCell)

#    def comboSelectionChanged(self):
#        logging.debug("comboSelectionChanged(): instantiated")
#        comboBox = self.sender()
#        chosenAdaptor = comboBox.currentIndex()      
#        vmName = comboBox.property('vmName')
#        QMessageBox.question(self, 'PyQt5 message', str(vmName) + " " + str(chosenAdaptor), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)