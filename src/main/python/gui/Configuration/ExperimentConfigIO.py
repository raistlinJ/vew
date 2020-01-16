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
            #jsonconfigfile = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], configname,"Experiments",configname+".json")
            experimentpath = os.path.join(self.s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'])
            name_list = os.listdir(experimentpath)
            dirs = []
            for name in name_list:
                fullpath = os.path.join(experimentpath,name)
                if os.path.isdir(fullpath) and (pathcontains in name):
                    dirs.append(fullpath)
            logging.debug("getExperimentXMLFilenames(): Completed " + str(dirs))
            if dirs == None or dirs == []:
                return []
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
    ####READ/WRITE Test for XML data
        logging.info("Reading XML data for " + str(configname))
        data = e.getExperimentXMLFileData(configname)
        logging.info("JSON READ:\r\n"+json.dumps(data))   
        
        logging.info("Writing XML data for " + str(configname))
        e.writeExperimentXMLFileData(data, configname)
        
        logging.info("Reading XML data for " + str(configname))
        data = e.getExperimentXMLFileData(configname)
        logging.info("JSON READ:\r\n"+json.dumps(data))   

    ####READ/WRITE Test for JSON data
        logging.info("Reading JSON data for " + str(configname))
        data = e.getExperimentJSONFileData(configname)
        logging.info("JSON READ:\r\n"+json.dumps(data))   

        logging.info("Writing JSON data for " + str(configname))
        e.writeExperimentJSONFileData(data, configname)

        logging.info("Reading JSON data for " + str(configname))
        data = e.getExperimentJSONFileData(configname)
        logging.info("JSON READ:\r\n"+json.dumps(data))   

    logging.debug("Experiment stop complete.")    
