#This file will read the XML data and make it available as JSON
import xmltodict
import logging
import json
import sys, traceback
from engine.Configuration.SystemConfigIO import SystemConfigIO
from engine.Configuration.ExperimentConfigIO import ExperimentConfigIO
import os

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    logging.debug("Instantiating Experiment Config IO")
    e = ExperimentConfigIO()
    logging.info("Getting experiment folders and filenames")
    [xmlExperimentFilenames, xmlExperimentNames] = e.getExperimentXMLFilenames()
    logging.info("Contents: " + str(xmlExperimentFilenames) + " " + str(xmlExperimentNames))

###UNCOMMENT TO TEST ALL CONFIGS
    #Process only the first one
    # confignames = xmlExperimentNames
    # for configname in confignames:
    # # ####READ/WRITE Test for XML data
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

    # ####VM Rolled Out Data
    #     logging.info("Reading Experiment Roll Out Data for " + str(configname))
    #     data, numclones = e.getExperimentVMRolledOut(configname)
    #     logging.info("JSON READ:\r\n"+json.dumps(data))   

    # logging.debug("Experiment stop complete.")    

###TEST A SINGLE CONFIG
    #Process only the first one
    #confignames = xmlExperimentNames
    configname = "sample"
    #for configname in confignames:
    # ####READ/WRITE Test for XML data
    logging.info("Reading XML data for " + str(configname))
    data = e.getExperimentXMLFileData(configname)
    #logging.info("JSON READ:\r\n"+json.dumps(data))   
        
    logging.info("Writing XML data for " + str(configname))
    e.writeExperimentXMLFileData(data, configname)
        
    logging.info("Reading XML data for " + str(configname))
    data = e.getExperimentXMLFileData(configname)
    # logging.info("JSON READ:\r\n"+json.dumps(data))   

    ####READ/WRITE Test for JSON data
    logging.info("Reading JSON data for " + str(configname))
    data = e.getExperimentJSONFileData(configname)
    logging.info("JSON READ:\r\n"+json.dumps(data))   

    logging.info("Writing JSON data for " + str(configname))
    e.writeExperimentJSONFileData(data, configname)

    logging.info("Reading JSON data for " + str(configname))
    data = e.getExperimentJSONFileData(configname)
    logging.info("JSON READ:\r\n"+json.dumps(data))   

    ####VM Rolled Out Data
    logging.info("Reading Experiment Roll Out Data for " + str(configname))
    data, numclones = e.getExperimentVMRolledOut(configname)
    logging.info("JSON READ:\r\n"+json.dumps(data))   

    logging.debug("Experiment stop complete.")    