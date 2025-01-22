from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QTableView, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox, QAbstractScrollArea)

import logging

class ChallengesStatsTreeWidget(QTableWidget):

    def __init__(self, parent):
        
        super(ChallengesStatsTreeWidget, self).__init__()
        logging.debug("Creating ChallengesTreeWidget")
    
        self.parent = parent
        self.setSortingEnabled(True)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setMinimumSize(750, 600)
        self.challengesList = []
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #self.setSelectionBehavior(QTableView.selectRow)

        self.setRowCount(0)
        self.setColumnCount(5)

        self.setHorizontalHeaderLabels(("ID", "Category", "Name", "Solves", "Value"))

        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 300)
        self.setColumnWidth(2, 300)
        self.setColumnWidth(3, 50)
        self.setColumnWidth(4, 50)

    def populateTreeStore(self, challengesList):
        self.challengesList = challengesList
        for challenge in self.challengesList:
            logging.debug("populateTreeStore(): working with: " + str(challenge))
            id = self.challengesList[challenge][0]
            category = self.challengesList[challenge][1]
            name =  self.challengesList[challenge][2]
            solves = self.challengesList[challenge][3]
            value = self.challengesList[challenge][4]
            
            rowPos = self.rowCount()
            self.insertRow(rowPos)
            
            self.idCell = QTableWidgetItem(str(id))
            self.idCell.setFlags(Qt.ItemIsEnabled)
            
            self.categoryCell = QTableWidgetItem(str(category))
            self.categoryCell.setFlags(Qt.ItemIsEnabled)

            self.nameCell = QTableWidgetItem(str(name))
            self.nameCell.setFlags(Qt.ItemIsEnabled)
            
            self.solvesCell = QTableWidgetItem(str(solves))
            self.solvesCell.setFlags(Qt.ItemIsEnabled)
            
            self.valueCell = QTableWidgetItem(str(value))
            self.valueCell.setFlags(Qt.ItemIsEnabled)
            
            self.setItem(rowPos, 0, self.idCell)
            self.setItem(rowPos, 1, self.categoryCell)
            self.setItem(rowPos, 2, self.nameCell)
            self.setItem(rowPos, 3, self.solvesCell)
            self.setItem(rowPos, 4, self.valueCell)