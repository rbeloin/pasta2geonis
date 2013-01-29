'''

Created on Jan 14, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import sys, os
import arcpy
from geonis_log import EvtLog, errHandledWorkflowTask
from arcpy import AddMessage as arcAddMsg, AddError as arcAddErr, AddWarning as arcAddWarn
from arcpy import Parameter
from logging import DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL
from lno_geonis_base import ArcpyTool
from geonis_pyconfig import GeoNISDataType
from geonis_helpers import isShapefile, isKML, isTif

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

    @errHandledWorkflowTask(taskName="unzip main package")
    def unzipPkg(self, apackageDir):
        return os.path.isdir(apackageDir)

    def execute(self, parameters, messages):
        super(UnpackPackages, self).execute(parameters, messages)
        packageDir = self.getParamAsText(parameters,2)
        self.logger.logMessage(DEBUG , "package dir found? " + str(os.path.isdir(packageDir)))
        outputDir = os.path.abspath(os.path.join(os.path.join(packageDir,os.path.pardir),"workflow_dirs"))
        self.logger.logMessage(DEBUG,  "output directory: " + str(outputDir))
        outDirList = []
        for i in range(3):
            newdir = os.path.join(outputDir, "pkg_" + str(i))
            if not os.path.isdir(newdir):
                os.mkdir(newdir)
            outDirList.append(newdir)
        if self.unzipPkg(r"c:\arcgis"):
            self.logger.logMessage(INFO, "got true from task")
        arcpy.SetParameterAsText( 3,  ";".join(outDirList))



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
        params.append(Parameter(
                        displayName = "Report from checks",
                        name = "report",
                        datatype = "String",
                        direction = "Output",
                        parameterType = "Derived",
                        multiValue = False))
        return params

    def updateParameters(self, parameters):
        super(CheckSpatialData, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        super(CheckSpatialData, self).updateMessages(parameters)

    @errHandledWorkflowTask(taskName="Data type check")
    def acceptableDataType(self, apackageDir):
        if not os.path.isdir(apackageDir):
            return GeoNISDataType.NA
        files = os.listdir(apackageDir)
        for afile in (os.path.join(apackageDir,f) for f in files):
            if isShapefile(afile):
                return GeoNISDataType.SHAPEFILE
            elif isKML(afile):
                return GeoNISDataType.KML
        return GeoNISDataType.NA

    @errHandledWorkflowTask(taskName="Format report")
    def getReport(self, notesfilePath):
        retval = {}
        pkgname = os.path.dirname(notesfilePath)
        with open(notesfilePath) as notesfile:
            retval[pkgname] = " ".join(notesfile.readlines())
        return retval

    def execute(self, parameters, messages):
        super(CheckSpatialData, self).execute(parameters, messages)
        try:
            assert self.inputDirs != None
            assert self.outputDirs != None
            reportText = []
            for dataDir in self.inputDirs:
                notesfilePath = os.path.join(dataDir,"pkgID_geonis_notes.txt")
                reportfilePath = os.path.join(dataDir, "pkgID_geonis_report.txt")
                with open(notesfilePath,'w') as notesfile:
                    try:
                        spatialType = self.acceptableDataType(dataDir)
                        if spatialType == GeoNISDataType.NA:
                            raise Exception("No compatible data found in %s" % dataDir)
                        if spatialType == GeoNISDataType.KML:
                            self.logger.logMessage(INFO, "kml  found")
                            notesfile.write('Checking as kml vector\n')
                        if spatialType == GeoNISDataType.SHAPEFILE:
                            self.logger.logMessage(INFO, "shapefile found")
                            notesfile.write('Checking as shapefile\n')
                        self.logger.logMessage(INFO, "working in: " + dataDir)
                    except Exception as e:
                        self.logger.logMessage(WARN, e.message)
                    else:
                        self.outputDirs.append(dataDir)
                reportText.append(self.getReport(notesfilePath))
            arcpy.SetParameterAsText(3, ";".join(self.outputDirs))
            arcpy.SetParameterAsText(4,str(reportText))
        except AssertionError:
            self.logger.logMessage(CRITICAL, "expected parameter not found")
            sys.exit(1)
        except Exception as crit:
            self.logger.logMessage(CRITICAL, crit.message)
            sys.exit(1)



class GatherMetadata(ArcpyTool):
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = "Creates new metadata from the EML."
        self._label = "S4. Gather Metadata"
        self._alias = "metadata"

    def getParameterInfo(self):
        params = super(GatherMetadata, self).getParameterInfo()
        params.append(self.getMultiDirInputParameter())
        params.append(self.getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        super(GatherMetadata, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        super(GatherMetadata, self).updateMessages(parameters)

    def execute(self, parameters, messages):
        super(GatherMetadata, self).execute(parameters, messages)
        if parameters[2].value:
            dirlist = self.getParamAsText(parameters, 2).split(';')
        else:
            dirlist = []
        for d in dirlist:
            self.logger.logMessage(INFO, "working in: " + d)
        #pass the list on
        arcpy.SetParameterAsText(3, self.getParamAsText( parameters, 2))


#this is imported into Toolbox.pyt file and used to instantiate tools
toolclasses =  [UnpackPackages,
                CheckSpatialData,
                GatherMetadata]


