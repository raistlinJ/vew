import logging
import sys, traceback
import threading
import json
from engine.Manager.PackageManage.PackageManage import PackageManage
from engine.Manager.PackageManage.PackageManageVBox import PackageManageVBox
from engine.Manager.VMManage.VBoxManage import VBoxManage
from engine.Manager.VMManage.VBoxManageWin import VBoxManageWin
from engine.Configuration.SystemConfigIO import SystemConfigIO
import zipfile
import os
import time

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Starting Program")

    resfilename = "samples\sample.res"

    logging.debug("Instantiating Experiment Config IO")
    p = PackageManageVBox()
    logging.info("Importing file")
    p.importPackage(resfilename)
    logging.info("Operation Complete")