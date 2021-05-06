# from PyQt5.QtWidgets import QFileDialog, QWidget
# from gui.Dialogs.ConnectionOpeningDialog import ConnectionOpeningDialog
# from engine.Configuration.SystemConfigIO import SystemConfigIO
# import os
# import logging

# class ConnectionOpenDialog:
#     def connectionOpenDialog(self, parent):       
#         logging.debug("connectionOpenDialog(): Instantiated")
#         self.parent = parent
#         self.s = SystemConfigIO()
#         #get required info for opening the connection (path, method)

#         result = self.openConnection(self.s.getConfig()["BROWSER"]["BROWSER_PATH"])
#         logging.debug("connectionOpenDialog(): Completed")
#         return result

#     def openConnection(self, pathToConnection, args):
#         logging.debug("openConnection(): instantiated")
#         result = ConnectionOpeningDialog(self.parent, pathToConnection, args).exec_()
#         return result


