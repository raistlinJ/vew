import sys, traceback
from subprocess import Popen
import logging

PATH_TO_FIREFOX="C:/Program Files/Mozilla Firefox/firefox.exe"

#take from: http://code.activestate.com/recipes/577279-generate-list-of-numbers-from-hyphenated-and-comma/
def hyphen_range(s):
    """ Takes a range in form of "a-b" and generate a list of numbers between a and b inclusive.
    Also accepts comma separated ranges like "a-b,c-d,f" will build a list which will include
    Numbers from a to b, a to d and f"""
    s="".join(s.split())#removes white space
    r=set()
    for x in s.split(','):
        t=x.split('-')
        if len(t) not in [1,2]: raise SyntaxError("hash_range is given its arguement as "+s+" which seems not correctly formated.")
        r.add(int(t[0])) if len(t)==1 else r.update(set(range(int(t[0]),int(t[1])+1)))
    l=list(r)
    l.sort()
    return l
 
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    if len(sys.argv) < 5:
        logging.error("Usage: python guacStartConns.py <baseURL> <baseUser> <basePass> <connsRange> [additional arguments]*")
        exit()
        logging.info("guacStartConns.py: Creating Connections, Users and associations")
    baseURL = str(sys.argv[1])
    baseUser = str(sys.argv[2])
    basePass = str(sys.argv[3])
    connsRange = str(sys.argv[4])
    if len(sys.argv) > 4:
        additionalArguments = sys.argv[5:]
    
    logging.debug("baseURL: " + baseURL)
    try:
        for instance in hyphen_range(connsRange):
            username = baseUser + str(instance)
            cmd = PATH_TO_FIREFOX + " -private-window" + " \"" + baseURL + "/#/?username=" + username + "&password=" + username + "\""
            logging.debug("Running command: " + cmd)
            p = Popen(cmd)
            logging.debug("Instantiating connection number: " + str(instance))
    except Exception:
            logging.error("Error in getExperimentXMLFileData(): An error occured ")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)