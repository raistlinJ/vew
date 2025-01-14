#This file will read the XML data and make it available as JSON
import xmltodict
import logging
import json
import sys, traceback
from engine.Configuration.SystemConfigIO import SystemConfigIO
import os
import threading

class ExperimentConfigIO:

    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def getInstance(cls):
        logging.debug("getInstance() ExperimentConfigIO: instantiated")
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

    def __init__(self):
        #Virtually private constructor
        self.s = SystemConfigIO()
        self.rolledoutjson = {}
        self.config_jsondata = {}
        self.config_rdp_userpass = {}
        self.config_challengesys_userpass = {}

    def storeConfigRDPBrokerCreds(self, configname, username, password, url, method):
        logging.debug("ExperimentConfigIO: storeConfigRDPBrokerCreds(): instantiated")
        self.config_rdp_userpass[configname] = (username, password, url, method)

    def getConfigRDPBrokerCreds(self, configname):
        logging.debug("ExperimentConfigIO: getConfigRDPBrokerCreds(): instantiated")
        if configname in self.config_rdp_userpass:
            return self.config_rdp_userpass[configname]
        return None

    def storeConfigChallengeSysCreds(self, configname, username, password, method):
        logging.debug("ExperimentConfigIO: storeConfigChallengeSysCreds(): instantiated")
        self.config_challengesys_userpass[configname] = (username, password, method)

    def getConfigChallengeSysCreds(self, configname):
        logging.debug("ExperimentConfigIO: getConfigChallengeSysCreds(): instantiated")
        if configname in self.config_challengesys_userpass:
            return self.config_challengesys_userpass[configname]
        return None

    def getExperimentXMLFileData(self, configname, force_refresh=False):
        logging.debug("ExperimentConfigIO: getExperimentXMLFileData(): instantiated")
        jsondata = None
        if configname in self.config_jsondata:
            if force_refresh == False:
                return self.config_jsondata[configname]
        try:
            xmlconfigfile = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], configname,"Experiments",configname+".xml")
            if os.path.getsize(xmlconfigfile) > 0:
                with open(xmlconfigfile) as fd:
                    jsondata = xmltodict.parse(fd.read(), process_namespaces=True)
                self.config_jsondata[configname] = jsondata
            return jsondata
        except FileNotFoundError:
            logging.error("Error in getExperimentXMLFileData(): File not found: " + str(xmlconfigfile))
            return None
        except Exception:
            logging.error("Error in getExperimentXMLFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None
    
    def getExperimentServerInfo(self, configname):
        logging.debug("ExperimentConfigIO: getExperimentXMLFileData(): instantiated")
        jsondata = self.getExperimentJSONFileData(configname)
        vmserverip=None
        rdpbroker=None
        chatserver=None
        challengesserver = None
        users_file=None
        if "xml" in jsondata:
            if "testbed-setup" in jsondata["xml"]:
                if "network-config" in jsondata["xml"]["testbed-setup"]:
                    if "vm-server-ip" in jsondata["xml"]["testbed-setup"]["network-config"]:
                        vmserverip = jsondata["xml"]["testbed-setup"]["network-config"]["vm-server-ip"]
                    if "rdp-broker-ip" in jsondata["xml"]["testbed-setup"]["network-config"]:
                        rdpbroker = jsondata["xml"]["testbed-setup"]["network-config"]["rdp-broker-ip"]
                    if "chat-server-ip" in jsondata["xml"]["testbed-setup"]["network-config"]:
                        chatserver = jsondata["xml"]["testbed-setup"]["network-config"]["chat-server-ip"]
                    if "challenges-server-ip" in jsondata["xml"]["testbed-setup"]["network-config"]:
                        challengesserver = jsondata["xml"]["testbed-setup"]["network-config"]["challenges-server-ip"]
                if "vm-set" in jsondata["xml"]["testbed-setup"]:
                    if "vm-set" in jsondata["xml"]["testbed-setup"]:
                        if "users-filename" in jsondata["xml"]["testbed-setup"]["vm-set"]:
                            users_file = jsondata["xml"]["testbed-setup"]["vm-set"]["users-filename"]
                    
        return vmserverip, rdpbroker, chatserver, challengesserver, users_file

    def getExperimentVMRolledOut(self, configname, config_jsondata=None, force_refresh="False"):
        logging.debug("ExperimentConfigIO: getExperimentXMLFileData(): instantiated")
        try:
            if configname in self.rolledoutjson:
                if force_refresh == False:
                    return self.rolledoutjson[configname]

            vmRolledOutList = {}
            if config_jsondata == None or force_refresh:
                config_jsondata = self.getExperimentXMLFileData(configname, force_refresh=True)
            if config_jsondata == None:
                return None
            vmServerIP = config_jsondata["xml"]["testbed-setup"]["network-config"]["vm-server-ip"]
            rdpBrokerIP = config_jsondata["xml"]["testbed-setup"]["network-config"]["rdp-broker-ip"]
            chatServerIP = config_jsondata["xml"]["testbed-setup"]["network-config"]["chat-server-ip"]
            challengesServerIP = config_jsondata["xml"]["testbed-setup"]["network-config"]["challenges-server-ip"]
            vmSet = config_jsondata["xml"]["testbed-setup"]["vm-set"]
            numClones = int(vmSet["num-clones"])
            cloneSnapshots = vmSet["clone-snapshots"]
            linkedClones = vmSet["linked-clones"]
            baseGroupname = vmSet["base-groupname"]
            baseOutname = vmSet["base-outname"]
            vrdpBaseport = vmSet["vrdp-baseport"]
            usersFilename = vmSet["users-filename"]

            logging.debug("getExperimentVMRolledOut(): path: " + " numClones: " + str(numClones) + " linked: " + str(linkedClones) + " baseGroup: " + str(baseGroupname) + " baseOut: " + str(baseOutname) + "vrdpBase: " + str(vrdpBaseport) + " usersFilename: " + str(usersFilename))
            if "vm" not in vmSet:
                return None
            if isinstance(vmSet["vm"], list) == False:
                logging.debug("getExperimentVMRolledOut(): vmSet only has a single VM; placing into list for compatibility")
                vmSet["vm"] = [vmSet["vm"]]
            #we get the vms in order of group; 
            for vm in vmSet["vm"]:
                vmName = vm["name"]
                vmRolledOutList[vmName] = []
                logging.debug("getExperimentVMRolledOut(): adding data for vm: " + str(vmName))

                startupCmds_reformatted = None
                startupDelay = 0
                #read startup commands
                if "startup" in vm and "startup" in vm and vm["startup"] != None and "cmd" in vm["startup"]:
                    startupCmds_reformatted = {}
                    if "delay" in vm["startup"]:
                        startupDelay = vm["startup"]["delay"]
                    startupcmds = vm["startup"]["cmd"]
                    #if this is not a list, make it one (xml to json limitation)
                    if isinstance(startupcmds, list) == False:
                        startupcmds = [startupcmds]
                    #iterate through each startup command
                    for startupcmd in startupcmds:
                        #if exec does not exist, just quit; can't do anything without it
                        if "exec" not in startupcmd:
                            logging.error("getExperimentVMRolledOut(): exec tag missing: " + str(startupcmd))
                            continue
                        if "enabled" not in startupcmd or startupcmd["enabled"] != "2":
                            logging.debug("getExperimentVMRolledOut(): command disabled, skipping: " + str(startupcmd))
                            continue
                        #set default hypervisor and seq if they aren't specified
                        hypervisor = "unset"
                        seq = "0"
                        if hypervisor in startupcmd:
                            hypervisor = startupcmd["hypervisor"]
                        if "seq" in startupcmd:
                            seq = startupcmd["seq"]
                        #store the data and allow for duplicate sequences (store as list)
                        if seq not in startupCmds_reformatted:
                            startupCmds_reformatted[seq] = [(hypervisor, startupcmd["exec"])]
                        else:
                            startupCmds_reformatted[seq].append((hypervisor, startupcmd["exec"]))

                storedCmds_reformatted = None
                storedDelay = 0
                #read stored commands
                if "stored" in vm and "stored" in vm and vm["stored"] != None and "cmd" in vm["stored"]:
                    storedCmds_reformatted = {}
                    if "delay" in vm["stored"]:
                        storedDelay = vm["stored"]["delay"]
                    storedcmds = vm["stored"]["cmd"]
                    #if this is not a list, make it one (xml to json limitation)
                    if isinstance(storedcmds, list) == False:
                        storedcmds = [storedcmds]
                    #iterate through each stored command
                    for storedcmd in storedcmds:
                        #if exec does not exist, just quit; can't do anything without it
                        if "exec" not in storedcmd:
                            logging.error("getExperimentVMRolledOut(): exec tag missing: " + str(storedcmd))
                            continue
                        if "enabled" not in storedcmd or storedcmd["enabled"] != "2":
                            logging.debug("getExperimentVMRolledOut(): command disabled, skipping: " + str(storedcmd))
                            continue
                        #set default hypervisor and seq if they aren't specified
                        hypervisor = "unset"
                        seq = "0"
                        if hypervisor in storedcmd:
                            hypervisor = storedcmd["hypervisor"]
                        if "seq" in storedcmd:
                            seq = storedcmd["seq"]
                        #store the data and allow for duplicate sequences (store as list)
                        if seq not in storedCmds_reformatted:
                            storedCmds_reformatted[seq] = [(hypervisor, storedcmd["exec"])]
                        else:
                            storedCmds_reformatted[seq].append((hypervisor, storedcmd["exec"]))

                #get names for clones
                myBaseOutname = baseOutname
                for i in range(1, numClones + 1):
                    if vmName[-4:] == ".vmx":
                        cloneVMName = vmName[:-4] + myBaseOutname + str(i) + ".vmx"
                    else:
                        cloneVMName = vmName + myBaseOutname + str(i)
                    cloneGroupName = "/" + baseGroupname + "/Set" + str(i)
                  
                    # intnet adaptors
                    internalnets = vm["internalnet-basename"]
                    cloneNetNum = 1
                    logging.debug("getExperimentVMRolledOut(): Internal net names: " + str(internalnets))
                    cloneNets = []
                    if isinstance(internalnets, list) == False:
                        internalnets = [internalnets]
                    for internalnet in internalnets:
                        cloneNets.append(str(internalnet) + str(myBaseOutname) + str(i))
                        cloneNetNum += 1
                    # vrdp setup, if enabled include the port in the returned json
                    vrdpEnabled = vm["vrdp-enabled"]
                    if vrdpEnabled != None and vrdpEnabled == 'true':
                        vrdpBaseport = str(int(vrdpBaseport))
                        vmRolledOutList[vmName].append({"name": cloneVMName, "group-name": cloneGroupName, "networks": cloneNets, "vrdpEnabled": vrdpEnabled, "vrdpPort": vrdpBaseport, "baseGroupName": baseGroupname, "groupNum": str(i), "vm-server-ip": vmServerIP, "rdp-broker-ip": rdpBrokerIP, "chat-server-ip": chatServerIP, "challenges-server-ip": challengesServerIP, "clone-snapshots": cloneSnapshots, "linked-clones": linkedClones, "startup-cmds": startupCmds_reformatted, "startup-cmds-delay": startupDelay, "stored-cmds": storedCmds_reformatted, "stored-cmds-delay": storedDelay, "users-filename": usersFilename})
                        #vmRolledOutList[vmName].append({"name": cloneVMName, "group-name": cloneGroupName, "networks": cloneNets, "vrdpEnabled": vrdpEnabled, "vrdpPort": vrdpBaseport, "baseGroupName": baseGroupname, "groupNum": str(i), "vm-server-ip": vmServerIP, "clone-snapshots": cloneSnapshots, "linked-clones": linkedClones, "startup-cmds": startupCmds_reformatted, "startup-cmds-delay": startupDelay, "users-filename": usersFilename})
                        vrdpBaseport = int(vrdpBaseport) + 1
                    #otherwise, don't include vrdp port
                    else:
                        #vmRolledOutList[vmName].append({"name": cloneVMName, "group-name": cloneGroupName, "networks": cloneNets, "vrdpEnabled": vrdpEnabled, "baseGroupName": baseGroupname, "groupNum": str(i), "clone-snapshots": cloneSnapshots, "linked-clones": linkedClones, "startup-cmds": startupCmds_reformatted, "startup-cmds-delay": startupDelay, "users-filename": usersFilename})
                        vmRolledOutList[vmName].append({"name": cloneVMName, "group-name": cloneGroupName, "networks": cloneNets, "vrdpEnabled": vrdpEnabled, "baseGroupName": baseGroupname, "groupNum": str(i), "vm-server-ip": vmServerIP, "rdp-broker-ip": rdpBrokerIP, "chat-server-ip": chatServerIP, "challenges-server-ip": challengesServerIP, "clone-snapshots": cloneSnapshots, "linked-clones": linkedClones, "startup-cmds": startupCmds_reformatted, "startup-cmds-delay": startupDelay, "stored-cmds": storedCmds_reformatted, "stored-cmds-delay": storedDelay, "users-filename": usersFilename})

                    logging.debug("getExperimentVMRolledOut(): finished setting up clone: " + str(vmRolledOutList))
            self.rolledoutjson[configname] = vmRolledOutList, numClones
            return vmRolledOutList, numClones

        except Exception:
            logging.error("Error in getExperimentVMRolledOut(): An error occured. Check that file exists and that it is properly formatted.")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def getValidVMsFromTypeName(self, configname, itype, name, rolledoutjson=None):
        logging.debug("getValidVMsFromTypeName(): instantiated")
        if rolledoutjson == None:
            rolledoutjson = self.getExperimentVMRolledOut(configname)
        #get VMs or sets that we need to start
        validvms = []
        validvmnames = []
        if name == "all":
            #if none was specified, just add all vms to the list
            validvms = self.getExperimentVMListsFromRolledOut(configname, rolledoutjson)
            for vm in validvms:
                validvmnames.append(vm["name"])            
        elif itype == "set":
            validvms = self.getExperimentVMsInSetFromRolledOut(configname, name, rolledoutjson)
            for vm in validvms:
                validvmnames.append(vm)                
        elif itype == "template":
            validvms = []
            if name in self.getExperimentVMNamesFromTemplateFromRolledOut(configname, rolledoutjson):
                validvms = self.getExperimentVMNamesFromTemplateFromRolledOut(configname, rolledoutjson)[name]
            for vm in validvms:
                validvmnames.append(vm)
        elif itype == "vm":
            validvmnames.append(name)
        elif itype == "":
            #if none was specified, just add all vms to the list
            validvms = self.getExperimentVMListsFromRolledOut(configname, rolledoutjson)
            for vm in validvms:
                validvmnames.append(vm["name"])
        return validvmnames

    def getExperimentVMsInSetFromRolledOut(self, configname, set_num, rolledout_jsondata=None):
        logging.debug("ExperimentConfigIO: getExperimentVMsInSetFromRolledOut(): instantiated")
        sets = self.getExperimentSetDictFromRolledOut(configname, rolledout_jsondata=rolledout_jsondata)
        set_num_str = str(set_num)
        if set_num_str not in sets:
            return []
        return sets[set_num_str]

    def getExperimentSetDictFromRolledOut(self, configname, rolledout_jsondata=None):
        logging.debug("ExperimentConfigIO: getExperimentSetListsFromJSON(): instantiated")
        if rolledout_jsondata == None:
            logging.debug("ExperimentConfigIO: no json provided, reading from file")
            rolledout_jsondata = self.getExperimentVMRolledOut(self, configname)
        (template_vms, num_clones) = rolledout_jsondata
        sets = {}
        for template_vm in template_vms:
            for clone_num in range(num_clones):
                if str(clone_num+1) not in sets:
                    sets[str(clone_num+1)] = []
                sets[str(clone_num+1)].append(template_vms[template_vm][clone_num]["name"])
        return sets

    def getExperimentVMNamesFromTemplateFromRolledOut(self, configname, rolledout_jsondata=None):
        logging.debug("ExperimentConfigIO: getExperimentVMNamesFromTemplateFromRolledOut(): instantiated")
        if rolledout_jsondata == None:
            logging.debug("getExperimentVMNamesFromTemplateFromRolledOut(): no json provided, reading from file")
            rolledout_jsondata = self.getExperimentVMRolledOut(self, configname)
        (template_vms, num_clones) = rolledout_jsondata
        templates = {}
        for template_vm in template_vms:
            if template_vm not in templates:
                templates[template_vm] = []
            for vminfo in template_vms[template_vm]:
                vmname = vminfo["name"]
                templates[template_vm].append(vmname)
        return templates

    def getExperimentVMListsFromRolledOut(self, configname, rolledout_jsondata=None):
        logging.debug("ExperimentConfigIO: getExperimentVMListsFromRolledOut(): instantiated")
        if rolledout_jsondata == None:
            logging.debug("getExperimentVMListsFromRolledOut(): no json provided, reading from file")
            rolledout_jsondata = self.getExperimentVMRolledOut(self, configname)
        (template_vms, num_clones) = rolledout_jsondata
        vms = []
        for template_vm in template_vms:
            for cloned_vm in template_vms[template_vm]:
                vms.append(cloned_vm)
        return vms

    def getExperimentJSONFileData(self, configname, force_refresh=False):
        logging.debug("ExperimentConfigIO: getExperimentJSONFileData(): instantiated")
        if configname in self.config_jsondata:
            if force_refresh == False:
                return self.config_jsondata[configname]
        try:
            jsonconfigfile = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], configname,"Experiments",configname+".json")
            with open(jsonconfigfile) as fd:
                jsondata = json.load(fd)
            self.config_jsondata[configname] = jsondata
            return jsondata
        except FileNotFoundError:
            logging.error("getExperimentJSONFileData(): File not found: " + str(jsonconfigfile))
            return None
        except Exception:
            logging.error("Error in getExperimentJSONFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def writeExperimentXMLFileData(self, jsondata, configname):
        logging.debug("ExperimentConfigIO: writeExperimentXMLFileData(): instantiated")
        try:
            xmlconfigfile = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], configname,"Experiments",configname+".xml")
            with open(xmlconfigfile, 'w') as fd:
                xmltodict.unparse(jsondata, output=fd, pretty=True)
        except Exception:
            logging.error("Error in writeExperimentXMLFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def writeExperimentJSONFileData(self, jsondata, configname):
        logging.debug("ExperimentConfigIO: writeExperimentJSONFileData(): instantiated")
        try:
            jsonconfigfile = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], configname,"Experiments",configname+".json")
            with open(jsonconfigfile, 'w') as fd:
                json.dump(jsondata, fd, indent=4)
        except Exception:
            logging.error("Error in writeExperimentJSONFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def getExperimentXMLFilenames(self, pathcontains=""):
        logging.debug("ExperimentConfigIO: getExperimentXMLFilenames(): Instantiated")
        try:
            #First get the folds in the experiments directory as specified in the config file
            xmlExperimentFilenames = []
            xmlExperimentNames = []
            experimentpath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'])
            name_list = os.listdir(experimentpath)
            dirs = []
            for name in name_list:
                fullpath = os.path.join(experimentpath,name)
                if os.path.isdir(fullpath) and (pathcontains in name):
                    dirs.append(fullpath)
            logging.debug("getExperimentXMLFilenames(): Completed " + str(dirs))
            if dirs == None or dirs == []:
                return [xmlExperimentFilenames, xmlExperimentNames]
            #now get the actual xml experiment files
            xmlExperimentFilenames = []
            xmlExperimentNames = []
            for basepath in dirs:
                #basepath e.g., ExperimentData/sample
                xmlExperimentPath = os.path.join(basepath,"Experiments")
                #xmlExperimentPath e.g., ExperimentData/sample/Experiments
                logging.debug("getExperimentXMLFilenames(): looking at dir " + str(xmlExperimentPath))
                if os.path.exists(xmlExperimentPath):
                    xmlNameList = os.listdir(xmlExperimentPath)
                    logging.debug("getExperimentXMLFilenames(): looking at files " + str(xmlNameList))
                    #xmlNameList e.g., [sample.xml]
                    for name in xmlNameList:
                        fullpath = os.path.join(xmlExperimentPath,name)
                        logging.debug("getExperimentXMLFilenames(): looking at fullpath " + str(fullpath))
                        if fullpath.endswith(".xml"):
                            xmlExperimentFilenames.append(fullpath)
                            baseNoExt = os.path.basename(name)
                            baseNoExt = os.path.splitext(baseNoExt)[0]
                            xmlExperimentNames.append(baseNoExt)
                            logging.debug("getExperimentXMLFilenames(): adding " + str(xmlExperimentFilenames) + " " + str(xmlExperimentNames))
            return [xmlExperimentFilenames, xmlExperimentNames]

        except FileNotFoundError:
            logging.error("Error in getExperimentXMLFilenames(): Path not found: " + str(experimentpath))
            return None
        except Exception:
            logging.error("Error in getExperimentXMLFilenames(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    logging.debug("Instantiating Experiment Config IO")
    e = ExperimentConfigIO.getInstance()
    logging.info("Getting experiment folders and filenames")
    [xmlExperimentFilenames, xmlExperimentNames] = e.getExperimentXMLFilenames()
    logging.info("Contents: " + str(xmlExperimentFilenames) + " " + str(xmlExperimentNames))
    
    #Process only the first one
    confignames = xmlExperimentNames
    for configname in confignames:
    # ####READ/WRITE Test for XML data
    #     logging.info("Reading XML data for " + str(configname))
    #     data = e.getExperimentXMLFileData(configname)
    #     logging.info("JSON READ:\r\n"+json.dumps(data))   
        
    #     logging.info("Writing XML data for " + str(configname))
    #     e.writeExperimentXMLFileData(data, configname)
        
    #     logging.info("Reading XML data for " + str(configname))
    #     data = e.getExperimentXMLFileData(configname)
    #     logging.info("JSON READ:\r\n"+json.dumps(data))   

    # ####READ/WRITE Test for JSON data
    #     logging.info("Reading JSON data for " + str(configname))
    #     data = e.getExperimentJSONFileData(configname)
    #     logging.info("JSON READ:\r\n"+json.dumps(data))   

    #     logging.info("Writing JSON data for " + str(configname))
    #     e.writeExperimentJSONFileData(data, configname)

    #     logging.info("Reading JSON data for " + str(configname))
    #     data = e.getExperimentJSONFileData(configname)
    #     logging.info("JSON READ:\r\n"+json.dumps(data))   

    ####VM Rolled Out Data
        logging.info("Reading Experiment Roll Out Data for " + str(configname))
        data, numclones = e.getExperimentVMRolledOut(configname)
        logging.info("JSON READ:\r\n"+json.dumps(data))   

    logging.debug("Experiment stop complete.")    
