from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QObject
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QDialogButtonBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QTableView, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox)

import logging

class ExperimentActionsVMStatusWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, configname=None, widgetname="", rolledoutjson=None, interest_vmnames = []):
        logging.debug("ExperimentActionsBaseWidgets instantiated")
        if configname == None:
            logging.error("configname cannot be empty")
            return None
        QtWidgets.QWidget.__init__(self, parent=None)
        self.widgetname = widgetname
        self.configname = configname
        self.rolledoutjson = rolledoutjson

        self.eco = ExperimentConfigIO()

        self.setWindowTitle("ExperimentActionsBaseWidgets")
        self.setObjectName("ExperimentActionsBaseWidgets")
        self.layoutWidget = QtWidgets.QWidget()
        self.layoutWidget.setObjectName("layoutWidget")
        self.outerVertBox = QtWidgets.QVBoxLayout()
        self.outerVertBox.setObjectName("outerVertBox")
        self.layoutWidget.setLayout(self.outerVertBox)

        self.vmStatusTable = QtWidgets.QTableWidget(parent)
        self.vmStatusTable.setObjectName("vmStatusTable")
        self.vmStatusTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vmStatusTable.setSelectionBehavior(QTableView.SelectRows)
        
        self.vmStatusTable.setRowCount(0)
        self.vmStatusTable.setColumnCount(4)
        self.vmStatusTable.setHorizontalHeaderLabels(("VM Name", "UUID", "Username", "Status"))
        
        self.vmStatusTable.setSortingEnabled(True)
        self.outerVertBox.addWidget(self.vmStatusTable)

        self.setLayout(self.outerVertBox)
        self.retranslateUi(rolledoutjson, interest_vmnames)

    def retranslateUi(self, rolledoutjson, interest_vmnames):
        logging.debug("BaseWidget: retranslateUi(): instantiated")
        
        ###Fill in data from json
        (template_vms, num_clones) = rolledoutjson
        
        for template_vm in template_vms:
            for cloned_vm in template_vms[template_vm]:
                if interest_vmnames == [] or cloned_vm["name"] in interest_vmnames:
                    rowPos = self.vmStatusTable.rowCount()
                    self.vmStatusTable.insertRow(rowPos)
                    vmCell = QTableWidgetItem(str(cloned_vm["name"]))
                    uuidCell = QTableWidgetItem(str("refresh req."))
                    statusCell = QTableWidgetItem(str("refresh req."))
                    statusCell.setFlags(Qt.ItemIsEnabled)
                    self.vmStatusTable.setItem(rowPos, 0, vmCell)
                    self.vmStatusTable.setItem(rowPos, 1, uuidCell)
                    self.vmStatusTable.setItem(rowPos, 2, statusCell)
                    self.vmStatusTable.resizeColumnToContents(0)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = ExperimentActionsVMStatusWidget()
    ui.show()
    sys.exit(app.exec_())
