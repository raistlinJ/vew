import logging
from gui.Dialogs.ChallengesActionDialog import ChallengesActionDialog

class ChallengesActions():

    def challengesActionEvent(self, parent, configname, actionlabelname, challengesserver, users_file="", itype="", name=""):
        logging.debug("challengesActionEvent(): showContextMenu(): instantiated")
        if "Create Users" in actionlabelname:
            self.challengesAction(parent, configname, "Add", challengesserver, users_file, itype, name)
        elif "Remove Users" in actionlabelname:
            self.challengesAction(parent, configname, "Remove", challengesserver, users_file, itype, name)
        elif "Clear All Users on Server" in actionlabelname:
            self.challengesAction(parent, configname, "Clear", challengesserver, users_file, itype, name)
        elif "Open User in Browser" in actionlabelname:
            self.challengesAction(parent, configname, "OpenUsers", challengesserver, users_file, itype, name)

    def challengesAction(self, parent, configname, actionname, challengesserver, users_file, itype, name):
        logging.debug("challengesAction(): showContextMenu(): instantiated")
        ChallengesActionDialog(parent, configname, actionname, challengesserver, users_file, itype, name).exec_()