from engine.Manager.VMManage.VMManage import VMManage

class VM:
    VM_STATE_RUNNING = 2
    VM_STATE_OFF = 3
    VM_STATE_SUSPENDED = 4
#    VM_STATE_ABORTED = 5
    VM_STATE_UNKNOWN = 6
    VM_STATE_OTHER = -2


    ###Start MACHINE_STATE DEFS#### (from https=//www.virtualbox.org/sdkref/_virtual_box_8idl.html)
    MachineState_Null = 0
    MachineState_PoweredOff = 1
    MachineState_Saved = 2
    MachineState_Teleported = 3

    MachineState_Aborted = 4
    MachineState_Running = 5
    MachineState_Paused = 6
    MachineState_Stuck = 7

    MachineState_Teleporting = 8
    MachineState_LiveSnapshotting = 9
    MachineState_Starting = 10
    MachineState_Stopping = 11

    MachineState_Saving = 12
    MachineState_Restoring = 13
    MachineState_TeleportingPausedVM = 14
    MachineState_TeleportingIn = 15

    MachineState_DeletingSnapshotOnline = 16
    MachineState_DeletingSnapshotPaused = 17
    MachineState_OnlineSnapshotting = 18
    MachineState_RestoringSnapshot = 19

    MachineState_DeletingSnapshot = 20
    MachineState_SettingUp = 21
    MachineState_Snapshotting = 22
    MachineState_FirstOnline = 5

    MachineState_LastOnline = 18
    MachineState_FirstTransient = 8
    MachineState_LastTransient = 22
    MACHINE_STATE = {0 : "MachineState_Null", 1: "MachineState_PoweredOff", 2: "MachineState_Saved", 3: "MachineState_Teleported" ,
    4: "MachineState_Aborted", 5: "MachineState_Running", 6: "MachineState_Paused", 7: "MachineState_Stuck",
    8: "MachineState_Teleporting", 9: "MachineState_LiveSnapshotting", 10: "MachineState_Starting", 11:"MachineState_Stopping",
    12: "MachineState_Saving", 13: "MachineState_Restoring", 14: "MachineState_TeleportingPausedVM", 15: "MachineState_TeleportingIn",
    16: "MachineState_DeletingSnapshotOnline", 17: "MachineState_DeletingSnapshotPaused", 18: "MachineState_OnlineSnapshotting", 19: "MachineState_RestoringSnapshot",
    20: "MachineState_DeletingSnapshot", 21: "MachineState_SettingUp", 22: "MachineState_Snapshotting"}
  #5: "MachineState_FirstOnline",  18: "MachineState_LastOnline", 8: "MachineState_FirstTransient", 22: "MachineState_LastTransient" : 22
    ####END MACHINE_STATE DEFS####

    
    def __init__(self):
        #TODO: think of making these into a dictionary entry
        self.name = ""
        self.UUID = ""
        self.setupStatus = VMManage.VM_SETUP_UNKNOWN
        self.state = "UNKNOWN"
        self.adaptorInfo = {} #list adaptors (strings)
        self.groups = ""#list groups (strings)
        self.latestSnapUUID = ""
