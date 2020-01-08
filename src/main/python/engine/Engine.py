import logging
import shlex
import argparse
import sys
from time import sleep
from engine.Manager.ConnectionManage.ConnectionManageGuacRDP import ConnectionManageGuacRDP
from engine.Manager.PackageManage.PackageManageVBox import PackageManageVBox
from engine.Manager.ExperimentManage.ExperimentManageVBox import ExperimentManageVBox
import threading

class Engine:
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def getInstance(cls):
        logging.debug("getInstance() Engine: instantiated")
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

    def __init__(self):
        #Virtually private constructor
        #if Engine.__singleton_instance != None:
        #    raise Exception("Use the getInstance method to obtain an instance of this class")
        
        ##These are defaults and will be based on the SystemConfigIO values, for now make assumptions
        #Create the ConnectionManage
        self.connectionManage = ConnectionManageGuacRDP()
        #Create the PackageManage
        self.packageManage = PackageManageVBox()
        #Create the ExperimentManage
        self.experimentManage = ExperimentManageVBox()        
        #build the parser
        self.buildParser()

    def engineStatusCmd(self, args):
        logging.debug("engineStatusCmd(): instantiated")
        #should have status for all managers
        #query all of the managers status and then return them here

        #return "\r\nConnections: \r\n" + str(connsStatus) + "\r\nVMs:\r\n" + str(vmsStatus)
        return {"PackageMgr" : self.packageManage.getPackageManageStatus(),
                    "ConnectionMgr" : self.connectionManage.getConnectionManageStatus(),
                    "ExperimentMgr": self.experimentManage.getExperimentManageStatus() }

    def packagerStatusCmd(self, args):
        logging.debug("packagerStatusCmd(): instantiated")
        #query packager manager status and then return it here

        return self.packageManage.getPackageManageStatus()

    def packagerImportCmd(self, args):
        logging.debug("packagerImportCmd(): instantiated")
        #will import res package from file
        resfilename = args.resfilename

        return self.packageManage.importPackage(resfilename)

    def packagerExportCmd(self, args):
        logging.debug("packagerExportCmd(): instantiated")
        #will export package to res file
        configfilename = args.configfilename
        exportfilename = args.exportfilename

        return self.packageManage.exportPackage(configfilename, exportfilename)

    def connectionStatusCmd(self, args):
        #query connection manager status and then return it here
        return self.connectionManage.getConnectionManageStatus()
        
    def connectionCreateCmd(self, args):
        logging.debug("connectionCreateCmd(): instantiated")
        #will create connections as specified in configfile
        configfilename = args.configfilename

        return self.connectionManage.createConnections(configfilename)

    def connectionRemoveCmd(self, args):
        logging.debug("connectionRemoveCmd(): instantiated")
        #will remove connections as specified in configfile
        configfilename = args.configfilename

        return self.connectionManage.createConnections(configfilename)

    def connectionOpenCmd(self, args):
        logging.debug("connectionOpenCmd(): instantiated")
        #open a display to the current connection
        configfilename = args.configfilename
        experimentid = args.experimentid
        vmid = args.vmid

        return self.connectionManage.openConnection(configfilename, experimentid, vmid)

    def experimentStatusCmd(self, args):
        #query connection manager status and then return it here
        return self.experimentManage.getExperimentManageStatus()
        
    def experimentCreateCmd(self, args):
        logging.debug("experimentCreateCmd(): instantiated")
        #will create instances of the experiment (clones of vms) as specified in configfile
        configfilename = args.configfilename

        return self.experimentManage.createExperiment(configfilename)

    def experimentStartCmd(self, args):
        logging.debug("experimentStartCmd(): instantiated")
        #will start instances of the experiment (clones of vms) as specified in configfile
        configfilename = args.configfilename

        return self.experimentManage.startExperiment(configfilename)

    def experimentStopCmd(self, args):
        logging.debug("experimentStopCmd(): instantiated")
        #will start instances of the experiment (clones of vms) as specified in configfile
        configfilename = args.configfilename

        return self.experimentManage.stopExperiment(configfilename)

    def experimentRemoveCmd(self, args):
        logging.debug("experimentRemoveCmd(): instantiated")
        #will remove instances of the experiment (clones of vms) as specified in configfile
        configfilename = args.configfilename

        return self.experimentManage.removeExperiment(configfilename)


    def vmManageRefreshCmd(self, args):
        self.vmManage.refreshAllVMInfo()
        
    def vmConfigCmd(self, args):
        logging.debug("vmConfigCmd(): instantiated")
        vmName = "\""+args.vmName+"\""
                
        #check if vm exists
        logging.debug("vmConfigCmd(): Sending status request for VM: " + vmName)
        if self.vmManage.getVMStatus(vmName) == None:
            logging.error("vmConfigCmd(): vmName does not exist or you need to call refreshAllVMs: " + vmName)
            return None

        logging.debug("vmConfigCmd(): VM found, configuring VM")
        #TODO
        #Need to configure the vm adaptors accordingly
        # self.vmManage.configureVM(vmName, args.srcIPAddress, args.dstIPAddress, args.srcPort, args.dstPort, args.adaptorNum)
                
    def vmManageStartCmd(self, args):
        logging.debug("vmManageStartCmd(): instantiated")
        vmName = "\""+args.vmName+"\""

        logging.debug("Configured VM found, starting vm")
        #send start command
        self.vmManage.startVM(vmName)

    def vmManageSuspendCmd(self, args):
        logging.debug("vmManageSuspendCmd(): instantiated")
        vmName = "\""+args.vmName+"\""

        #send suspend command
        self.vmManage.suspendVM(vmName)

    def buildParser(self):
        self.parser = argparse.ArgumentParser(description='Replication Experiment System engine')
        self.subParsers = self.parser.add_subparsers()

# -----------Engine
        self.engineParser = self.subParsers.add_parser('engine', help='retrieve overall engine status')
        self.engineParser.add_argument('status', help='retrieve engine status')
        self.engineParser.set_defaults(func=self.engineStatusCmd)

# -----------Packager
        self.packageManageParser = self.subParsers.add_parser('packager')
        self.packageManageSubParsers = self.packageManageParser.add_subparsers(help='manage packaging of experiments')

        self.packageManageStatusParser = self.packageManageSubParsers.add_parser('status', help='retrieve package manager status')
        self.packageManageStatusParser.set_defaults(func=self.packagerStatusCmd)

        self.packageManageImportParser = self.packageManageSubParsers.add_parser('import', help='import a RES package from file')
        self.packageManageImportParser.add_argument('resfilename', metavar='<res filename>', action="store",
                                          help='path to res file')
        #TODO: add an optional vagrant script -- should exist within the res file
        self.packageManageImportParser.set_defaults(func=self.packagerImportCmd)

        self.packageManageExportParser = self.packageManageSubParsers.add_parser('export', help='export an experiment from config to a RES file')
        self.packageManageExportParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.packageManageExportParser.add_argument('exportfilename', metavar='<export filename>', action="store",
                                          help='path where res file will be created')
        self.packageManageExportParser.set_defaults(func=self.packagerExportCmd)

#-----------Connections
        self.connectionManageParser = self.subParsers.add_parser('conns')
        self.connectionManageSubParser = self.connectionManageParser.add_subparsers(help='manage connections')

        self.connectionManageStatusParser = self.connectionManageSubParser.add_parser('status', help='retrieve connection manager status')
        self.connectionManageStatusParser.set_defaults(func=self.connectionStatusCmd)

        self.connectionManageCreateParser = self.connectionManageSubParser.add_parser('create', help='create conns as specified in config file')
        self.connectionManageCreateParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.connectionManageCreateParser.set_defaults(func=self.connectionCreateCmd)
        
        self.connectionManageRemoveParser = self.connectionManageSubParser.add_parser('remove', help='remove conns as specified in config file')
        self.connectionManageRemoveParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.connectionManageRemoveParser.set_defaults(func=self.connectionCreateCmd)

        self.connectionManageOpenParser = self.connectionManageSubParser.add_parser('open', help='start connection to specified experiment instance and vrdp-enabled vm as specified in config file')
        self.connectionManageOpenParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.connectionManageOpenParser.add_argument('experimentid', metavar='<experiment id>', action="store",
                                          help='experiment instance number')
        self.connectionManageOpenParser.add_argument('vmid', metavar='<vm id>', action="store",
                                          help='virtual machine (with vrdp enabled) number')
        self.connectionManageOpenParser.set_defaults(func=self.connectionOpenCmd)

#-----------Experiment
        self.experimentManageParser = self.subParsers.add_parser('experiment', help='setup, start, and stop experiments as specified in a config file')
        self.experimentManageSubParser = self.experimentManageParser.add_subparsers(help='manage experiments')

        self.experimentManageStatusParser = self.experimentManageSubParser.add_parser('status', help='retrieve experiment manager status')
        self.experimentManageStatusParser.set_defaults(func=self.experimentStatusCmd)

        self.experimentManageCreateParser = self.experimentManageSubParser.add_parser('create', help='create clones aka instances of experiment')
        self.experimentManageCreateParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.experimentManageCreateParser.set_defaults(func=self.experimentCreateCmd)

        self.experimentManageStartParser = self.experimentManageSubParser.add_parser('start', help='start (headless) clones aka instances of experiment')
        self.experimentManageStartParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')                                          
        self.experimentManageStartParser.set_defaults(func=self.experimentStartCmd)

        self.experimentManageStopParser = self.experimentManageSubParser.add_parser('stop', help='stop clones aka instances of experiment')
        self.experimentManageStopParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')                                          
        self.experimentManageStopParser.set_defaults(func=self.experimentStopCmd)

        self.experimentManageRemoveParser = self.experimentManageSubParser.add_parser('remove', help='remove clones aka instances of experiment')
        self.experimentManageRemoveParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')                                          
        self.experimentManageRemoveParser.set_defaults(func=self.experimentRemoveCmd)

    def execute(self, cmd):
        logging.debug("execute(): instantiated")
        try:
            #parse out the command
            logging.debug("execute(): Received: " + str(cmd))
            r = self.parser.parse_args(shlex.split(cmd))
            #r = self.parser.parse_args(cmd)
            logging.debug("execute(): returning result: " + str(r))
            return r.func(r)
        except argparse.ArgumentError as err:
            logging.error(exc.message, '\n', err.argument)	
        # except SystemExit:
            # return

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")
###Base Engine tests
    logging.debug("Instantiating Engine")
    e = Engine()
    logging.debug("engine object: " + str(e))

    logging.debug("Calling Engine.getInstance()")
    e = Engine.getInstance()
    logging.debug("engine object: " + str(e))

    logging.debug("Calling Engine.getInstance()")
    e = Engine.getInstance()
    logging.debug("engine object: " + str(e))

###Engine tests
    res = e.execute("engine status ")

###Packager tests
    #e.execute(sys.argv[1:])
    e.execute("packager status")
    
    ###import
    e.execute("packager import resfile.res")
    res = e.execute("packager status")
    while res["writeStatus"] != PackageManageVBox.PACKAGE_MANAGE_COMPLETE:
        sleep(1)
        logging.debug("Waiting for package import to complete...")
        res = e.execute("packager status")
    logging.debug("Package import complete.")
    
    e.execute("packager export sample myresfile.res")
    res = e.execute("packager status")
    while res["writeStatus"] != PackageManageVBox.PACKAGE_MANAGE_COMPLETE:
        sleep(1)
        logging.debug("Waiting for package export to complete...")
        res = e.execute("packager status")
    logging.debug("Package export complete.") 
    
###Connection tests
    # sleep(60)#alternative, check status until packager is complete and idle
    e.execute("conns status")
    e.execute("conns create sample")

    # sleep(10) #alternative, check status until connection manager is complete and idle
    e.execute("conns status")
    e.execute("conns remove sample")
    
    # sleep(10) #alternative, check status until connection manager is complete and idle
    e.execute("conns status")
    e.execute("conns open sample 1 1")

    #####---Create Experiment Test#####
    logging.info("Starting Experiment")
    e.execute("experiment create sample")
    res = e.execute("experiment status")
    logging.debug("Waiting for experiment create to complete...")
    while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
        sleep(1)
        logging.debug("Waiting for experiment create to complete...")
        res = e.execute("experiment status")
    logging.debug("Experiment create complete.")    

    #####---Start Experiment Test#####
    logging.info("Starting Experiment")
    e.execute("experiment start sample")
    res = e.execute("experiment status")
    logging.debug("Waiting for experiment start to complete...")
    while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
        sleep(1)
        logging.debug("Waiting for experiment start to complete...")
        res = e.execute("experiment status")
    logging.debug("Experiment start complete.")    

    #####---Stop Experiment Test#####
    sleep(5)
    logging.info("Stopping Experiment")
    e.execute("experiment stop sample")
    res = e.execute("experiment status")
    logging.debug("Waiting for experiment stop to complete...")
    while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
        sleep(1)
        logging.debug("Waiting for experiment stop to complete...")
        res = e.execute("experiment status")
    logging.debug("Experiment stop complete.")    

    #####---Remove Experiment Test#####
    sleep(5)
    logging.info("Remove Experiment")
    e.execute("experiment remove sample")
    res = e.execute("experiment status")
    logging.debug("Waiting for experiment remove to complete...")
    while res["writeStatus"] != ExperimentManageVBox.EXPERIMENT_MANAGE_COMPLETE:
        sleep(1)
        logging.debug("Waiting for experiment remove to complete...")
        res = e.execute("experiment status")
    logging.debug("Experiment remove complete.")    

    sleep(3) #allow some time for observation
    #quit
