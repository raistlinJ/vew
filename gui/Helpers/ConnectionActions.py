import logging
from gui.Dialogs.ConnectionActionDialog import ConnectionActionDialog

class ConnectionActions():

    def connectionActionEvent(self, parent, configname, actionlabelname, vmHostname, rdpBrokerHostname, itype, name):
        logging.debug("connectionActionEvent(): showContextMenu(): instantiated")
        if "Create Users" in actionlabelname:
            self.connectionAction(parent, configname, "Add", vmHostname, rdpBrokerHostname, itype, name)
        elif "Remove Users" in actionlabelname:
            self.connectionAction(parent, configname, "Remove", vmHostname, rdpBrokerHostname, itype, name)
        elif "Clear All Entries" in actionlabelname:
            self.connectionAction(parent, configname, "RemoveAll", vmHostname, rdpBrokerHostname, itype, name)

    def connectionAction(self, parent, configname, actionname, vmHostname, rdpBrokerHostname, itype, name):
        logging.debug("connnectionAction(): showContextMenu(): instantiated")
        ConnectionActionDialog(parent, configname, actionname, vmHostname, rdpBrokerHostname).exec_()