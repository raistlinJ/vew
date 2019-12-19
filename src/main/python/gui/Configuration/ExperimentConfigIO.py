#This file will read the XML data and make it available as JSON
import xmltodict

class ExperimentConfigIO:
    def __init__(self):
        pass

    def getExperimentFileData(self, configfilename):
        with open(configfilename) as fd:
            jsondata = xmltodict.parse(fd.read(), process_namespaces=True)
        return jsondata