import logging
from gui.Dialogs.ExperimentActionDialog import ExperimentActionDialog

class ExperimentActions():

    def experimentActionEvent(self, configname, actionlabelname, itype, name):
        logging.debug("cloneExperimentActionEvent(): showContextMenu(): instantiated")
        if "Signal - Create Clone" in actionlabelname:
            self.experimentAction(configname, "Create Experiment", itype, name)
        elif "Signal - Start VM" in actionlabelname:
            self.experimentAction(configname, "Start Experiment", itype, name)
        elif "Signal - Suspend & Save State" in actionlabelname:
            self.experimentAction(configname, "Suspend Experiment", itype, name)
        elif "Signal - Pause VM" in actionlabelname:
            self.experimentAction(configname, "Pause Experiment", itype, name)
        elif "Signal - Restore Snapshot" in actionlabelname:
            self.experimentAction(configname, "Restore Experiment", itype, name)
        elif "Signal - Snapshot VM" in actionlabelname:
            self.experimentAction(configname, "Snapshot Experiment", itype, name)
        elif "Signal - Delete Clone" in actionlabelname:
            self.experimentAction(configname, "Remove Experiment", itype, name)            
        elif "Signal - Power Off VM" in actionlabelname:
            self.experimentAction(configname, "Stop Experiment", itype, name)

    def experimentAction(self, configname, actionname, itype, name):
        logging.debug("experimentAction(): showContextMenu(): instantiated")
        ExperimentActionDialog().experimentActionDialog(configname, actionname, itype, name)