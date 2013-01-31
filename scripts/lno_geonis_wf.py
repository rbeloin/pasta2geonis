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
from geonis_helpers import isShapefile, isKML, isTif, isTifWorld, isASCIIRaster, isFileGDB, isJpeg, isJpegWorld

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
        params.append(arcpy.Parameter(
                        displayName = "Location for new directories",
                        name = "out_location",
                        datatype = "Folder",
                        parameterType = "Required",
                        direction = "Input"))
        params.append(self.getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        super(UnpackPackages, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        super(UnpackPackages, self).updateMessages(parameters)

    @errHandledWorkflowTask(taskName="Open Packages")
    def unzipPkg(self, apackageDir, locationDir):
        if not os.path.isdir(locationDir):
            os.mkdir(locationDir)
        outDirList = []
        for i in range(4):
            newdir = os.path.join(outputDir, "pkg_" + str(i))
            if not os.path.isdir(newdir):
                os.mkdir(newdir)
            outDirList.append(newdir)
        return outDirList

    @errHandledWorkflowTask(taskName="Parse EML")
    def parseEML(self, workDir):
        return os.path.isdir(workDir)

    @errHandledWorkflowTask(taskName="Retrieve and unzip data")
    def retrieveData(self, workDir):
        return os.path.isdir(workDir)

    def execute(self, parameters, messages):
        super(UnpackPackages, self).execute(parameters, messages)
        carryForwardList = []
        packageDir = self.getParamAsText(parameters,2)
        outputDir = self.getParamAsText(parameters, 3)
        self.logger.logMessage(DEBUG,  "in: %s; out:%s" % (packageDir, outputDir))
        dirList = self.unzipPkg(packageDir, outputDir)
        try:
            for workdir in dirList:
                self.parseEML(workdir)
                self.retrieveData(workdir)
        except Exception as err:
            self.logger.logMessage(WARN, "The data in %s will not be processed. %s" % (workdir, err.message))
        else:
            carryForwardList.append(workdir)
        arcpy.SetParameterAsText(4,  ";".join(carryForwardList))



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
    def acceptableDataType(self, apackageDir, hint = None):
        if not os.path.isdir(apackageDir):
            self.logger.logMessage(WARN,"Parameter not a directory.")
            return GeoNISDataType.NA
        contents = [os.path.join(apackageDir,item) for item in os.listdir(apackageDir)]
        self.logger.logMessage(DEBUG, str(contents))
        allTypesFound = []
        for afile in (f for f in contents if os.path.isfile(f)):
            if isShapefile(afile):
                allTypesFound.append(GeoNISDataType.SHAPEFILE)
            elif isKML(afile):
                allTypesFound.append(GeoNISDataType.KML)
            elif isTif(afile):
                allTypesFound.append(GeoNISDataType.TIF)
            elif isASCIIRaster(afile):
                allTypesFound.append(GeoNISDataType.ASCIIRASTER)
        for afolder in (f for f in contents if os.path.isdir(f)):
            if isFileGDB(afolder):
                allTypesFound.append(GeoNISDataType.FILEGEODB)
        if len(allTypesFound) > 0:
            #in most cases we probably just had one hit
            if len(allTypesFound) == 1:
                if hint is not None and allTypesFound[0] != hint:
                    self.logger.logMessage(WARN, "Expected data type not matching found data")
                return allTypesFound[0]
            #found more than one candidate
            #figure out what we really have by certainty
            #if we have a hint, use it
            if hint is not None and hint in allTypesFound:
                return hint
            #files with world files are good bets
            if GeoNISDataType.TFW in allTypesFound and GeoNISDataType.TIF in allTypesFound:
                return GeoNISDataType.TIF
            if GeoNISDataType.JPGW in allTypesFound and GeoNISDataType.JPEG in allTypesFound:
                return GeoNISDataType.JPEG
            if GeoNISDataType.FILEGEODB in allTypesFound:
                return GeoNISDataType.FILEGEODB
            if GeoNISDataType.SHAPEFILE in allTypesFound:
                return GeoNISDataType.SHAPEFILE
            if GeoNISDataType.KML in allTypesFound:
                return GeoNISDataType.KML
            if GeoNISDataType.ASCIIRASTER in allTypesFound:
                return GeoNISDataType.ASCIIRASTER
            if GeoNISDataType.TIF in allTypesFound:
                # Tif without world file. Are geotags enough?
                return GeoNISDataType.TIF
            return GeoNISDataType.NA
        else:
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
                            notesfile.write('TYPE:kml\n')
                        if spatialType == GeoNISDataType.SHAPEFILE:
                            self.logger.logMessage(INFO, "shapefile found")
                            notesfile.write('TYPE:shapefile\n')
                        if spatialType == GeoNISDataType.ASCIIRASTER:
                            self.logger.logMessage(INFO, "ascii raster found")
                            notesfile.write('TYPE:ascii raster\n')
                        if spatialType == GeoNISDataType.FILEGEODB:
                            self.logger.logMessage(INFO, "file gdb found")
                            notesfile.write('TYPE:file geodatabase\n')
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


