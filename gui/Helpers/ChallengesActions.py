import logging
from gui.Dialogs.ChallengesActionDialog import ChallengesActionDialog

class ChallengesActions():

    def challengesActionEvent(self, parent, configname, actionlabelname, vmHostname, rdpBrokerHostname, users_file="", itype="", name=""):
        logging.debug("challengesActionEvent(): showContextMenu(): instantiated")
        if "Create Users" in actionlabelname:
            self.challengesAction(parent, configname, "Add", vmHostname, rdpBrokerHostname, users_file, itype, name)
        elif "Remove Users" in actionlabelname:
            self.challengesAction(parent, configname, "Remove", vmHostname, rdpBrokerHostname, users_file, itype, name)
        elif "Clear All Entries" in actionlabelname:
            self.challengesAction(parent, configname, "Clear", vmHostname, rdpBrokerHostname, users_file, itype, name)
        elif "Open Challengess" in actionlabelname:
            self.challengesAction(parent, configname, "Open", vmHostname, rdpBrokerHostname, users_file, itype, name)

    def challengesAction(self, parent, configname, actionname, vmHostname, rdpBrokerHostname, users_file, itype, name):
        logging.debug("connnectionAction(): showContextMenu(): instantiated")
        ChallengesActionDialog(parent, configname, actionname, vmHostname, rdpBrokerHostname, users_file, itype, name).exec_()