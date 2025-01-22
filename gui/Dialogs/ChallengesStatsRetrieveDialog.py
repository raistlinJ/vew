from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

from engine.Engine import Engine
import time
from engine.Configuration.SystemConfigIO import SystemConfigIO
from gui.Dialogs.ChallengesStatsRetrievingDialog import ChallengesStatsRetrievingDialog
from gui.Widgets.ChallengesWidgets.ChallengesStatsTreeWidget import ChallengesStatsTreeWidget
import logging
import configparser

class ChallengesStatsRetrieveDialog(QDialog):

    def __init__(self, parent, args):
        logging.debug("ChallengesStatsRetrieveDialog(): instantiated")
        super(ChallengesStatsRetrieveDialog, self).__init__(parent)      
        self.parent = parent
        self.args = args
        self.s = SystemConfigIO()
        self.challenges = {}
        self.challengesNames = []

        self.buttons = QDialogButtonBox()
        self.ok_button = self.buttons.addButton( self.buttons.Ok )
        # self.ok_button.setEnabled(False)
        # self.buttons.addButton( self.buttons.Cancel )

        self.buttons.accepted.connect( self.accept )
        # self.buttons.rejected.connect( self.reject )

        self.setWindowTitle("Challenge Statistics")
        #self.setFixedSize(550, 300)

        self.box_main_layout = QGridLayout()
        self.box_main = QWidget()
        self.box_main.setLayout(self.box_main_layout)

        #label = QLabel("Select Challenges Stats to add")
        #self.box_main_layout.addWidget(label, 1, 0)
        
        self.setLayout(self.box_main_layout)       

#####
        # Here we will place the tree view
        self.treeWidget = ChallengesStatsTreeWidget(self)
        self.treeWidget.itemSelectionChanged.connect(self.onItemSelected)
        
        self.box_main_layout.addWidget(self.treeWidget, 1, 0)
        
        s = ChallengesStatsRetrievingDialog(self.parent, self.args).exec_()
        if s != None and 'challengesStats' in s:
            self.challenges = s["challengesStats"]
        else:
            logging.warning("ChallengesStatsRetrieveDialog(): No Challenges were retrieved")
            noChallengesDialog = QMessageBox.critical(self, "Challenges Error", "No Challenges were found. The system may not have challenges or your credentials may be incorrect.", QMessageBox.Ok)
            return
        if len(self.challenges) == 0:
            logging.warning("ChallengesStatsRetrieveDialog(): No Challenges were retrieved")
            noChallengesDialog = QMessageBox.critical(self, "Challenges Error", "No Challenges were found. The system may not have challenges or your credentials may be incorrect.", QMessageBox.Ok)
            return

        #self.treeWidget.setSelectionMode(ChallengesTreeWidget.MultiSelection)
        self.treeWidget.populateTreeStore(self.challenges)      
        
        #self.treeWidget.adjustSize()
        #self.adjustSize()
        
#####
        self.box_main_layout.addWidget(self.buttons, 2, 0)

        self.setLayout(self.box_main_layout)

    def exec_(self):
        logging.debug("ChallengesStatsRetrieveDialog(): exec_() instantiated")
        result = super(ChallengesStatsRetrieveDialog, self).exec_()
        if str(result) == str(1):        
            logging.debug("dialog_response(): OK was pressed")
#            self.configuringChallenges()
            return (QMessageBox.Ok, self.challengesNames)
        return (QMessageBox.Cancel, self.challengesNames)
        
    def onItemSelected(self):
        logging.debug("ChallengesStatsRetrieveDialog(): onItemSelected() instantiated")
        selectedItems = self.treeWidget.selectedItems()
        logging.debug("ChallengesStatsRetrieveDialog(): onItemSelected() selected items: " + str(selectedItems))

        if len(selectedItems) > 0:
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)
            return
        self.challengesNames = []
        for selectedItem in selectedItems:
            self.challengesNames.append(selectedItem.text())

                    