#This file will read the XML data and make it available as JSON
import xmltodict
import logging
import json
import sys, traceback
from engine.Configuration.SystemConfigIO import SystemConfigIO
import os

class ExperimentConfigIO:
    def __init__(self):
        self.s = SystemConfigIO()

    def getExperimentXMLFileData(self, configname):
        logging.debug("ExperimentConfigIO: getExperimentXMLFileData(): instantiated")
        try:
            xmlconfigfile = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], configname,"Experiments",configname+".xml")
            with open(xmlconfigfile) as fd:
                jsondata = xmltodict.parse(fd.read(), process_namespaces=True)
            return jsondata
        except FileNotFoundError:
            logging.error("Error in getExperimentXMLFileData(): File not found: " + str(xmlconfigfile))
            return None
        except Exception:
            logging.error("Error in getExperimentXMLFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def getExperimentVMRolledOut(self, configname):
        logging.debug("ExperimentConfigIO: getExperimentXMLFileData(): instantiated")
        ## Sample RolledOut JSON:
        # { 
        # "defaulta" : 
        #    [
        #       {
        #          "name": "defaulta1",
        #          "group-name": "/sample/Unit1/",
        #          "nets": ["test1", "test2"],
        #          "vrdpPort": "1001"
        #       },
        #       {
        #          "name": "defaulta2",
        #          "group-name": "/sample/Unit1/",
        #          "nets": ["test1"],
        #          "vrdpPort": "1002"
        #       }
        #    ]
        # } 
        try:
            vmRolledOutList = {}
            jsondata = self.getExperimentXMLFileData(configname)
            ipAddress = jsondata["xml"]["testbed-setup"]["network-config"]["ip-address"]
            vmSet = jsondata["xml"]["testbed-setup"]["vm-set"]
            pathToVirtualBox = jsondata["xml"]["vbox-setup"]["path-to-vboxmanage"]
            numClones = int(vmSet["num-clones"])
            cloneSnapshots = vmSet["clone-snapshots"]
            linkedClones = vmSet["linked-clones"]
            baseGroupname = vmSet["base-groupname"]
            baseOutname = vmSet["base-outname"]
            vrdpBaseport = vmSet["vrdp-baseport"]

            logging.debug("getExperimentVMRolledOut(): path: " + str(pathToVirtualBox) + " numClones: " + str(numClones) + " linked: " + str(linkedClones) + " baseGroup: " + str(baseGroupname) + " baseOut: " + str(baseOutname) + "vrdpBase: " + str(vrdpBaseport))
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
                if "startup" in vm and "cmd" in vm["startup"]:

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
                        #set default hypervisor and seq if they aren't specified
                        hypervisor = "vbox"
                        seq = "0"
                        if hypervisor in startupcmd:
                            hypervisor = startupcmd["hypervisor"]
                        if "seq" in startupcmd:
                            seq = startupcmd["seq"]
                        #store the data and allow for duplicate sequences (store as list)
                        if seq not in startupCmds_reformatted:
                            startupCmds_reformatted[seq] = [(hypervisor, startupcmd["exec"])]
                        else:
                            startupCmds_reformatted[seq].append[(hypervisor, startupcmd["exec"])]

                #get names for clones
                myBaseOutname = baseOutname
                for i in range(1, numClones + 1):
                    cloneVMName = vmName + myBaseOutname + str(i)
                    cloneGroupName = "/" + baseGroupname + "/Unit" + str(i)
                  
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
                        vmRolledOutList[vmName].append({"name": cloneVMName, "group-name": cloneGroupName, "networks": cloneNets, "vrdpEnabled": vrdpEnabled, "vrdpPort": vrdpBaseport, "baseGroupName": baseGroupname, "groupNum": str(i), "ip-address": ipAddress, "clone-snapshots": cloneSnapshots, "linked-clones": linkedClones, "startup-cmds": startupCmds_reformatted, "startup-cmds-delay": startupDelay})
                        vrdpBaseport = int(vrdpBaseport) + 1
                    #otherwise, don't include vrdp port
                    else:
                        vmRolledOutList[vmName].append({"name": cloneVMName, "group-name": cloneGroupName, "networks": cloneNets, "vrdpEnabled": vrdpEnabled, "baseGroupName": baseGroupname, "groupNum": str(i), "ip-address": ipAddress, "clone-snapshots": cloneSnapshots, "linked-clones": linkedClones, "startup-cmds": startupCmds_reformatted, "startup-cmds-delay": startupDelay})

                    logging.debug("getExperimentVMRolledOut(): finished setting up clone: " + str(vmRolledOutList))
            return vmRolledOutList, numClones

        except Exception:
            logging.error("Error in getExperimentVMRolledOut(): An error occured. Check that file exists and that it is properly formatted.")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def getExperimentJSONFileData(self, configname):
        logging.debug("ExperimentConfigIO: getExperimentJSONFileData(): instantiated")
        try:
            jsonconfigfile = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], configname,"Experiments",configname+".json")
            with open(jsonconfigfile) as fd:
                jsondata = json.load(fd)
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
    e = ExperimentConfigIO()
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
