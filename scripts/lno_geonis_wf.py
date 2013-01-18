'''

Created on Jan 14, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import sys, os
import arcpy

from lno_geonis_base import ArcpyTool
from lno_geonis_base import getListofCommonInputs, updateParametersCommon, getMultiDirInputParameter, getMultiDirOutputParameter


class UnpackPackages(ArcpyTool):
    def __init__(self):
        pass

    @property
    def label(self):
        return "Unpack Packages"

    @property
    def alias(self):
        return "unpack"

    @property
    def description(self):
        return "Finds packages in the input directory and unpacks them into separate directories, reads the EML, and downloads the spatial data. "

    def getParameterInfo(self):
        params = getListofCommonInputs()
        self.numberCommonParams = len(params)
        params.append(arcpy.Parameter(
                        displayName = "Directory of Packages",
                        name = "in_dir",
                        datatype = "Folder",
                        parameterType = "Required",
                        direction = "Input"))
        #for indexing
        self.in_ndx = self.numberCommonParams
        params.append(getMultiDirOutputParameter())
        self.out_ndx = self.in_ndx + 1
        return params

    def updateParameters(self, parameters):
        updateParametersCommon(parameters)
        parameters[0].value = True
        return

    def updateMessages(self, parameters):
        #check for empty input dir
        return

    def execute(self, parameters, messages):
        showMsgs = parameters[0].value
        if showMsgs and self.isRunningAsTool:
            messages.AddMessage("About to create test dirs")
        else:
            arcpy.AddMessage("Not running as tool.")
        packageDir = parameters[self.in_ndx].valueAsText
        if showMsgs:
            messages.AddMessage("package dir is: " + str(os.path.isdir(packageDir)))
        outputDir = os.path.abspath(os.path.join(os.path.join(packageDir,os.path.pardir),"workflow_dirs"))
        if showMsgs:
            messages.AddMessage(str(outputDir))
        outDirList = []
        for i in range(3):
            newdir = os.path.join(outputDir, "pkg_" + str(i))
            if not os.path.isdir(newdir):
                os.mkdir(newdir)
            outDirList.append(newdir)
        arcpy.SetParameterAsText(self.out_ndx, ";".join(outDirList))
        return


class CheckSpatialData(ArcpyTool):
    def __init__(self):
        pass

    @property
    def label(self):
        return "Check Spatial Data"

    @property
    def alias(self):
        return "runchecks"

    @property
    def description(self):
        return "Performs validation checks on the spatial data found in the input directories."

    def getParameterInfo(self):
        params = getListofCommonInputs()
        self.numberCommonParams = len(params)
        params.append(getMultiDirInputParameter())
        self.in_ndx = self.numberCommonParams
        params.append(getMultiDirOutputParameter())
        self.out_ndx = self.in_ndx + 1
        return params

    def updateParameters(self, parameters):
        parameters[0].value = True
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        showMsgs = parameters[0].value
        if parameters[self.in_ndx].value:
            dirlist = parameters[self.in_ndx].valueAsText.split(';')
        else:
            dirlist = []
        if(showMsgs and self.isRunningAsTool):
            messages.AddMessage("Now running checks...")
            messages.AddMessage("number of dirs: " + str(len(dirlist)))
        else:
            arcpy.AddMessage("Testing checks...")
        for d in dirlist:
            messages.AddMessage("found d: " + d)
            messages.AddMessage(str(os.path.isdir(d)))
        #pass the list on
        arcpy.SetParameterAsText(self.out_ndx, parameters[self.in_ndx].valueAsText)
        return

class CreateMetadata(ArcpyTool):
    def __init__(self):
        pass

    @property
    def label(self):
        return "Create Metadata"

    @property
    def alias(self):
        return "metadata"

    @property
    def description(self):
        return "Creates new metadata from the EML."

    def getParameterInfo(self):
        params = getListofCommonInputs()
        self.numberCommonParams = len(params)
        params.append(getMultiDirInputParameter())
        self.in_ndx = self.numberCommonParams
        params.append(getMultiDirOutputParameter())
        self.out_ndx = self.in_ndx + 1
        return params

    def updateParameters(self, parameters):
        parameters[0].value = True
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        showMsgs = parameters[0].value
        if parameters[self.in_ndx].value:
            dirlist = parameters[self.in_ndx].valueAsText.split(';')
        else:
            dirlist = []
        if(showMsgs and self.isRunningAsTool):
            messages.AddMessage("Now creating metadata...")
            messages.AddMessage("number of dirs: " + str(len(dirlist)))
        else:
            arcpy.AddMessage("Testing checks...")
        for d in dirlist:
            messages.AddMessage("found d: " + d)
            messages.AddMessage(str(os.path.isdir(d)))
        #pass the list on
        arcpy.SetParameterAsText(self.out_ndx, parameters[self.in_ndx].valueAsText)
        return


def quicktest():
    #testtool.runAsToolboxTool()
    mytest = testtool()
    print mytest.isRunningAsTool
    print mytest.canRunInBackground
    print mytest.isLicensed()
    print mytest.label
    print mytest.description
    print mytest.getParameterInfo()
    print mytest.execute([], [])

if __name__ == '__main__':
    quicktest()
