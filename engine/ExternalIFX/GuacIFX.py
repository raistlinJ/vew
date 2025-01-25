import subprocess
import shutil
import xml.etree.ElementTree as ET
import shlex
import sys
import os
import logging
from guacapy import Guacamole
from engine.Configuration.SystemConfigIO import SystemConfigIO

class GuacIFX:
        
    def createUser(self, guacConn, username, password):
        logging.info("createUser(): instantiated")
        try:
            ########User creation##########
            userCreatePayload = {"username":username, "password":password, "attributes":{ "disabled":"", "expired":"", "access-window-start":"", "access-window-end":"", "valid-from":"", "valid-until":"", "timezone":0}}
            guacConn.add_user(userCreatePayload)
        except Exception as e:
            logging.error("Error during guacamole user creation: " + str(e))
            #exit()

    def createConnAssociation(self, guacConn, connName, username, ip, port):
        logging.info("createConnAssociation(): instantiated")
        try:
            #logic to add a user/connection and associate them together
            s = SystemConfigIO()
            protocol = "vnc"
            if s.getConfig()['HYPERVISOR']['ACTIVE'] == "VBOX":
                protocol = "rdp"
            ########Connection creation##########
            connCreatePayload = {"name":connName,
            "parentIdentifier":"ROOT",
            "protocol":protocol,
            "attributes":{"max-connections":"","max-connections-per-user":""},
            "activeConnections":0,
            "parameters":{
                "port":port,
                "enable-menu-animations":"true",
                "enable-desktop-composition":"true",
                "hostname":ip,
                "color-depth":"16",
                "enable-font-smoothing":"true",
                "ignore-cert":"true",
                "enable-drive":"false",
                "enable-full-window-drag":"true",
                "security":"",
                "password":"",
                "enable-wallpaper":"true",
                "create-drive-path":"true",
                "enable-theming":"true",
                "username":"",
                "console":"",
                "disable-audio":"true",
                "domain":"",
                "drive-path":"",
                "disable-auth":"",
                "server-layout":"",
                "width":"1400",
                "height":"1050",
                "dpi":"",
                "resize-method":"display-update",
                "console-audio":"",
                "enable-printing":"",
                "preconnection-id":"",
                "enable-sftp":"",
                "sftp-port":""}}
            res = guacConn.add_connection(connCreatePayload)
            logging.debug("ADD CONN RES: " + str(res))
            connID = res['identifier']
            ########Connection Permission for User#########
            connPermPayload = [{"op":"add","path":"/connectionPermissions/"+connID,"value":"READ"}]
            guacConn.grant_permission(username, connPermPayload)

        except Exception as e:
            logging.error("Error during guacamole connection creation: " + str(e))
            #exit()

    def createGuacEntries(self, inputFilename, guacHostname, guacUsername, guacPass, guacURLPath, guacConnMethod, inputFileBasename):
        logging.info("createGuacEntry(): instantiated")
        inputFileBasename = os.path.splitext(os.path.basename(inputFilename))[0]

        #######Guac connection##########
        #guacConn = Guacamole('192.168.99.102',username='guacadmin',password='guacadmin',url_path='/guacamole',method='http')
        guacConn = Guacamole(guacHostname,username=guacUsername,password=guacPass,url_path=guacURLPath, method=guacConnMethod)
        if guacConn == None:
            logging.error("Error with guac connection")
            exit()
            
        logging.debug("Connection to guac successful: " + str(guacConn))

        #######Read experiment-related info from file##########
        tree = ET.parse(inputFilename)
        root = tree.getroot()

        netConfig = root.find('testbed-setup').find('network-config')
        vmset = root.find('testbed-setup').find('vm-set')

        # ---get ip address information
        vmServerIP = netConfig.find('vm-server-ip').text

        # ---here we look at each vmset
        numClones = int(vmset.find('num-clones').text)
        cloneSnapshots = vmset.find('clone-snapshots').text
        linkedClones = vmset.find('linked-clones').text
        baseGroupname = vmset.find('base-groupname').text

        baseOutname = vmset.find('base-outname').text

        vrdpBaseport = vmset.find('vrdp-baseport').text

        #first create all users (one per clone)
        for i in range(1, numClones + 1):
            #create username
            #username = "user"+str(i)
            username = baseGroupname+str(i)
            username = ''.join(e for e in username if e.isalnum())
            logging.info( "Creating Username: " + username)
            self.createUser(guacConn, username, username)

        for vm in vmset.findall('vm'):
            vrdpEnabled = vm.find('vrdp-enabled').text
            vmname = vm.find('name').text
            #traverse through groups 
            for i in range(1, numClones + 1):
                #username = "user"+str(i)
                username = baseGroupname+str(i)
                username = ''.join(e for e in username if e.isalnum())
                
                myBaseOutname = baseOutname

                newvmName = vmname + myBaseOutname + str(i)

                # vrdp setup
                if vrdpEnabled and vrdpEnabled == 'true':
                    #guacConn, connName, username, password, ip, port):
                    self.createConnAssociation(guacConn, newvmName, username, vmServerIP, vrdpBaseport)
                    vrdpBaseport = str(int(vrdpBaseport) + 1)
        logging.info( """
        **************************************************************************************
        Guacamole User and Connection script complete
        **************************************************************************************
        """)

    def removeUser(self, guacConn, username):
        logging.info("removeUser(): instantiated")
        try:
            ########User deletion##########
            guacConn.delete_user(username)
        except Exception as e:
            logging.error("Error during guacamole user removal: " + str(e))
            #exit()

    def removeConnAssociation(self, guacConn, connName):
        logging.info("removeConnAssociation(): instantiated")
        try:
            logging.info("removeConnAssociation() instantiated()")
            #logic to add a user/connection and associate them together
            ########Connection removal##########
            res = guacConn.get_connection_by_name(connName)
            logging.debug("GET CONN RES: " + str(res))
            connID = res['identifier']
            ########Connection Permission for User#########
            guacConn.delete_connection(connID)
            logging.info("removeConnAssociation() complete")
        except Exception as e:
            logging.error("Error during guacamole connection removal: " + str(e))

    def removeGuacEntries(self, inputFilename, guacHostname, guacUsername, guacPass, guacURLPath, guacConnMethod, inputFileBasename):
        logging.info("removeGuacEntry(): instantiated")
        #######Guac connection##########
        #guacConn = Guacamole('192.168.99.102',username='guacadmin',password='guacadmin',url_path='/guacamole',method='http')
        guacConn = Guacamole(guacHostname,username=guacUsername,password=guacPass,url_path=guacURLPath, method=guacConnMethod)
        if guacConn == None:
            logging.error("Error with guac connection")
            return
            
        logging.debug("Connection to guac successful: " + str(guacConn))

        #######Read experiment-related info from file##########
        tree = ET.parse(inputFilename)
        root = tree.getroot()

        netConfig = root.find('testbed-setup').find('network-config')
        vmset = root.find('testbed-setup').find('vm-set')

        # ---get ip address information
        vmServerIP = netConfig.find('vm-server-ip').text

        # ---here we look at each vmset
        numClones = int(vmset.find('num-clones').text)
        cloneSnapshots = vmset.find('clone-snapshots').text
        linkedClones = vmset.find('linked-clones').text
        baseGroupname = vmset.find('base-groupname').text

        baseOutname = vmset.find('base-outname').text

        vrdpBaseport = vmset.find('vrdp-baseport').text

        #first get all users (one per clone)
        for i in range(1, numClones + 1):
            #create username
            #username = "user"+str(i)
            username = baseGroupname+str(i)
            username = ''.join(e for e in username if e.isalnum())
            self.removeUser(guacConn, username)

        for vm in vmset.findall('vm'):
            vrdpEnabled = vm.find('vrdp-enabled').text
            vmname = vm.find('name').text
            #traverse through groups 
            for i in range(1, numClones + 1):
                myBaseOutname = baseOutname
                newvmName = vmname + myBaseOutname + str(i)

                # vrdp setup
                if vrdpEnabled and vrdpEnabled == 'true':
                    #guacConn, connName
                    self.removeConnAssociation(guacConn, newvmName)
        logging.info( """
        **************************************************************************************
        Guacamole User and Connection removal script complete
        **************************************************************************************
        """)

if __name__ == "__main__":
    if len(sys.argv) < 6:
        logging.error("Usage: python GuacIFX.py <input xml file> <guac-server-hostname> <guac-username> <guac-pass> <guac-url-path> <guac-conn-method>")
        exit()
        logging.info("GuacIFX.py: Creating Connections, Users and associations")
    inputFilename = sys.argv[1]
    guacHostname = sys.argv[2]
    guacUsername = sys.argv[3]
    guacPass = sys.argv[4]
    guacURLPath = sys.argv[5]
    guacConnMethod = sys.argv[6]
    
    g = GuacIFX()
    g.createGuacEntries(inputFilename, guacHostname, guacUsername, guacPass, guacURLPath, guacConnMethod)
    g.removeGuacEntries(inputFilename, guacHostname, guacUsername, guacPass, guacURLPath, guacConnMethod)
    
