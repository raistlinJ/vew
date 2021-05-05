import logging
from gui.Dialogs.ConnectionActionDialog import ConnectionActionDialog

class ConnectionActions():

    def connectionActionEvent(self, parent, configname, actionlabelname, vmHostname, rdpBrokerHostname, users_file="", itype="", name=""):
        logging.debug("connectionActionEvent(): showContextMenu(): instantiated")
        if "Create Users" in actionlabelname:
            self.connectionAction(parent, configname, "Add", vmHostname, rdpBrokerHostname, users_file, itype, name)
        elif "Remove Users" in actionlabelname:
            self.connectionAction(parent, configname, "Remove", vmHostname, rdpBrokerHostname, users_file, itype, name)
        elif "Clear All Entries" in actionlabelname:
            self.connectionAction(parent, configname, "Clear", vmHostname, rdpBrokerHostname, users_file, itype, name)
        elif "Open Connections" in actionlabelname:
            self.connectionAction(parent, configname, "Open", vmHostname, rdpBrokerHostname, users_file, itype, name)

    def connectionAction(self, parent, configname, actionname, vmHostname, rdpBrokerHostname, users_file, itype, name):
        logging.debug("connnectionAction(): showContextMenu(): instantiated")
        ConnectionActionDialog(parent, configname, actionname, vmHostname, rdpBrokerHostname, users_file, itype, name).exec_()