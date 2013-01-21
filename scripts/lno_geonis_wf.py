'''

Created on Jan 14, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import sys, os
import arcpy
from geonis_log import EvtLog
from arcpy import AddMessage as arcAddMsg, AddError as arcAddErr, AddWarning as arcAddWarn
from logging import DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL

from lno_geonis_base import ArcpyTool


class UnpackPackages(ArcpyTool):
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = "Finds packages in the input directory and unpacks them into separate directories, reads the EML, and downloads the spatial data. "
        self._label = "S2. Unpack Packages"
        self._alias = "unpack"

    def getParameterInfo(self):
        params = super(UnpackPackages,self).getParameterInfo()
        params.append(arcpy.Parameter(
                        displayName = "Directory of Packages",
                        name = "in_dir",
                        datatype = "Folder",
                        parameterType = "Required",
                        direction = "Input"))
        params.append(self.getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        super(UnpackPackages, self).updateParameters()

    def updateMessages(self, parameters):
        super(UnpackPackages, self).updateMessages()

    def execute(self, parameters, messages):
        super(UnpackPackages, self).execute(parameters, messages)
        self.logger.logMessage(DEBUG, self.showMsgs, "this is debug msg")
        self.logger.logMessage(INFO, self.showMsgs,"uppacking, making dirs")
        self.logger.logMessage(INFO, self.showMsgs, "About to create test dirs")
        """
        packageDir = parameters[2].valueAsText
        logger.logMessage(logging.DEBUG , showMsgs,"package dir is: " + str(os.path.isdir(packageDir)))
        outputDir = os.path.abspath(os.path.join(os.path.join(packageDir,os.path.pardir),"workflow_dirs"))
        logger.logMessage( logging.INFO, showMsgs,  str(outputDir))
        outDirList = []
        for i in range(3):
            newdir = os.path.join(outputDir, "pkg_" + str(i))
            if not os.path.isdir(newdir):
                os.mkdir(newdir)
            outDirList.append(newdir)
        #arcpy.SetParameterAsText(3, ";".join(outDirList))
        """


##class CheckSpatialData(ArcpyTool):
##    def __init__(self):
##        pass
##
##    @property
##    def label(self):
##        return "S3. Check Spatial Data"
##
##    @property
##    def alias(self):
##        return "runchecks"
##
##    @property
##    def description(self):
##        return "Performs validation checks on the spatial data found in the input directories."
##
##    def getParameterInfo(self):
##        params = getListofCommonInputs()
##        params.append(getMultiDirInputParameter())
##        params.append(getMultiDirOutputParameter())
##        return params
##
##    def updateParameters(self, parameters):
##        pass
##
##
##    def updateMessages(self, parameters):
##        return
##
##    def execute(self, parameters, messages):
####        showMsgs = parameters[0].value
####        logMessage(logging.INFO, showMsgs,  "Checking data")
####        if parameters[2].value:
####            dirlist = parameters[2].valueAsText.split(';')
####        else:
####            dirlist = []
####        logMessage(logging.INFO, showMsgs,  "Testing checks...")
####        for d in dirlist:
####            logMessage(logging.DEBUG, showMsgs,  "found d: " + d)
####            logMessage(logging.DEBUG, showMsgs,  str(os.path.isdir(d)))
##        #pass the list on
##        arcpy.SetParameterAsText(3, parameters[2].valueAsText)
##        return
##
##class CreateMetadata(ArcpyTool):
##    def __init__(self):
##        pass
##
##    @property
##    def label(self):
##        return "S3. Create Metadata"
##
##    @property
##    def alias(self):
##        return "metadata"
##
##    @property
##    def description(self):
##        return "Creates new metadata from the EML."
##
##    def getParameterInfo(self):
##        params = getListofCommonInputs()
##        params.append(getMultiDirInputParameter())
##        params.append(getMultiDirOutputParameter())
##        return params
##
##    def updateParameters(self, parameters):
##        pass
##
##
##    def updateMessages(self, parameters):
##        pass
##
##    def execute(self, parameters, messages):
##        showMsgs = parameters[0].value
####        logMessage(logging.INFO, showMsgs, "Now making metadata")
####        if parameters[2].value:
####            dirlist = parameters[2].valueAsText.split(';')
####        else:
####            dirlist = []
####            logMessage(logging.DEBUG, showMsgs , "number of dirs: " + str(len(dirlist)))
####        for d in dirlist:
####            logMessage( logging.DEBUG, showMsgs,  "found d: " + d)
##        #pass the list on
##        arcpy.SetParameterAsText(3, parameters[2].valueAsText)
##        return


def quicktest():
    #testtool.runAsToolboxTool()
    unpack = UnpackPackages()
    params = unpack.getParameterInfo()
    params[0].value = True
    params[1].value = None
    unpack.execute(params,[])





if __name__ == '__main__':
    quicktest()
