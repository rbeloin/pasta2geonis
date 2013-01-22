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
        super(UnpackPackages, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        super(UnpackPackages, self).updateMessages(parameters)

    def execute(self, parameters, messages):
        super(UnpackPackages, self).execute(parameters, messages)
        self.logger.logMessage(DEBUG, self.showMsgs, "this is debug msg")
        self.logger.logMessage(INFO, self.showMsgs,"uppacking, making dirs")
        self.logger.logMessage(INFO, self.showMsgs, "About to create test dirs")
        packageDir = self.getParamAsText(parameters,2)
        self.logger.logMessage(DEBUG , self.showMsgs,"package dir is: " + str(os.path.isdir(packageDir)))
        outputDir = os.path.abspath(os.path.join(os.path.join(packageDir,os.path.pardir),"workflow_dirs"))
        self.logger.logMessage(INFO, self.showMsgs,  str(outputDir))
        outDirList = []
        for i in range(3):
            newdir = os.path.join(outputDir, "pkg_" + str(i))
            if not os.path.isdir(newdir):
                os.mkdir(newdir)
            outDirList.append(newdir)
        parameters[3].value = ";".join(outDirList)



class CheckSpatialData(ArcpyTool):
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = "Performs validation checks on the spatial data found in the input directories."
        self._label = "S3. Check Spatial Data"
        self._alias = "runchecks"

    def getParameterInfo(self):
        params = super(CheckSpatialData, self).getParameterInfo()
        params.append(self.getMultiDirInputParameter())
        params.append(self.getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        super(CheckSpatialData, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        super(CheckSpatialData, self).updateMessages(parameters)

    def execute(self, parameters, messages):
        super(CheckSpatialData, self).execute(parameters, messages)
        self.logger.logMessage(INFO, self.showMsgs,  "Checking data")
        if parameters[2].value:
            dirlist = parameters[2].valueAsText.split(';')
        else:
            dirlist = []
        for d in dirlist:
            self.logger.logMessage(INFO, self.showMsgs,  "found directory: " + d)
        #pass the list on
        arcpy.SetParameterAsText(3, parameters[2].valueAsText)
        return

class CreateMetadata(ArcpyTool):
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = "Creates new metadata from the EML."
        self._label = "S4. Create Metadata"
        self._alias = "metadata"

    def getParameterInfo(self):
        params = super(CreateMetadata, self).getParameterInfo()
        params.append(self.getMultiDirInputParameter())
        params.append(self.getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        super(CreateMetadata, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        super(CreateMetadata, self).updateMessages(parameters)

    def execute(self, parameters, messages):
        super(CreateMetadata, self).execute(parameters, messages)
        self.logger.logMessage(INFO, self.showMsgs,  "Metadata started.")
        if parameters[2].value:
            dirlist = parameters[2].valueAsText.split(';')
        else:
            dirlist = []
        for d in dirlist:
            self.logger.logMessage(INFO, self.showMsgs,  "found directory: " + d)
        #pass the list on
        arcpy.SetParameterAsText(3, parameters[2].valueAsText)
        return



#this is imported into Toolbox.pyt file and used to instantiate tools
toolclasses =  [UnpackPackages,
                CheckSpatialData,
                CreateMetadata]


