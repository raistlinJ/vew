#This file will read the XML data and make it available as JSON
import xmltodict
import logging
import json
import sys, traceback
from gui.Configuration.SystemConfigIO import SystemConfigIO
import os

class ExperimentConfigIO:
    def __init__(self):
        pass

    def getExperimentXMLFileData(self, configfilename):
        logging.debug("getExperimentXMLFileData(): instantiated")
        try:    
            with open(configfilename) as fd:
                jsondata = xmltodict.parse(fd.read(), process_namespaces=True)
            return jsondata
        except FileNotFoundError:
            logging.error("Error in getExperimentXMLFileData(): File not found: " + str(configfilename))
            return None
        except Exception:
            logging.error("Error in getExperimentXMLFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def getExperimentJSONFileData(self, configfilename):
        logging.debug("getExperimentJSONFileData(): instantiated")
        try:
            with open(configfilename) as fd:
                jsondata = json.load(fd)
            return jsondata
        except FileNotFoundError:
            logging.error("getExperimentJSONFileData(): File not found: " + str(configfilename))
            return None
        except Exception:
            logging.error("Error in getExperimentJSONFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def writeExperimentXMLFileData(self, jsondata, configfilename):
        logging.debug("writeExperimentXMLFileData(): instantiated")
        try:
            with open(configfilename, 'w') as fd:
                xmltodict.unparse(jsondata, output=fd, pretty=True)
        except Exception:
            logging.error("Error in writeExperimentXMLFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

    def writeExperimentJSONFileData(self, jsondata, configfilename):
        logging.debug("writeExperimentJSONFileData(): instantiated")
        try:
            with open(configfilename, 'w') as fd:
                json.dump(jsondata, fd, indent=4)
        except Exception:
            logging.error("Error in writeExperimentJSONFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return None

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    logging.debug("Instantiating Experiment Config IO")
    e = ExperimentConfigIO()
    s = SystemConfigIO()
    xmlconfigfile = os.path.join(s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], "sample","Experiments","sample_configfile.xml")
    jsonconfigfile = os.path.join(s.getConfig()['EXPERIMENTS']['EXPERIMENTS_PATH'], "sample","Experiments","sample_configfile.json")
####READ/WRITE Test for XML data
    logging.info("Reading XML data")
    data = e.getExperimentXMLFileData(xmlconfigfile)
    logging.info("JSON READ:\r\n"+json.dumps(data))   
    
    logging.info("Writing XML data")
    e.writeExperimentXMLFileData(data, xmlconfigfile)
    
    logging.info("Reading XML data")
    data = e.getExperimentXMLFileData(xmlconfigfile)
    logging.info("JSON READ:\r\n"+json.dumps(data))   

####READ/WRITE Test for JSON data
    logging.info("Reading JSON data")
    data = e.getExperimentJSONFileData(jsonconfigfile)
    logging.info("JSON READ:\r\n"+json.dumps(data))   

    logging.info("Writing JSON data")
    e.writeExperimentJSONFileData(data, jsonconfigfile)

    logging.info("Reading JSON data")
    data = e.getExperimentJSONFileData(jsonconfigfile)
    logging.info("JSON READ:\r\n"+json.dumps(data))   

    logging.debug("Experiment stop complete.")    
