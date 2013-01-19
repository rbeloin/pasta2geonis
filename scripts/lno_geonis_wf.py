'''

Created on Jan 14, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import sys, os
import logging
import arcpy

from lno_geonis_base import ArcpyTool
from lno_geonis_base import getListofCommonInputs, updateParametersCommon, getMultiDirInputParameter, getMultiDirOutputParameter

# module var logger
evtLogger = None

def startLogger(logpath):
    global evtLogger
    evtLogger = logging.getLogger("geonisWF")
    if logpath:
        if not os.path.isfile(logpath):
            logfile = os.path.join(logpath, "geonis_wf.log")
        else:
            logfile = logpath
        fileHandler = logging.FileHandler(logfile)
        #for files, we format with timestamp
        fileHandler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"))
        evtLogger.addHandler(fileHandler)
    else:
        evtLogger.addHandler(logging.StreamHandler())
    evtLogger.info("*************** Logging started ***************")

def logMessage(level, verbose, msg):
    global evtLogger
    if evtLogger:
        evtLogger.log(level, msg)
    if not evtLogger or verbose:
        if verbose and (level == logging.INFO or level == logging.DEBUG):
            arcpy.AddMessage(msg)
        elif level == logging.WARN or level == logging.WARNING:
            arcpy.AddWarning(msg)
        elif level == logging.ERROR or level == logging.CRITICAL:
            arcpy.AddError(msg)


class UnpackPackages(ArcpyTool):
    def __init__(self):
        pass

    @property
    def label(self):
        return "S2. Unpack Packages"

    @property
    def alias(self):
        return "unpack"

    @property
    def description(self):
        return "Finds packages in the input directory and unpacks them into separate directories, reads the EML, and downloads the spatial data. "

    def getParameterInfo(self):
        params = getListofCommonInputs()
        params.append(arcpy.Parameter(
                        displayName = "Directory of Packages",
                        name = "in_dir",
                        datatype = "Folder",
                        parameterType = "Required",
                        direction = "Input"))
        params.append(getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        updateParametersCommon(parameters)
        #parameters[0].value = True
        if not evtLogger and self.isRunningAsTool and parameters[1] and parameters[1].value:
            startLogger(parameters[1].valueAsText)
        if evtLogger:
            if parameters[0].value:
                evtLogger.setLevel(logging.DEBUG)
            else:
                evtLogger.setLevel(logging.INFO)

    def updateMessages(self, parameters):
        #check for empty input dir
        pass

    def execute(self, parameters, messages):
        showMsgs = parameters[0].value
        logMessage(logging.INFO, showMsgs,"uppacking, making dirs")
        logMessage(logging.INFO, showMsgs, "About to create test dirs")
        packageDir = parameters[2].valueAsText
        logMessage(logging.DEBUG , showMsgs,"package dir is: " + str(os.path.isdir(packageDir)))
        outputDir = os.path.abspath(os.path.join(os.path.join(packageDir,os.path.pardir),"workflow_dirs"))
        logMessage( logging.INFO, showMsgs,  str(outputDir))
        outDirList = []
        for i in range(3):
            newdir = os.path.join(outputDir, "pkg_" + str(i))
            if not os.path.isdir(newdir):
                os.mkdir(newdir)
            outDirList.append(newdir)
        arcpy.SetParameterAsText(3, ";".join(outDirList))


class CheckSpatialData(ArcpyTool):
    def __init__(self):
        pass

    @property
    def label(self):
        return "S3. Check Spatial Data"

    @property
    def alias(self):
        return "runchecks"

    @property
    def description(self):
        return "Performs validation checks on the spatial data found in the input directories."

    def getParameterInfo(self):
        params = getListofCommonInputs()
        params.append(getMultiDirInputParameter())
        params.append(getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        if not evtLogger and self.isRunningAsTool and parameters[1] and parameters[1].value:
            startLogger(parameters[1].valueAsText)
        if evtLogger:
            if parameters[0].value:
                evtLogger.setLevel(logging.DEBUG)
            else:
                evtLogger.setLevel(logging.WARNING)


    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        showMsgs = parameters[0].value
        logMessage(logging.INFO, showMsgs,  "Checking data")
        if parameters[2].value:
            dirlist = parameters[2].valueAsText.split(';')
        else:
            dirlist = []
        logMessage(logging.INFO, showMsgs,  "Testing checks...")
        for d in dirlist:
            logMessage(logging.DEBUG, showMsgs,  "found d: " + d)
            logMessage(logging.DEBUG, showMsgs,  str(os.path.isdir(d)))
        #pass the list on
        arcpy.SetParameterAsText(3, parameters[2].valueAsText)
        return

class CreateMetadata(ArcpyTool):
    def __init__(self):
        pass

    @property
    def label(self):
        return "S3. Create Metadata"

    @property
    def alias(self):
        return "metadata"

    @property
    def description(self):
        return "Creates new metadata from the EML."

    def getParameterInfo(self):
        params = getListofCommonInputs()
        params.append(getMultiDirInputParameter())
        params.append(getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        if not evtLogger and self.isRunningAsTool and parameters[1] and parameters[1].value:
            startLogger(parameters[1].valueAsText)
        if evtLogger:
            if parameters[0].value:
                evtLogger.setLevel(logging.DEBUG)
            else:
                evtLogger.setLevel(logging.WARNING)


    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        showMsgs = parameters[0].value
        logMessage(logging.INFO, showMsgs, "Now making metadata")
        if parameters[2].value:
            dirlist = parameters[2].valueAsText.split(';')
        else:
            dirlist = []
            logMessage(logging.DEBUG, showMsgs , "number of dirs: " + str(len(dirlist)))
        for d in dirlist:
            logMessage( logging.DEBUG, showMsgs,  "found d: " + d)
        #pass the list on
        arcpy.SetParameterAsText(3, parameters[2].valueAsText)
        return


def quicktest():
    #testtool.runAsToolboxTool()
    startLogger(None)
    evtLogger.debug("What's up?")



if __name__ == '__main__':
    quicktest()
