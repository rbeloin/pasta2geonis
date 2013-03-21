'''

Created on Jan 14, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import sys, os, re
import time, datetime
import json
import httplib, urllib, urllib2
from HTMLParser import HTMLParser
import psycopg2
from shutil import copyfileobj
from zipfile import ZipFile
from lxml import etree
import arcpy
from geonis_log import EvtLog, errHandledWorkflowTask
from arcpy import AddMessage as arcAddMsg, AddError as arcAddErr, AddWarning as arcAddWarn
from arcpy import Parameter
from logging import DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL
from lno_geonis_base import ArcpyTool
from geonis_pyconfig import GeoNISDataType, tempMetadataFilename, geodatabase
from geonis_pyconfig import pathToRasterData, pathToRasterMosaicDatasets, pathToStylesheets, dsnfile, pathToMapDoc, layerQueryURI, pubConnection, mapServInfo
from geonis_helpers import isShapefile, isKML, isTif, isTifWorld, isASCIIRaster, isFileGDB, isJpeg, isJpegWorld, isEsriE00, isRasterDS, isProjection
from geonis_helpers import siteFromId, getToken
from geonis_emlparse import createEmlSubset, createEmlSubsetWithNode, writeWorkingDataToXML, readWorkingData, readFromEmlSubset, createSuppXML, stringToValidName
from geonis_postgresql import cursorContext, getPackageInsert, getEntityInsert

## *****************************************************************************
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

    @errHandledWorkflowTask(taskName="Open Package")
    def unzipPkg(self, apackage, locationDir):
        name, ext = os.path.splitext(os.path.basename(apackage))
        testpath = os.path.join(locationDir,name)
        destpath = testpath
        i = 1
        while os.path.isdir(destpath):
            destpath = '%s_%i' % (testpath,i)
            i += 1
        with ZipFile(apackage) as pkg:
            if pkg.testzip() is None:
                pkg.extractall(destpath)
            else:
                self.logger.logMessage(WARN,"%s did not pass zip test." % (apackage,))
                raise Exception("Zip test fail.")
        return destpath

    @errHandledWorkflowTask(taskName="Parse EML")
    def parseEML(self, workDir):
        retval = []
        emldatafile = os.path.join(workDir,tempMetadataFilename)
        pkgfiles = os.listdir(workDir)
        xmlfiles = [f for f in pkgfiles if f[-4:].lower() == '.xml']
        if len(xmlfiles) == 0:
            self.logger.logMessage(WARN,"No xml files in %s" % (workDir,))
            raise Exception("No xml file in package.")
        elif len(xmlfiles) > 1:
            xmlfiles = [f for f in xmlfiles if f[:8].lower() == 'knb-lter']
            if len(xmlfiles) != 1:
                self.logger.logMessage(WARN,"More than one EML file in %s ?" % (workDir,))
                if len(xmlfiles) == 0:
                    raise Exception("No EML file in package.")
        emlfile = os.path.join(workDir, xmlfiles[0])
        pkgId, dataEntityNum = createEmlSubset(workDir, emlfile)
        for i in range(dataEntityNum):
            parentDir = os.path.dirname(workDir)
            path = parentDir + os.sep + pkgId + "." + str(i)
            if not os.path.exists(path):
                os.mkdir(path)
            createEmlSubsetWithNode(workDir, path, i + 1, self.logger)
            retval.append(path)
        return (pkgId, retval)
##        emldata = parseAndPopulateEMLDicts(emlfile, self.logger)
##        with open(emldatafile,'w') as datafile:
##            datafile.write(repr(emldata))

    @errHandledWorkflowTask(taskName="Package initial entry")
    def makePackageRec(self, pkgId):
        """Inserts record into package table """
        stmt, vals = getPackageInsert()
        vals["packageid"] = pkgId
        scope, id, rev = siteFromId(pkgId)
        vals["scope"] = scope
        vals["identifier"] = id
        vals["revision"] = rev
        with cursorContext(self.logger) as cur:
            cur.execute(stmt, vals)

    @errHandledWorkflowTask(taskName="Read URL from emlSubset")
    def readURL(self, workDir):
        emldata = readWorkingData(workDir, self.logger)
        url = readFromEmlSubset(workDir, "//physical/distribution/online/url", self.logger)
        if len(url) > 0:
            emldata["physical/distribution/online/url"] = url
            writeWorkingDataToXML(workDir, emldata, self.logger)


    @errHandledWorkflowTask(taskName="Retrieve and unzip data")
    def retrieveData(self, workDir):
        emldata = readWorkingData(workDir, self.logger)
        dataloc = emldata["physical/distribution/online/url"]
        if dataloc is not None:
            try:
                uri = HTMLParser().unescape(dataloc)
                sdatafile = os.path.join(workDir,emldata["shortEntityName"] + '.zip')
                resource = urllib2.urlopen(uri)
                with open(sdatafile,'wb') as dest:
                    copyfileobj(resource,dest)
            except Exception as e:
                raise Exception(e.message)
            finally:
                if resource:
                    resource.close()
            if not os.path.exists(sdatafile):
                raise Exception("spatial data file %s missing after download" % (sdatafile,))
            with ZipFile(sdatafile) as sdata:
                if sdata.testzip() is None:
                    sdata.extractall(workDir)
                else:
                    self.logger.logMessage(WARN,"%s did not pass zip test." % (sdatafile,))
                    raise Exception("Zip test fail.")
            #TODO: check to see if only a dir after unpacking. Its contents may need to be raised to the current dir level
        else:
            self.logger.logMessage(WARN, "URL for data source missing.")
            raise Exception("No URL for data in %s" % (workDir,))


    @errHandledWorkflowTask(taskName="Entity initial entry")
    def makeEntityRec(self, workDir):
        """Inserts record into entity table """
        emldata = readWorkingData(workDir, self.logger)
        stmt, vals = getEntityInsert()
        vals["packageid"] = emldata["packageId"]
        vals["entityname"] = emldata["entityName"]
        vals["entitydescription"] = emldata["entityDesc"][:999]
        vals["status"] = "%s node found. Downloaded." % emldata["spatialType"]
        if emldata["spatialType"] == "spatialVector":
            vals["isvector"] = True
        elif emldata["spatialType"] == "spatialRaster":
            vals["israster"] = True
        with cursorContext(self.logger) as cur:
            cur.execute(stmt, vals)

    def execute(self, parameters, messages):
        super(UnpackPackages, self).execute(parameters, messages)
        carryForwardList = []
        packageDir = self.getParamAsText(parameters,2)
        outputDir = self.getParamAsText(parameters, 3)
        self.logger.logMessage(DEBUG,  "in: %s; out:%s" % (packageDir, outputDir))
        if not os.path.isdir(outputDir):
            os.mkdir(outputDir)
        allpackages = [os.path.join(packageDir,f) for f in os.listdir(packageDir) if os.path.isfile(os.path.join(packageDir,f)) and f[-4:].lower() == '.zip']
        #loop over packages, handling one at a time. an error will drop the current package and go to the next one
        for pkg in allpackages:
            try:
                workdir = self.unzipPkg(pkg, outputDir)
                packageId, dataDirs = self.parseEML(workdir)
                self.makePackageRec(packageId)
                for dir in dataDirs:
                    #loop over data package dirs, in most cases just one, if error keep trying others
                    try:
                        initWorkingData = readWorkingData(dir, self.logger)
                        if initWorkingData["spatialType"] is None:
                            self.logger.logMessage(WARN, "No EML spatial node. The data in %s with id %s will not be processed." % (pkg, packageId))
                            continue
                        self.readURL(dir)
                        self.retrieveData(dir)
                        self.makeEntityRec(dir)
                        carryForwardList.append(dir)
                    except Exception as err:
                        self.logger.logMessage(WARN, "The data in %s will not be processed. %s" % (dir, err.message))
            except Exception as err:
                self.logger.logMessage(WARN, "The data in %s will not be processed. %s" % (pkg, err.message))
        arcpy.SetParameterAsText(4,  ";".join(carryForwardList))


## *****************************************************************************
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

    @errHandledWorkflowTask(taskName="Examine EML data for type")
    def examineEMLforType(self, emldata):
        spatialTypeItem = emldata["spatialType"]
        if spatialTypeItem == "spatialVector":
            retval = GeoNISDataType.SPATIALVECTOR
        elif spatialTypeItem == "spatialRaster":
            retval = GeoNISDataType.SPATIALRASTER
        else:
            self.logger.logMessage(WARN,"EML spatial type is %s, should be either 'spatialVector' or 'spatialRaster'." % (spatialTypeItem,))
            raise Exception("EML spatialType not found.")
        # now see if can find out more specifically
        entDescStr = emldata["entityDesc"]
        if retval == GeoNISDataType.SPATIALVECTOR:
            for fileext in [GeoNISDataType.SHAPEFILE, GeoNISDataType.KML, GeoNISDataType.FILEGEODB]:
                for ext in fileext:
                    pat = r"\b%s\b" % (ext[1:],)
                    if re.search(pat, entDescStr) is not None:
                        retval = fileext
                        return retval
        else:
            for fileext in [GeoNISDataType.TIF, GeoNISDataType.ESRIE00, GeoNISDataType.JPEG, GeoNISDataType.ASCIIRASTER, GeoNISDataType.FILEGEODB]:
                for ext in fileext:
                    pat = r"\b%s\b" % (ext[1:],)
                    if re.search(pat, entDescStr) is not None:
                        retval = fileext
                        return retval
        return retval


    @errHandledWorkflowTask(taskName="Data type check")
    def acceptableDataType(self, apackageDir, emldata):
        if not os.path.isdir(apackageDir):
            self.logger.logMessage(WARN,"Parameter not a directory.")
            return (None, GeoNISDataType.NA)
        hint = emldata["type(eml)"]
        contents = [os.path.join(apackageDir,item) for item in os.listdir(apackageDir)]
        if len(contents) == 0:
            self.logger.logMessage(WARN,"Directory empty.")
            return (None, GeoNISDataType.NA)
        spatialTypeItem = emldata["spatialType"]
        if spatialTypeItem == "spatialVector":
            emlNode = GeoNISDataType.SPATIALVECTOR
        elif spatialTypeItem == "spatialRaster":
            emlNode = GeoNISDataType.SPATIALRASTER
        #array of tuples, one of which we will return
        allPotentialFiles = []
        #special handling - if we have interchange file, E00, then import it, reset the hint, and continue
        interchangeF = [f for f in contents if isEsriE00(f)]
        if len(interchangeF):
            #reset the hint
            if hint == GeoNISDataType.ESRIE00:
                hint = emlNode
            arcpy.env.workspace = apackageDir
            exchangeFile = interchangeF[0]
            fileName, ext = os.path.splitext(os.path.basename(exchangeFile))
            arcpy.ImportFromE00_conversion(exchangeFile, apackageDir, fileName)
            #for now, lets not delete. takes a while to download  os.remove(exchangeFile)
            #redo our contents list
            contents = [os.path.join(apackageDir,item) for item in os.listdir(apackageDir)]
        #gather up all files and folders that fit some description of spatial data
        for afile in (f for f in contents if os.path.isfile(f)):
            if isShapefile(afile):
                allPotentialFiles.append((afile,GeoNISDataType.SHAPEFILE))
            elif isKML(afile):
                allPotentialFiles.append((afile,GeoNISDataType.KML))
            elif isTif(afile):
                allPotentialFiles.append((afile,GeoNISDataType.TIF))
            elif isTifWorld(afile):
                allPotentialFiles.append((afile,GeoNISDataType.TFW))
            elif isJpeg(afile):
                allPotentialFiles.append((afile,GeoNISDataType.JPEG))
            elif isJpegWorld(afile):
                allPotentialFiles.append((afile,GeoNISDataType.JPGW))
            elif isASCIIRaster(afile):
                allPotentialFiles.append((afile, GeoNISDataType.ASCIIRASTER))
            elif isProjection(afile):
                allPotentialFiles.append((afile, GeoNISDataType.PRJ))
        for afolder in (f for f in contents if os.path.isdir(f)):
            if isFileGDB(afolder):
                allPotentialFiles.append((afolder, GeoNISDataType.FILEGEODB))
            if isRasterDS(afolder):
                allPotentialFiles.append((afolder, GeoNISDataType.SPATIALRASTER))
        if len(allPotentialFiles) > 0:
            #in most cases we probably just had one hit
            if len(allPotentialFiles) == 1:
                if allPotentialFiles[0][1] == GeoNISDataType.PRJ:
                    self.logger.logMessage(WARN, "Only a projection file, %s, was found." % (allPotentialFiles[0][0],))
                    return (None, GeoNISDataType.NA)
                if hint is not None and hint not in allPotentialFiles[0]:
                    self.logger.logMessage(WARN, "Expected data type %s is not exactly found data type %s for %s" % (hint, allPotentialFiles[0][1], allPotentialFiles[0][0]))
                return allPotentialFiles[0]
            #found more than one candidate
            #figure out what we really have by certainty
            #if we have a hint, use it
            for found in allPotentialFiles:
                if hint is not None and hint in found:
                    self.logger.logMessage(INFO, "Found hint %s matches %s, %s." % (hint, found[0], found[1]))
                    return found
            #we have more than one possibility, and it didn't match the hint
            #list of all types found for easy checking
            allTypesFound = [item[1] for item in allPotentialFiles]
            #seperate checking based on node in EML file, since that is the best indication we have
            if emlNode == GeoNISDataType.SPATIALRASTER:
                #files with world files or projections are good bets
                if (GeoNISDataType.TFW in allTypesFound or GeoNISDataType.PRJ in allTypesFound) and GeoNISDataType.TIF in allTypesFound:
                    fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.TIF).next()
                elif (GeoNISDataType.JPGW in allTypesFound or GeoNISDataType.PRJ in allTypesFound) and GeoNISDataType.JPEG in allTypesFound:
                    fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.JPEG).next()
                elif GeoNISDataType.FILEGEODB in allTypesFound:
                    fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.FILEGEODB).next()
                elif GeoNISDataType.ASCIIRASTER in allTypesFound:
                    fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.ASCIIRASTER).next()
                elif GeoNISDataType.TIF in allTypesFound:
                    # Tif without world file or prj file?
                    fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.TIF).next()
                    self.logger.logMessage(WARN, "%s seems to be tif with no prj or tfw." % (fileHit,))
                else:
                    fileHit, itsType = (None, GeoNISDataType.NA)
            elif emlNode == GeoNISDataType.SPATIALVECTOR:
            #files with world files or projections are good bets
                if GeoNISDataType.FILEGEODB in allTypesFound:
                    fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.FILEGEODB).next()
                elif GeoNISDataType.SHAPEFILE in allTypesFound:
                    fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.SHAPEFILE).next()
                elif GeoNISDataType.KML in allTypesFound:
                    fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.KML).next()
                else:
                    fileHit, itsType = (None, GeoNISDataType.NA)
            else:
                return (None, GeoNISDataType.NA)
            return (fileHit, itsType)
        else:
            return (None, GeoNISDataType.NA)

    @errHandledWorkflowTask(taskName="Data name check")
    def entityNameMatch(self, entityName, dataFilePath):
        dataFileName = os.path.basename(dataFilePath).lower()
        if entityName.lower() == dataFileName:
            return True
        else:
            name, ext = os.path.splitext(dataFileName)
            if entityName.lower() == name:
                return True
            else:
                self.logger.logMessage(WARN, "entityName %s did not match data name %s" % (entityName, dataFileName))
                return False


    @errHandledWorkflowTask(taskName="Format report")
    def getReport(self, reportText):
        """eventually when we know the report format, this could be an XSLT from emlSubset+workingData
        to the formatted report, perhaps json, xml, or html """
        return ""

    def execute(self, parameters, messages):
        super(CheckSpatialData, self).execute(parameters, messages)
        try:
            assert self.inputDirs != None
            assert self.outputDirs != None
            reportText = []
            for dataDir in self.inputDirs:
                self.logger.logMessage(INFO, "working in: " + dataDir)
                try:
                    status = "Entering data checks."
                    emldata = readWorkingData(dataDir, self.logger)
                    pkgId = emldata["packageId"]
                    shortPkgId = pkgId[9:]
                    reportfilePath = os.path.join(dataDir, shortPkgId + "_geonis_report.txt")
                    entityName = emldata["entityName"]
                    hint = self.examineEMLforType(emldata)
                    emldata["type(eml)"] = hint
                    foundFile, spatialType = self.acceptableDataType(dataDir, emldata)
                    if spatialType == GeoNISDataType.NA:
                        emldata["type"] = "NOT FOUND"
                        status = "Data type not found with tentative type %s" % hint
                        raise Exception("No compatible data found in %s" % dataDir)
                    emldata["datafilePath"] = foundFile
                    status = "Found acceptable data file."
                    nameMatch = self.entityNameMatch(entityName, foundFile)
                    emldata["datafileMatchesEntity"] = nameMatch
                    if spatialType == GeoNISDataType.KML:
                        self.logger.logMessage(INFO, "kml  found")
                        emldata["type"] = "kml"
                    if spatialType == GeoNISDataType.SHAPEFILE:
                        self.logger.logMessage(INFO, "shapefile found")
                        emldata["type"] = "shapefile"
                    if spatialType == GeoNISDataType.ASCIIRASTER:
                        self.logger.logMessage(INFO, "ascii raster found")
                        emldata["type"] = "ascii raster"
                    if spatialType == GeoNISDataType.FILEGEODB:
                        self.logger.logMessage(INFO, "file gdb found")
                        emldata["type"] = "file geodatabase"
                        #need to examine file gdb to see what is there, or rely on EML?
                    if spatialType == GeoNISDataType.ESRIE00:
                        self.logger.logMessage(WARN, "arcinfo e00  reported. Should have been unpacked.")
                    if spatialType == GeoNISDataType.TIF:
                        emldata["type"] = "tif"
                    if spatialType == GeoNISDataType.JPEG:
                        emldata["type"] = "jpg"
                    if spatialType == GeoNISDataType.SPATIALRASTER:
                        emldata["type"] = "raster dataset"
                    if spatialType == GeoNISDataType.SPATIALVECTOR:
                        emldata["type"] = "vector"
                except Exception as err:
                    status = "Failed after %s with %s" % (status, err.message)
                    self.logger.logMessage(WARN, e.message)
                    reportText.append({"Status":"Failed"})
                    reportText.append({"Error message":e.message})
                else:
                    status = "Passed checks"
                    reportText.append({"Status":"OK"})
                    self.outputDirs.append(dataDir)
                finally:
                    #write status msg to workflow.entity. Need both packagid and entityname to be unique
                    if pkgId and entityName:
                        stmt = "UPDATE workflow.entity set status = %s WHERE packageid = %s and entityname = %s;"
                        with cursorContext(self.logger) as cur:
                            cur.execute(stmt, (status[:499], pkgId, entityName))
                    writeWorkingDataToXML(dataDir, emldata, self.logger)
                    formattedReport = self.getReport(reportText)
            arcpy.SetParameterAsText(3, ";".join(self.outputDirs))
            arcpy.SetParameterAsText(4,str(reportText))
        except AssertionError:
            self.logger.logMessage(CRITICAL, "expected parameter not found")
            sys.exit(1)
        except Exception as crit:
            self.logger.logMessage(CRITICAL, crit.message)
            sys.exit(1)

## *****************************************************************************
class LoadVectorTypes(ArcpyTool):
    """Loads to geodatabase any vector types, then exports, amends, and imports metadata."""
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = "Loads to geodatabase any vector data types, then exports, amends, and imports metadata."
        self._label = "S4. Load Vector"
        self._alias = "loadvector"

    def getParameterInfo(self):
        params = super(LoadVectorTypes, self).getParameterInfo()
        params.append(self.getMultiDirInputParameter())
        params.append(self.getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        """called whenever user edits parameter in tool GUI. Can adjust other parameters here. """
        super(LoadVectorTypes, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        """called after all of the update parameter calls. Call attach messages to parameters, usually warnings."""
        super(LoadVectorTypes, self).updateMessages(parameters)

    @errHandledWorkflowTask(taskName="Load shapefile")
    def loadShapefile(self, scope, name, path):
        """call feature class to feature class to copy shapefile to geodatabase"""
        self.logger.logMessage(INFO,"Loading %s to %s/%s as %s\n" % (path, geodatabase, scope, name))
        #if no dataset, make one
        if not arcpy.Exists(os.path.join(geodatabase,scope)):
            arcpy.CreateFeatureDataset_management(out_dataset_path = geodatabase,
                                                out_name = scope,
                                                spatial_reference = self.spatialRef)
        arcpy.FeatureClassToFeatureClass_conversion(in_features = path,
                                    out_path = os.path.join(geodatabase,scope),
                                    out_name = name)
        return geodatabase + os.sep + scope + os.sep + name


    @errHandledWorkflowTask(taskName="Load KML")
    def loadKml(self, scope, name, path):
        """call KML to Layer tool to copy kml contents to file gdb, then loop over features
        and load each to geodatabase"""
        self.logger.logMessage(INFO,"Loading %s to %s/%s as %s\n" % (path, geodatabase, scope, name))
        #if no dataset, make one
        if not arcpy.Exists(os.path.join(geodatabase,scope)):
            arcpy.CreateFeatureDataset_management(out_dataset_path = geodatabase,
                                                out_name = scope,
                                                spatial_reference = self.spatialRef)
        arcpy.KMLToLayer_conversion( in_kml_file = path,
                                    output_folder = os.path.dirname(path),
                                    output_data = name)
        # load resulting feature classes out of fgdb just created
        fgdb = os.path.join(os.path.dirname(path), name + '.gdb')
        arcpy.env.workspace = fgdb
        fclasses = arcpy.ListFeatureClasses(wild_card = '*', feature_type = '', feature_dataset = "Placemarks")
        if fclasses:
            feature = fclasses[0]
            fcpath = fgdb + os.sep + "Placemarks" + os.sep + feature
            outDS = os.path.join(geodatabase, scope)
            outF = name + '_' + feature
            arcpy.FeatureClassToFeatureClass_conversion(in_features = fcpath,
                                                        out_path = outDS,
                                                        out_name = outF)
            return outDS + os.sep + outF
        return None


    @errHandledWorkflowTask(taskName="Merge metadata")
    def mergeMetadata(self, workDir, loadedFeatureClass):
        if not loadedFeatureClass:
            return
        createSuppXML(workDir)
        xmlSuppFile = workDir + os.sep + "emlSupp.xml"
        if not os.path.isfile(xmlSuppFile):
            self.logger.logMessage(WARN, "Supplemental metadata file missing in %s" % (workDir,))
            return
        arcpy.env.workspace = workDir
        result = arcpy.XSLTransform_conversion(loadedFeatureClass, pathToStylesheets + os.sep + "metadataMerge.xsl", "merged_metadata.xml", xmlSuppFile)
        result2 = arcpy.MetadataImporter_conversion("merged_metadata.xml", loadedFeatureClass)


    @errHandledWorkflowTask(taskName="Update entity table")
    def updateTable(self, workDir, loadedFeatureClass, pkid, entityname):
        if not loadedFeatureClass:
            return
        scope_data = os.sep.join(loadedFeatureClass.split(os.sep)[-2:])
        stmt = "UPDATE workflow.entity set storage = %s WHERE packageid = %s and entityname = %s;"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt, (scope_data, pkid, entityname))


    def execute(self, parameters, messages):
        super(LoadVectorTypes, self).execute(parameters, messages)
        for dir in self.inputDirs:
            datafilePath, pkgId, datatype, entityname, shortentityname = ("" for i in range(5))
            try:
                status = "Entering load vector"
                emldata = readWorkingData(dir, self.logger)
                pkgId = emldata["packageId"]
                datafilePath = emldata["datafilePath"]
                datatype = emldata["type"]
                entityname = emldata["entityName"]
                shortentityname = emldata["shortEntityName"]
                siteId, n, m = siteFromId(pkgId)
                #TODO Do we need a way to specify this suffix?
                scopeWithSuffix = siteId + "_main"
                if 'shapefile' in datatype:
                    loadedFeatureClass = self.loadShapefile(scopeWithSuffix, shortentityname, datafilePath)
                    status = "Loaded shapefile"
                elif 'kml' in datatype:
                    loadedFeatureClass = self.loadKml(scopeWithSuffix, shortentityname, datafilePath)
                    status = "Loaded from KML"
                elif 'geodatabase' in datatype:
                    #TODO: copy vector from file geodatabase, for now, leave dir behind
                    status = "Loaded from file geodatabase"
                    continue
                else:
                    # no vector data here; continue to next dir, placing this one into the output set
                    self.outputDirs.append(dir)
                    continue
                # amend metadata
                self.mergeMetadata(dir, loadedFeatureClass)
                # update table in geonis db
                self.updateTable(dir, loadedFeatureClass, pkgId, entityname)
                # add dir for next tool, in any case except exception
                self.outputDirs.append(dir)
                status = "Load with metadata complete"
            except Exception as err:
                status = "Failed after %s with %s" % (status, err.message)
                self.logger.logMessage(WARN, "Exception loading %s. %s\n" % (datafilePath, err.message))
            finally:
                #write status msg to db table
                if pkgId and entityname:
                    stmt = "UPDATE workflow.entity set status = %s WHERE packageid = %s and entityname = %s;"
                    with cursorContext(self.logger) as cur:
                        cur.execute(stmt, (status[:499], pkgId, entityname))
        #pass the list on
        arcpy.SetParameterAsText(3, ";".join(self.outputDirs))

## *****************************************************************************
class LoadRasterTypes(ArcpyTool):
    """Expects some type or raster dataset, with its path and type saved to notes.
       Calls addRasterToMosaicDataset for the mosaic dataset of the site."""
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = "For any raster data type, copies raster data entity, updates metadata, then loads to mosaic dataset of site."
        self._label = "S5. Load Raster"
        self._alias = "loadraster"

    def getParameterInfo(self):
        params = super(LoadRasterTypes, self).getParameterInfo()
        params.append(self.getMultiDirInputParameter())
        params.append(self.getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        """called whenever user edits parameter in tool GUI. Can adjust other parameters here. """
        super(LoadRasterTypes, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        """called after all of the update parameter calls. Call attach messages to parameters, usually warnings."""
        super(LoadRasterTypes, self).updateMessages(parameters)


    @errHandledWorkflowTask(taskName="Check if raster we support")
    def isSupported(self, datatype):
        """ mostly to distinguish the vector folders that are passing through """
        dtype = datatype.lower()
        for t in self.supportedTypes:
            if t in dtype:
                return True
        return False


    @errHandledWorkflowTask(taskName="Prepare storage")
    def prepareStorage(self, site, datapath, name, dsSuffix = "main"):
        """ Create the directories necessary for storing the raw data, and return path to location.
            Also create mosaic dataset for site if needed.
            Currently appending '_main' to scope for storage dir and mosaic dataset name (db terms
            not allowed as ds name--I'm looking at you, and)
        """
        dsName = site + '_' + dsSuffix
        siteStore = os.path.join(pathToRasterData,dsName)
        #name, ext =  os.path.splitext( os.path.basename(datapath))
        storageLoc = siteStore + os.sep + name
        #if no site folder, make one
        if not os.path.exists(siteStore):
            os.mkdir(siteStore)
        #if no mosaic dataset, make it
        siteMosDS = pathToRasterMosaicDatasets + os.sep + dsName
        if not arcpy.Exists(siteMosDS):
            result = arcpy.Copy_management(pathToRasterMosaicDatasets + os.sep + "Template", siteMosDS)
        else:
            #if raster exists, delete it?
            pass
        i = 1
        while os.path.isdir(storageLoc):
            storageLoc = "%s_%s" % (storageLoc, i)
            i += 1
        return storageLoc, siteMosDS


    @errHandledWorkflowTask(taskName="Copy raster")
    def copyRaster(self, path, storageLoc):
        """Copy raster data to permanent home. Path must lead to raster dataset of some type."""
        self.logger.logMessage(INFO,"Copying %s to %s" % (path, storageLoc))
        data = storageLoc + os.sep + os.path.basename(path)
        #name, ext = os.path.splitext(os.path.basename(path))
        result = arcpy.Copy_management(path, data)
        if result.status != 4:
            raise Exception(WARN, "Copying %s to %s did not succeed. Status: %d\n" % (path, storageLoc, result.status))
        return data

    @errHandledWorkflowTask(taskName="Load raster")
    def loadRaster(self, siteMosDS, path, pId):
        """Load raster to mosaic dataset. Path must lead to raster dataset in permanent home."""
        self.logger.logMessage(INFO,"Loading raster %s to %s" % (path, siteMosDS))
        rastype = "Raster Dataset"
        updatecs = "UPDATE_CELL_SIZES"
        updatebnd = "UPDATE_BOUNDARY"
        updateovr = "UPDATE_OVERVIEWS"
        maxlevel = "2"
        maxcs = "#"
        maxdim = "#"
        spatialref = "#"
        inputdatafilter = "#"
        subfolder = "NO_SUBFOLDERS"
        duplicate = "OVERWRITE_DUPLICATES"
        buildpy = "BUILD_PYRAMIDS"
        calcstats = "CALCULATE_STATISTICS"
        buildthumb = "NO_THUMBNAILS"
        comments = pId
        forcesr = "#"
        result = arcpy.AddRastersToMosaicDataset_management(
                                            siteMosDS, rastype, path, updatecs,
                                            updatebnd, updateovr, maxlevel, maxcs,
                                            maxdim, spatialref, inputdatafilter,
                                            subfolder, duplicate, buildpy, calcstats,
                                            buildthumb, comments, forcesr)
        return result.status


    @errHandledWorkflowTask(taskName="Merge metadata")
    def mergeMetadata(self, workDir, raster):
        if not arcpy.Exists(raster):
            return False
        createSuppXML(workDir)
        xmlSuppFile = workDir + os.sep + "emlSupp.xml"
        if not os.path.isfile(xmlSuppFile):
            self.logger.logMessage(WARN, "Supplemental metadata file missing in %s" % (workDir,))
            return False
        arcpy.env.workspace = workDir
        result = arcpy.XSLTransform_conversion(raster, pathToStylesheets + os.sep + "metadataMerge.xsl", "merged_metadata.xml", xmlSuppFile)
        if result.status == 4:
            result2 = arcpy.MetadataImporter_conversion("merged_metadata.xml", raster)
        else:
            self.logger.logMessage(WARN, "XSLT failed with status %d" % (result.status,))
            return False
        if result2.status != 4:
            self.logger.logMessage(WARN, "Reloading of metadata failed with code %d" % (result2.status,))
            return False
        return True


    @errHandledWorkflowTask(taskName="Update entity table")
    def updateTable(self, location, pkid, entityname):
        # get last three parts of location:  scope, entity dir, entity name
        parts = location.split(os.sep)
        if len(parts) > 3:
            loc = os.sep.join(parts[-3:])
        else:
            loc = location[-50:]
        stmt = "UPDATE workflow.entity set storage = %s WHERE packageid = %s and entityname = %s;"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt, (loc, pkid, entityname))


    def execute(self, parameters, messages):
        super(LoadRasterTypes, self).execute(parameters, messages)
        #TODO: add file gdb to list, and handle. Could be mosaic ds in file gdb, e.g.
        self.supportedTypes = ("tif", "ascii raster", "coverage", "jpg", "raster dataset")
        for dir in self.inputDirs:
            datafilePath, pkgId, datatype, entityname = ("" for i in range(4))
            loadedRaster = None
            try:
                status = "Entering raster load"
                emldata = readWorkingData(dir, self.logger)
                pkgId = emldata["packageId"]
                datafilePath = emldata["datafilePath"]
                datatype = emldata["type"]
                entityname = emldata["entityName"]
                shortentityname = emldata["shortEntityName"]
                #check for supported type
                if not self.isSupported(datatype):
                    self.outputDirs.append(dir)
                    continue
                siteId, n, m = siteFromId(pkgId)
                rawDataLoc, mosaicDS = self.prepareStorage(siteId, datafilePath, shortentityname)
                status = "Storage prepared"
                os.mkdir(rawDataLoc)
                raster = self.copyRaster(datafilePath, rawDataLoc)
                self.updateTable(raster, pkgId, entityname)
                status = "Raster copied to permanent storage"
                # amend metadata in place
                if self.mergeMetadata(dir, raster):
                    status = "Metadata updated"
                    result = self.loadRaster(mosaicDS, raster, pkgId)
                    if result != 4:
                        status = "Load raster to mosaic failed"
                        self.logger.logMessage(WARN, "Loading %s did not succeed, with code %d.\n" % (raster, result))
                    else:
                        # add dir for next tool, in any case except exception
                        status = "Load raster completed"
                        self.outputDirs.append(dir)
                else:
                    self.logger.logMessage(WARN, "Metadata function returned False.\n")
            except Exception as err:
                status = "Failed after %s with %s" % (status, err.message)
                self.logger.logMessage(WARN, "Exception loading %s. %s\n" % (datafilePath, err.message))
            finally:
                #write status msg to db table
                if pkgId:
                    stmt = "UPDATE workflow.entity set status = %s WHERE packageid = %s;"
                    with cursorContext(self.logger) as cur:
                        cur.execute(stmt, (status[:499], pkgId))
        #pass the list on
        arcpy.SetParameterAsText(3, ";".join(self.outputDirs))


## *****************************************************************************
class UpdateMXDs(ArcpyTool):
    """Adds new vector data to map files"""
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = "Adds new vector data to map files by scope."
        self._label = "S6. Update MXD"
        self._alias = "updateMXD"

    def getParameterInfo(self):
        params = super(UpdateMXDs, self).getParameterInfo()
        params.append(self.getMultiDirInputParameter())
        params.append(self.getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        """called whenever user edits parameter in tool GUI. Can adjust other parameters here. """
        super(UpdateMXDs, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        """called after all of the update parameter calls. Call attach messages to parameters, usually warnings."""
        super(UpdateMXDs, self).updateMessages(parameters)

    @errHandledWorkflowTask(taskName="Add vector data to MXD")
    def addVectorData(self, workDir, workingData):
        """   """
        # see if entry in entity table, and get storage path
        stmt = "SELECT storage, status FROM workflow.entity WHERE packageid = %s and entityname = %s;"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt, (workingData["packageId"], workingData["entityName"]))
            rows = cur.fetchall()
            if rows:
                store, status = rows[0]
            else:
                raise Exception("Record not in entity table")
        # TODO: this is not robust, can pick up status from tool that skips it
        #if "complete" not in status:
        #    self.logger.logMessage(WARN, "Status of layer being added to mxd: %s" % (status,))
        scope = siteFromId(workingData["packageId"])[0]
        # make layer name
        layerName = stringToValidName(workingData["entityName"], spacesToUnderscore = True, max = 24)
        mxdName = scope + ".mxd"
        mxdfile = pathToMapDoc + os.sep + mxdName
        # check if layer is in mxd, and remove if found
        mxd = arcpy.mapping.MapDocument(mxdfile)
        layersFrame = arcpy.mapping.ListDataFrames(mxd, "layers")[0]
        for layer in arcpy.mapping.ListLayers(mxd, "", layersFrame):
            itsName = layer.name
            while itsName.startswith("geonis."):
                itsName = itsName[7:]
            if itsName == layerName:
                arcpy.mapping.RemoveLayer(layersFrame, layer)
                mxd.save()
        #now add to map
        feature = geodatabase + os.sep + store
        scratchFld = arcpy.env.scratchFolder
        arcpy.MakeFeatureLayer_management(in_features = feature, out_layer = layerName)
        lyrFile = scratchFld + os.sep + layerName + ".lyr"
        arcpy.SaveToLayerFile_management(layerName, lyrFile)
        arcpy.mapping.AddLayer(layersFrame, arcpy.mapping.Layer(lyrFile))
        mxd.save()
        workingData["layerName"] = layerName
        writeWorkingDataToXML(workDir, workingData)
        os.remove(lyrFile)
        del layersFrame, mxd
        return (layerName, mxdName)


    def execute(self, parameters, messages):
        super(UpdateMXDs, self).execute(parameters, messages)
        for dir in self.inputDirs:
            try:
                status = "Entering add vector to MXD"
                workingData = readWorkingData(dir, self.logger)
                if workingData["spatialType"] == "spatialVector":
                    pkgId = workingData["packageId"]
                    lName, mxdName = self.addVectorData(dir, workingData)
                    status = "Added to Map"
                    with cursorContext(self.logger) as cur:
                        stmt = """UPDATE workflow.entity set mxd = %(mxd)s, layername = %(layername)s, completed = %(now)s
                         WHERE packageid = %(pkgId)s and entityname = %(entityname)s;
                         """
                        cur.execute(stmt,
                         {'mxd': mxdName, 'layername' : lName, 'now' : datetime.datetime.now(), 'pkgId': pkgId, 'entityname' : workingData["entityName"]})
                    status = "OK"
                else:
                    status = "Carried forward to next tool"
                self.outputDirs.append(dir)
            except Exception as err:
                status = "Failed after %s with %s" % (status, err.message)
                self.logger.logMessage(WARN, err.message)
            finally:
                #write status msg to db table
                if workingData:
                    stmt = "UPDATE workflow.entity set status = %s WHERE packageid = %s  and entityname = %s;"
                    with cursorContext(self.logger) as cur:
                        cur.execute(stmt, (status[:499], workingData["packageId"], workingData["entityName"]))
        #pass the list on
        arcpy.SetParameterAsText(3, ";".join(self.outputDirs))


## *****************************************************************************
##class RefreshMapService(ArcpyTool):
##    """Adds new vector data to map, creates service def draft, modifies it to replace, uploads and starts service,
##       waits for service to start, gets list of layers, updates table with layer IDs. """
##    def __init__(self):
##        ArcpyTool.__init__(self)
##        self._description = "Adds new vector data to map, creates service def draft, modifies it to replace, uploads and starts service, waits for service to start, gets list of layers, updates table with layer IDs."
##        self._label = "Refresh Map Service"
##        self._alias = "refreshMapServ"
##
##    def getParameterInfo(self):
##        return super(RefreshMapService, self).getParameterInfo()
##
##    def updateParameters(self, parameters):
##        """called whenever user edits parameter in tool GUI. Can adjust other parameters here. """
##        super(RefreshMapService, self).updateParameters(parameters)
##
##    def updateMessages(self, parameters):
##        """called after all of the update parameter calls. Call attach messages to parameters, usually warnings."""
##        super(RefreshMapService, self).updateMessages(parameters)
##
##
##    @errHandledWorkflowTask(taskName="Create service draft")
##    def draftSD(self):
##        """Stops service, creates SD draft, modifies it"""
##        """http://maps3.lternet.edu:6080/arcgis/admin/services/Test/VectorData.MapServer/stop"""
##        arcpy.env.workspace = os.path.dirname(pathToMapDoc)
##        wksp = arcpy.env.workspace
##        #stop service first
##        with open(r"C:\pasta2geonis\arcgis_cred.txt") as f:
##            cred = eval(f.readline())
##        token = getToken(cred['username'], cred['password'])
##        if token:
##            serviceStopURL = "/arcgis/admin/services/Test/VectorData.MapServer/stop"
##            # This request only needs the token and the response formatting parameter
##            params = urllib.urlencode({'token': token, 'f': 'json'})
##            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
##            # Connect to URL and post parameters
##            httpConn = httplib.HTTPConnection("localhost", "6080")
##            httpConn.request("POST", serviceStopURL, params, headers)
##            response = httpConn.getresponse()
##            if (response.status != 200):
##                self.logger.logMessage(WARN, "Error while attempting to stop service.")
##            httpConn.close()
##        else:
##             self.logger.logMessage(WARN, "Error while attempting to get admin token.")
##        mxd = arcpy.mapping.MapDocument(pathToMapDoc)
##        sdDraft = wksp + os.sep + mapServInfo['service_name'] + ".sddraft"
##        arcpy.mapping.CreateMapSDDraft(mxd, sdDraft, mapServInfo['service_name'],
##        "ARCGIS_SERVER", pubConnection, False, "Test", mapServInfo['summary'], mapServInfo['tags'])
##        del mxd
##        #now we need to change one tag in the draft to indicate this is a replacement service
##        draftXml = etree.parse(sdDraft)
##        typeNode = draftXml.xpath("/SVCManifest/Type")
##        if typeNode and etree.iselement(typeNode[0]):
##            typeNode[0].text = "esriServiceDefinitionType_Replacement"
##            with open(sdDraft,'w') as outfile:
##                outfile.write(etree.tostring(draftXml, xml_declaration = False))
##            #save backup for debug
##            with open(sdDraft + '.bak', 'w') as bakfile:
##                bakfile.write(etree.tostring(draftXml, xml_declaration = False))
##        del typeNode, draftXml
##
##    @errHandledWorkflowTask(taskName="Replace service")
##    def replaceService(self):
##        """Creates SD, uploads to server"""
##        arcpy.env.workspace = os.path.dirname(pathToMapDoc)
##        wksp = arcpy.env.workspace
##        mxd = arcpy.mapping.MapDocument(pathToMapDoc)
##        sdDraft = wksp + os.sep + mapServInfo['service_name'] + ".sddraft"
##        sdFile =  wksp + os.sep + mapServInfo['service_name'] + ".sd"
##        if os.path.exists(sdFile):
##            os.remove(sdFile)
##        #by default, writes SD file to same loc as draft, then DELETES DRAFT
##        arcpy.StageService_server(sdDraft)
##        if os.path.exists(sdFile):
##            arcpy.UploadServiceDefinition_server(in_sd_file = sdFile, in_server = pubConnection, in_startupType = 'STARTED')
##        else:
##            raise Exception("Staging failed to create %s" % (sdFile,))
##
##
##    @errHandledWorkflowTask(taskName="Update search table")
##    def updateLayerIds(self, dbconn, addedLayerNames):
##        """Updates layer ids in search table with service info query"""
##            #get list of layer names from service
##        available = False
##        tries = 0
##        layerInfoJson = urllib2.urlopen(layerQueryURI)
##        layerInfo = json.loads(layerInfoJson.readline())
##        del layerInfoJson
##        available = "error" not in layerInfo
##        while not available and tries < 10:
##            time.sleep(5)
##            tries += 1
##            layerInfoJson = urllib2.urlopen(layerQueryURI)
##            layerInfo = json.loads(layerInfoJson.readline())
##            available = "error" not in layerInfo
##        self.logger.logMessage(DEBUG, "service conn attemps %d" % (tries,))
##        # make list of dict with just name and id of feature layers
##        layers = [{'name':lyr["name"],'id':lyr['id']} for lyr in layerInfo["layers"] if lyr["type"] == "Feature Layer"]
##        # shorten names that have db and schema in the name
##        for lyr in layers:
##            while lyr['name'].startswith("geonis."):
##                lyr['name'] = lyr['name'][7:]
##        # update table with ids of layers
##        # To completely refresh table, set all ids to null before using tool
##        curs = dbconn.cursor()
##        stmt = "SELECT id, layername FROM geonis.processed_items t1 WHERE t1.featureclass AND t1.serviceid is null;"
##        curs.execute(stmt)
##        rows = curs.fetchall()
##        dbconn.commit()
##        updateParams = []
##        if rows:
##            for row in rows:
##                rowid, layername = row
##                search = [lyr['id'] for lyr in layers if lyr['name'] == layername]
##                if search:
##                    updateParams.append((int(search[0]), int(rowid)))
##        del rows
##        # updateParams now has 0 or more tuples (layer id, db id)
##        stmt2 = "UPDATE geonis.processed_items SET serviceid = %s WHERE id = %s;"
##        for params in updateParams:
##            curs.execute(stmt2, params)
##        dbconn.commit()
##        del curs
##
##
##    def execute(self, parameters, messages):
##        super(RefreshMapService, self).execute(parameters, messages)
##        #bypass
##        conn = None
##        try:
##            with open(dsnfile) as dsnf:
##                dsnStr = dsnf.readline()
##            conn = psycopg2.connect(dsn = dsnStr)
##        except Exception as connerr:
##            self.logger.logMessage(ERROR, connerr.message)
##            exit(1)
##        try:
##            addedLayers = self.addVectorData(conn)
##            if addedLayers:
##                self.logger.logMessage(INFO, "The following added to map: %s" % (str(addedLayers),))
##                self.draftSD()
##                self.replaceService()
##                #delay for service to start, get layer info
##                time.sleep(20)
##                self.updateLayerIds(conn, addedLayers)
##            else:
##                self.logger.logMessage(INFO, "No new vector data added to map.")
##        except Exception as err:
##            conn.rollback()
##            self.logger.logMessage(ERROR, err.message)
##        finally:
##            conn.close()
##
##

## *****************************************************************************
class Tool(ArcpyTool):
    """template for GEONIS tool"""
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = "Description"
        self._label = "Name in toolbox"
        self._alias = "Name in scripts"

    def getParameterInfo(self):
        params = super(Tool, self).getParameterInfo()
        params.append(self.getMultiDirInputParameter())
        params.append(self.getMultiDirOutputParameter())
        return params

    def updateParameters(self, parameters):
        """called whenever user edits parameter in tool GUI. Can adjust other parameters here. """
        super(Tool, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        """called after all of the update parameter calls. Call attach messages to parameters, usually warnings."""
        super(Tool, self).updateMessages(parameters)

    @errHandledWorkflowTask(taskName="Task 1")
    def someTask(self, path):
        """perfom some task of this tool. decorator will wrap in error handling code and log task entry and errors"""
        pass

    def execute(self, parameters, messages):
        """called when user clicks run, or when invoked as script, after parameters adjusted by arcpy
        superclass will instantiate or get logger, inputDirs, and outputDirs instance variables
        """
        super(Tool, self).execute(parameters, messages)
        for dir in self.inputDirs:
            try:
                someTask(dir)
                self.outputDirs.append(dir)
            except Exception as err:
                self.logger.logMessage(WARN, err.message)
        #pass the list on
        arcpy.SetParameterAsText(3, ";".join(self.outputDirs))


#this list is imported into Toolbox.pyt file and used to instantiate tools
toolclasses =  [UnpackPackages,
                CheckSpatialData,
                LoadVectorTypes,
                LoadRasterTypes,
                UpdateMXDs ]

