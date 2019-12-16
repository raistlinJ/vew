#!/usr/bin/env python

import logging
import shlex
import argparse
import sys
from time import sleep
from engine.VMManage.VBoxManage import VBoxManage
from engine.VMManage.VBoxManageWin import VBoxManageWin
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
        if Engine.__singleton_instance != None:
            raise Exception("Use the getInstance method to obtain an instance of this class")

        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            self.vmManage = VBoxManage()
        else:
            self.vmManage = VBoxManageWin()

        #build the parser
        self.buildParser()

    def engineStatusCmd(self, args):
        logging.debug("engineStatusCmd(): instantiated")
        #should have status for all managers
        #query all of the managers status and then return them here

        #return "\r\nConnections: \r\n" + str(connsStatus) + "\r\nVMs:\r\n" + str(vmsStatus)
        return "\r\nVMs:\r\n" # + TODO: other managers

    def vmManageVMStatusCmd(self, args):
        logging.debug("vmManageStatusCmd(): instantiated")
        #will get the current configured VM (if any) display status
        vmName = "\""+args.vmName+"\""

        return self.vmManage.getVMStatus(vmName)
            
    def vmManageMgrStatusCmd(self, args):
        #return {"configuredVM" : self.configuredVM, "mgrStatus" : self.vmManage.getManagerStatus()}
        return {"mgrStatus" : self.vmManage.getManagerStatus()}
        
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
        self.packagerParser = self.subParsers.add_parser('packager')
        self.packagerSubParsers = self.packagerParser.add_subparsers(help='manage packaging of experiments')

        self.packagerStatusParser = self.packagerSubParsers.add_parser('status', help='retrieve package manager status')
        self.packagerStatusParser.set_defaults(func=self.packagerStatusCmd)

        self.packagerImportParser = self.packagerSubParsers.add_parser('import', help='import a RES package from file')
        self.packagerImportParser.add_argument('resfilename', metavar='<res filename>', action="store",
                                          help='path to res file')
        #TODO: add an optional vagrant script -- should exist within the res file
        self.packagerImportParser.set_defaults(func=self.packagerImportCmd)

        self.packagerExportParser = self.packagerSubParsers.add_parser('export', help='export an experiment from config to a RES file')
        self.packagerExportParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.packagerExportParser.add_argument('exportfilename', metavar='<export filename>', action="store",
                                          help='path where res file will be created')
        self.packagerExportParser.set_defaults(func=self.packagerExportCmd)

#-----------Connections
        self.connectionManageParser = self.subParsers.add_parser('conns')
        self.connectionManageParser = self.vmManageParser.add_subparsers(help='manage connections')

        self.connectionManageParser = self.connectionManageParser.add_parser('status', help='retrieve connection manager status')
        self.connectionManageParser.set_defaults(func=self.connectionStatusCmd)

        self.connectionManageParser = self.connectionManageParser.add_parser('create', help='create conns as specified in config file')
        self.connectionManageParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.connectionManageParser.set_defaults(func=self.connectionCreateCmd)
        
        self.connectionManageParser = self.connectionManageParser.add_parser('remove', help='remove conns as specified in config file')
        self.connectionManageParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.connectionManageParser.set_defaults(func=self.connectionCreateCmd)

        self.connectionManageParser = self.connectionManageParser.add_parser('open', help='start connection to specified experiment instance and vrdp-enabled vm as specified in config file')
        self.connectionManageParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.connectionManageParser.add_argument('experimentid', metavar='<experiment id>', action="store",
                                          help='experiment instance number')
        self.connectionManageParser.add_argument('vmid', metavar='<vm id>', action="store",
                                          help='virtual machine (with vrdp enabled) number')
        self.connectionManageParser.set_defaults(func=self.connectionCreateCmd)

#-----------Experiments
        self.experimentsManageParser = self.vmManageSubParsers.add_parser('experiments', help='setup, start, and stop experiments as specified in a config file')
        
        self.experimentsManageParser = self.connectionManageParser.add_parser('status', help='retrieve experiment manager status')
        self.experimentsManageParser.set_defaults(func=self.experimentsStatusCmd)

        self.experimentsManageParser = self.connectionManageParser.add_parser('create', help='create clones aka instances of experiment')
        self.experimentsManageParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.experimentsManageParser.set_defaults(func=self.experimentsCreateCmd)

        self.experimentsManageParser = self.connectionManageParser.add_parser('start', help='start (headless) clones aka instances of experiment')
        self.experimentsManageParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')                                          
        self.experimentsManageParser.set_defaults(func=self.experimentsStartCmd)

        self.experimentsManageParser = self.connectionManageParser.add_parser('stop', help='stop clones aka instances of experiment')
        self.experimentsManageParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')                                          
        self.experimentsManageParser.set_defaults(func=self.experimentsStopCmd)

        self.experimentsManageParser = self.connectionManageParser.add_parser('remove', help='remove clones aka instances of experiment')
        self.experimentsManageParser.add_argument('configfilename', metavar='<config filename>', action="store",
                                          help='path to config file')                                          
        self.experimentsManageParser.set_defaults(func=self.experimentsRemoveCmd)

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
        except SystemExit:
            return

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
    sleep(1)
    #e.execute(sys.argv[1:])
    e.execute("packager status")
    
    sleep(5) 
    e.execute("packager import resfile.res")

    sleep(60)#alternative, check status until packager is complete and idle
    e.execute("packager export myexperiment1.xml myresfile.res")
    
    sleep(60)#alternative, check status until packager is complete and idle
    e.execute("conns status")
    e.execute("conns create myexperiment1.xml")

    sleep(10) #alternative, check status until connection manager is complete and idle
    e.execute("conns status")
    e.execute("conns remove myexperiment1.xml")
    
    sleep(10) #alternative, check status until connection manager is complete and idle
    e.execute("conns status")
    e.execute("conns open myexperiment1.xml 1 1")

    sleep(5) #alternative, check status until connection manager is complete and idle
    e.execute("experiments status")
    e.execute("experiments create myexperiment1.xml")

    sleep(60) #alternative, check status until experiments manager is complete and idle
    e.execute("experiments status")
    e.execute("experiments start myexperiment1.xml")

    sleep(60) #alternative, check status until experiments manager is complete and idle
    e.execute("experiments status")
    e.execute("experiments stop myexperiment1.xml")

    sleep(60) #alternative, check status until experiments manager is complete and idle
    e.execute("experiments status")
    e.execute("experiments remove myexperiment1.xml")
    
    sleep(60) #allow some time for observation
    #quit
