import logging
from gui.Dialogs.ChallengesActionDialog import ChallengesActionDialog

class ChallengesActions():

    def challengesActionEvent(self, parent, configname, actionlabelname, challengesserver, users_file="", itype="", name=""):
        logging.debug("challengesActionEvent(): showContextMenu(): instantiated")
        if "Create Users" in actionlabelname:
            self.challengesAction(parent, configname, "Add", challengesserver, users_file, itype, name)
        elif "Remove Users" in actionlabelname:
            self.challengesAction(parent, configname, "Remove", challengesserver, users_file, itype, name)
        elif "Clear All Entries" in actionlabelname:
            self.challengesAction(parent, configname, "Clear", challengesserver, users_file, itype, name)
        elif "Open Challengess" in actionlabelname:
            self.challengesAction(parent, configname, "Open", challengesserver, users_file, itype, name)

    def challengesAction(self, parent, configname, actionname, challengesserver, users_file, itype, name):
        logging.debug("connnectionAction(): showContextMenu(): instantiated")
        ChallengesActionDialog(parent, configname, actionname, challengesserver, users_file, itype, name).exec_()