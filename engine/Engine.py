#Arguments in have to have double quotes if it has spaces.
#Once read by the injesting function, these quotes are removed
#The quotes will then be added as needed for backend system calls
import logging
import shlex
import argparse
import sys
import os
from engine.Manager.ConnectionManage.ConnectionManageGuacRDP import ConnectionManageGuacRDP
from engine.Manager.PackageManage.PackageManageVBox import PackageManageVBox
from engine.Manager.PackageManage.PackageManageVMware import PackageManageVMware
from engine.Manager.ExperimentManage.ExperimentManageVBox import ExperimentManageVBox
from engine.Manager.ExperimentManage.ExperimentManageVMware import ExperimentManageVMware
from engine.Manager.VMManage.VBoxManage import VBoxManage
from engine.Manager.VMManage.VBoxManageWin import VBoxManageWin
from engine.Manager.VMManage.VMwareManage import VMwareManage
from engine.Manager.VMManage.VMwareManageWin import VMwareManageWin
from engine.Configuration.SystemConfigIO import SystemConfigIO

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
        #Create the VMManage
        c = SystemConfigIO()
        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            if c.getConfig()['HYPERVISOR']['ACTIVE'] == 'VBOX':
                self.vmManage = VBoxManage(True)
            else:
                self.vmManage = VMwareManage(False)
        else:
            if c.getConfig()['HYPERVISOR']['ACTIVE'] == 'VBOX':
                self.vmManage = VBoxManageWin(True)
            else:
                self.vmManage = VMwareManageWin(False)

        #Create the ConnectionManage
        self.connectionManage = ConnectionManageGuacRDP()
        #Create the ExperimentManage
        #self.experimentManage = ExperimentManageVBox(self.vmManage)
        self.experimentManage = ExperimentManageVMware(self.vmManage)
        #Create the PackageManage
        #self.packageManage = PackageManageVBox(self.vmManage, self.experimentManage)
        self.packageManage = PackageManageVMware(self.vmManage, self.experimentManage)
        #build the parser
        self.buildParser()

    def engineStatusCmd(self, args):
        logging.debug("engineStatusCmd(): instantiated")
        #should have status for all managers
        #query all of the managers status and then return them here

        return {"VMMgr" : self.vmManage.getManagerStatus,
                    "PackageMgr" : self.packageManage.getPackageManageStatus(),
                    "ConnectionMgr" : self.connectionManage.getConnectionManageStatus(),
                    "ExperimentMgr": self.experimentManage.getExperimentManageStatus() }

    def vmManageVMStatusCmd(self, args):
        logging.debug("vmManageStatusCmd(): instantiated")
        #will get the current configured VM (if any) display status
        vmName = args.vmName.replace("\"","").replace("'","")
        logging.debug("vmManageStatusCmd(): Returning VM status for: " + str(vmName))
        return self.vmManage.getVMStatus(vmName)
        
    def vmManageMgrStatusCmd(self, args):
        logging.debug("vmManageMgrStatusCmd(): instantiated")
        return self.vmManage.getManagerStatus()
        
    def vmManageRefreshCmd(self, args):
        logging.debug("vmManageRefreshCmd(): instantiated")
        self.vmManage.refreshAllVMInfo()

    def packagerStatusCmd(self, args):
        logging.debug("packagerStatusCmd(): instantiated")
        #query packager manager status and then return it here
        return self.packageManage.getPackageManageStatus()

    def packagerImportCmd(self, args):
        logging.debug("packagerImportCmd(): instantiated: ")
        #will import res package from file
        resfilename = args.resfilename
        return self.packageManage.importPackage(resfilename)

    def packagerExportCmd(self, args):
        logging.debug("packagerExportCmd(): instantiated")
        #will export package to res file
        experimentname = args.experimentname
        exportpath = args.exportpath
        return self.packageManage.exportPackage(experimentname, exportpath)

    def connectionStatusCmd(self, args):
        #query connection manager status and then return it here
        return self.connectionManage.getConnectionManageStatus()

    def connectionRefreshCmd(self, args):
        hostname = args.hostname
        username = args.username
        password = args.password
        url_path = args.url_path
        method = args.method
        #query connection manager status and then return it here
        return self.connectionManage.getConnectionManageRefresh(hostname, username, password, url_path, method)
        
    def connectionCreateCmd(self, args):
        logging.debug("connectionCreateCmd(): instantiated")
        #will create connections as specified in configfile
        configname = args.configname
        hostname = args.hostname
        username = args.username
        password = args.password
        url_path = args.url_path
        method = args.method
        maxConnections = args.maxConnections
        maxConnectionsPerUser = args.maxConnectionsPerUser
        width = args.width
        height = args.height
        bitdepth = args.bitdepth
        itype = args.itype
        name = args.name
        creds_file = args.creds_file
        if creds_file != None and isinstance(creds_file, str) and creds_file.strip() != "None":
            full_creds_file = os.path.abspath(creds_file)
            if os.path.exists(full_creds_file):
                return self.connectionManage.createConnections(configname, hostname, username, password, url_path, method, maxConnections, maxConnectionsPerUser, width, height, bitdepth, full_creds_file, itype, name)
        return self.connectionManage.createConnections(configname, hostname, username, password, url_path, method, maxConnections, maxConnectionsPerUser, width, height, bitdepth)

    def connectionRemoveCmd(self, args):
        logging.debug("connectionRemoveCmd(): instantiated")
        #will remove connections as specified in configfile
        configname = args.configname
        configname = args.configname
        hostname = args.hostname
        username = args.username
        password = args.password
        url_path = args.url_path
        method = args.method
        itype = args.itype
        name = args.name
        creds_file = args.creds_file
        if creds_file != None and isinstance(creds_file, str) and creds_file.strip() != "None":
            full_creds_file = os.path.abspath(creds_file)
            if os.path.exists(full_creds_file):
                return self.connectionManage.removeConnections(configname, hostname, username, password, url_path, method, full_creds_file, itype, name)
        return self.connectionManage.removeConnections(configname, hostname, username, password, url_path, method)

    def connectionClearAllCmd(self, args):
        logging.debug("connectionClearAllCmd(): instantiated")
        #will remove connections as specified in configfile
        hostname = args.hostname
        username = args.username
        password = args.password
        url_path = args.url_path
        method = args.method
        
        return self.connectionManage.clearAllConnections(hostname, username, password, url_path, method)

    def connectionOpenCmd(self, args):
        logging.debug("connectionOpenCmd(): instantiated")
        #open a display to the current connection
        configname = args.configname
        experimentid = args.experimentid
        itype = args.itype
        name = args.itype

        return self.connectionManage.openConnection(configname, experimentid, itype, name)

    def experimentStatusCmd(self, args):
        #query connection manager status and then return it here
        return self.experimentManage.getExperimentManageStatus()
        
    def experimentCreateCmd(self, args):
        logging.debug("experimentCreateCmd(): instantiated")
        #will create instances of the experiment (clones of vms) as specified in configfile
        configname = args.configname
        itype=args.itype
        name=args.name
        if name == "all":
            return self.experimentManage.createExperiment(configname)    
        return self.experimentManage.createExperiment(configname, itype, name)

    def experimentStartCmd(self, args):
        logging.debug("experimentStartCmd(): instantiated")
        #will start instances of the experiment (clones of vms) as specified in configfile
        configname = args.configname
        itype=args.itype
        name=args.name
        if name == "all":
            return self.experimentManage.startExperiment(configname)    
        return self.experimentManage.startExperiment(configname, itype, name)

    def experimentSuspendCmd(self, args):
        logging.debug("experimentSuspendCmd(): instantiated")
        #will suspend instances of the experiment (clones of vms) as specified in configfile
        configname = args.configname
        itype=args.itype
        name=args.name
        if name == "all":
            return self.experimentManage.suspendExperiment(configname)    
        return self.experimentManage.suspendExperiment(configname, itype, name)

    def experimentPauseCmd(self, args):
        logging.debug("experimentPauseCmd(): instantiated")
        #will pause instances of the experiment (clones of vms) as specified in configfile
        configname = args.configname
        itype=args.itype
        name=args.name
        if name == "all":
            return self.experimentManage.pauseExperiment(configname)    
        return self.experimentManage.pauseExperiment(configname, itype, name)

    def experimentSnapshotCmd(self, args):
        logging.debug("experimentSnapshotCmd(): instantiated")
        #will snapshot instances of the experiment (clones of vms) as specified in configfile
        configname = args.configname
        itype=args.itype
        name=args.name
        if name == "all":
            return self.experimentManage.snapshotExperiment(configname)    
        return self.experimentManage.snapshotExperiment(configname, itype, name)

    def experimentStopCmd(self, args):
        logging.debug("experimentStopCmd(): instantiated")
        #will start instances of the experiment (clones of vms) as specified in configfile
        configname = args.configname
        itype=args.itype
        name=args.name
        if name == "all":
            return self.experimentManage.stopExperiment(configname)    
        return self.experimentManage.stopExperiment(configname, itype, name)

    def experimentRemoveCmd(self, args):
        logging.debug("experimentRemoveCmd(): instantiated")
        #will remove instances of the experiment (clones of vms) as specified in configfile
        configname = args.configname
        itype=args.itype
        name=args.name
        if name == "all":
            return self.experimentManage.removeExperiment(configname)    
        return self.experimentManage.removeExperiment(configname, itype, name)

    def experimentRestoreCmd(self, args):
        logging.debug("experimentRestoreCmd(): instantiated")
        #will restore state of the experiment (latest snapshots of vms) as specified in configfile
        configname = args.configname
        itype=args.itype
        name=args.name
        if name == "all":
            return self.experimentManage.restoreExperiment(configname)    
        return self.experimentManage.restoreExperiment(configname, itype, name)
  
    def vmConfigCmd(self, args):
        logging.debug("vmConfigCmd(): instantiated")
        vmName = args.vmName.replace("\"","").replace("'","")
                
        #check if vm exists
        logging.debug("vmConfigCmd(): Sending status request for VM: " + vmName)
        if self.vmManage.getVMStatus(vmName) == None:
            logging.error("vmConfigCmd(): vmName does not exist or you need to call refreshAllVMs: " + vmName)
            return None
        logging.debug("vmConfigCmd(): VM found, configuring VM")
                
    def vmManageStartCmd(self, args):
        logging.debug("vmManageStartCmd(): instantiated")
        vmName = args.vmName.replace("\"","").replace("'","")

        logging.debug("Configured VM found, starting vm")
        #send start command
        self.vmManage.startVM(vmName)

    def vmManageSuspendCmd(self, args):
        logging.debug("vmManageSuspendCmd(): instantiated")
        vmName = args.vmName.replace("\"","").replace("'","")

        #send suspend command
        self.vmManage.suspendVM(vmName)

    def vmManagePauseCmd(self, args):
        logging.debug("vmManagePauseCmd(): instantiated")
        vmName = args.vmName.replace("\"","").replace("'","")

        #send pause command
        self.vmManage.pauseVM(vmName)

    def vmManageSnapshotCmd(self, args):
        logging.debug("vmManageSnapshotCmd(): instantiated")
        vmName = args.vmName.replace("\"","").replace("'","")

        #send snapshot command
        self.vmManage.snapshotVM(vmName)

    def buildParser(self):
        self.parser = argparse.ArgumentParser(description='Replication Experiment System engine')
        self.subParsers = self.parser.add_subparsers()

# -----------Engine
        self.engineParser = self.subParsers.add_parser('engine', help='retrieve overall engine status')
        self.engineParser.add_argument('status', help='retrieve engine status')
        self.engineParser.set_defaults(func=self.engineStatusCmd)

#-----------VM Manage
        self.vmManageParser = self.subParsers.add_parser('vm-manage')
        self.vmManageSubParsers = self.vmManageParser.add_subparsers(help='manage vm')

        self.vmStatusParser = self.vmManageSubParsers.add_parser('vmstatus', help='retrieve vm status')
        self.vmStatusParser.add_argument('vmName', metavar='<vm name>', action="store",
                                           help='name of vm to retrieve status')
        self.vmStatusParser.set_defaults(func=self.vmManageVMStatusCmd)

        self.vmStatusParser = self.vmManageSubParsers.add_parser('mgrstatus', help='retrieve manager status')
        self.vmStatusParser.set_defaults(func=self.vmManageMgrStatusCmd)

        self.vmRefreshParser = self.vmManageSubParsers.add_parser('refresh', help='retreive current vm information')
        self.vmRefreshParser.set_defaults(func=self.vmManageRefreshCmd)

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
        self.packageManageExportParser.add_argument('experimentname', metavar='<config filename>', action="store",
                                          help='name of experiment')
        self.packageManageExportParser.add_argument('exportpath', metavar='<export path>', action="store",
                                          help='path where res file will be created')
        self.packageManageExportParser.set_defaults(func=self.packagerExportCmd)

#-----------Connections
        self.connectionManageParser = self.subParsers.add_parser('conns')
        self.connectionManageSubParser = self.connectionManageParser.add_subparsers(help='manage connections')

        self.connectionManageStatusParser = self.connectionManageSubParser.add_parser('status', help='retrieve connection manager status')
        self.connectionManageStatusParser.set_defaults(func=self.connectionStatusCmd)

        self.connectionManageRefreshParser = self.connectionManageSubParser.add_parser('refresh', help='retrieve all connection manager status')
        self.connectionManageRefreshParser.add_argument('hostname', metavar='<host address>', action="store",
                                          help='Name or IP address where Connection host resides')
        self.connectionManageRefreshParser.add_argument('username', metavar='<username>', action="store",
                                          help='Username for connecting to host')
        self.connectionManageRefreshParser.add_argument('password', metavar='<password>', action="store",
                                          help='Password for connecting to host')
        self.connectionManageRefreshParser.add_argument('url_path', metavar='<url_path>', action="store",
                                          help='URL path to broker service')
        self.connectionManageRefreshParser.add_argument('method', metavar='<method>', action="store",
                                          help='Either HTTP or HTTPS, depending on the server\'s configuration')
        self.connectionManageRefreshParser.set_defaults(func=self.connectionRefreshCmd)

        self.connectionManageCreateParser = self.connectionManageSubParser.add_parser('create', help='create conns as specified in config file')
        self.connectionManageCreateParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.connectionManageCreateParser.add_argument('hostname', metavar='<host address>', action="store",
                                          help='Name or IP address where Connection host resides')
        self.connectionManageCreateParser.add_argument('username', metavar='<username>', action="store",
                                          help='Username for connecting to host')
        self.connectionManageCreateParser.add_argument('password', metavar='<password>', action="store",
                                          help='Password for connecting to host')
        self.connectionManageCreateParser.add_argument('url_path', metavar='<url_path>', action="store",
                                          help='URL path to broker service')
        self.connectionManageCreateParser.add_argument('method', metavar='<method>', action="store",
                                          help='Either HTTP or HTTPS, depending on the server\'s configuration')
        self.connectionManageCreateParser.add_argument('maxConnections', metavar='<maxConnections>', action="store", default="1",
                                          help='Max number of connections allowed per remote conn')
        self.connectionManageCreateParser.add_argument('maxConnectionsPerUser', metavar='<maxConnectionsPerUser>', action="store", default="1", 
                                          help='Max number of connections allowed per user per remote conn')
        self.connectionManageCreateParser.add_argument('width', metavar='<width>', action="store", default="1400",
                                          help='Width of remote connection display')
        self.connectionManageCreateParser.add_argument('height', metavar='<height>', action="store", default="1050",
                                          help='Height of remote connection display')
        self.connectionManageCreateParser.add_argument('bitdepth', metavar='<bitdepth>', action="store", default="16",
                                          help='Bit-depth (8, 16, 24, or 32)')
        self.connectionManageCreateParser.add_argument('creds_file', metavar='<creds_file>', action="store",
                                          help='File with username/password pairs.')
        self.connectionManageCreateParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.connectionManageCreateParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')
        self.connectionManageCreateParser.set_defaults(func=self.connectionCreateCmd)
        
        self.connectionManageRemoveParser = self.connectionManageSubParser.add_parser('remove', help='remove conns as specified in config file')
        self.connectionManageRemoveParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.connectionManageRemoveParser.add_argument('hostname', metavar='<host address>', action="store",
                                          help='Name or IP address where Connection host resides')
        self.connectionManageRemoveParser.add_argument('username', metavar='<username>', action="store",
                                          help='Username for connecting to host')
        self.connectionManageRemoveParser.add_argument('password', metavar='<password>', action="store",
                                          help='Password for connecting to host')
        self.connectionManageRemoveParser.add_argument('url_path', metavar='<url_path>', action="store",
                                          help='URL path to broker service')
        self.connectionManageRemoveParser.add_argument('method', metavar='<method>', action="store",
                                          help='Either HTTP or HTTPS, depending on the server\'s configuration')
        self.connectionManageRemoveParser.add_argument('creds_file', metavar='<creds_file>', action="store",
                                          help='File with username/password pairs.')
        self.connectionManageRemoveParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.connectionManageRemoveParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')
        self.connectionManageRemoveParser.set_defaults(func=self.connectionRemoveCmd)

        self.connectionManageClearAllParser = self.connectionManageSubParser.add_parser('clear', help='Clear all connections in database')
        self.connectionManageClearAllParser.add_argument('hostname', metavar='<host address>', action="store",
                                          help='Name or IP address where Connection host resides')
        self.connectionManageClearAllParser.add_argument('username', metavar='<username>', action="store",
                                          help='Username for connecting to host')
        self.connectionManageClearAllParser.add_argument('password', metavar='<password>', action="store",
                                          help='Password for connecting to host')
        self.connectionManageClearAllParser.add_argument('url_path', metavar='<url_path>', action="store",
                                          help='URL path to broker service')
        self.connectionManageClearAllParser.add_argument('method', metavar='<method>', action="store",
                                          help='Either HTTP or HTTPS, depending on the server\'s configuration')
        self.connectionManageClearAllParser.set_defaults(func=self.connectionClearAllCmd)

        self.connectionManageOpenParser = self.connectionManageSubParser.add_parser('open', help='start connection to specified experiment instance and vrdp-enabled vm as specified in config file')
        self.connectionManageOpenParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.connectionManageOpenParser.add_argument('experimentid', metavar='<experiment id>', action="store",
                                          help='experiment instance number')
        self.connectionManageOpenParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.connectionManageOpenParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')
        self.connectionManageOpenParser.set_defaults(func=self.connectionOpenCmd)

#-----------Experiment
        self.experimentManageParser = self.subParsers.add_parser('experiment', help='setup, start, and stop experiments as specified in a config file')
        self.experimentManageSubParser = self.experimentManageParser.add_subparsers(help='manage experiments')

        self.experimentManageStatusParser = self.experimentManageSubParser.add_parser('status', help='retrieve experiment manager status')
        self.experimentManageStatusParser.set_defaults(func=self.experimentStatusCmd)

        self.experimentManageCreateParser = self.experimentManageSubParser.add_parser('create', help='create clones aka instances of experiment')
        self.experimentManageCreateParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.experimentManageCreateParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.experimentManageCreateParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')                                   
        self.experimentManageCreateParser.set_defaults(func=self.experimentCreateCmd)

        self.experimentManageStartParser = self.experimentManageSubParser.add_parser('start', help='start (headless) clones aka instances of experiment')
        self.experimentManageStartParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.experimentManageStartParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.experimentManageStartParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')
        self.experimentManageStartParser.set_defaults(func=self.experimentStartCmd)

        self.experimentManageStopParser = self.experimentManageSubParser.add_parser('stop', help='stop clones aka instances of experiment')
        self.experimentManageStopParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.experimentManageStopParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.experimentManageStopParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')                                          
        self.experimentManageStopParser.set_defaults(func=self.experimentStopCmd)

        self.experimentManageSuspendParser = self.experimentManageSubParser.add_parser('suspend', help='save state for clones aka instances of experiment')
        self.experimentManageSuspendParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.experimentManageSuspendParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.experimentManageSuspendParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')                                                                      
        self.experimentManageSuspendParser.set_defaults(func=self.experimentSuspendCmd)

        self.experimentManagePauseParser = self.experimentManageSubParser.add_parser('pause', help='pause clones aka instances of experiment')
        self.experimentManagePauseParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')                                
        self.experimentManagePauseParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.experimentManagePauseParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')                                                    
        self.experimentManagePauseParser.set_defaults(func=self.experimentPauseCmd)

        self.experimentManageSnapshotParser = self.experimentManageSubParser.add_parser('snapshot', help='snapshot clones aka instances of experiment')
        self.experimentManageSnapshotParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.experimentManageSnapshotParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.experimentManageSnapshotParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')                                              
        self.experimentManageSnapshotParser.set_defaults(func=self.experimentSnapshotCmd)

        self.experimentManageRestoreParser = self.experimentManageSubParser.add_parser('restore', help='restore experiment to latest snapshot')
        self.experimentManageRestoreParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.experimentManageRestoreParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.experimentManageRestoreParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')          
        self.experimentManageRestoreParser.set_defaults(func=self.experimentRestoreCmd)

        self.experimentManageRemoveParser = self.experimentManageSubParser.add_parser('remove', help='remove clones aka instances of experiment')
        self.experimentManageRemoveParser.add_argument('configname', metavar='<config filename>', action="store",
                                          help='path to config file')
        self.experimentManageRemoveParser.add_argument('itype', metavar='<instance-type>', action="store",
                                          help='set, template, or vm')
        self.experimentManageRemoveParser.add_argument('name', metavar='<instance-name>', action="store",
                                          help='all, set-number, template-vm-name, or clone-vm-name')                                                    
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
            logging.error(err.message, '\n', err.argument_name)	
        # except SystemExit:
            # return