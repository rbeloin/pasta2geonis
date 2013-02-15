'''

Created on Jan 14, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import sys, os, re
import time
import urllib2
from shutil import copyfileobj
from zipfile import ZipFile
import arcpy
from geonis_log import EvtLog, errHandledWorkflowTask
from arcpy import AddMessage as arcAddMsg, AddError as arcAddErr, AddWarning as arcAddWarn
from arcpy import Parameter
from logging import DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL
from lno_geonis_base import ArcpyTool
from geonis_pyconfig import GeoNISDataType, tempMetadataFilename, geodatabase, pathToMetadataMerge, pathToRasterData, pathToRasterMosaicDatasets
from geonis_helpers import isShapefile, isKML, isTif, isTifWorld, isASCIIRaster, isFileGDB, isJpeg, isJpegWorld, isEsriE00, isRasterDS, isProjection
from geonis_helpers import siteFromId
from geonis_emlparse import parseAndPopulateEMLDicts, createSuppXML

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
        #TODO: rename eml file so as to avoid confusion with other xml files that may be unpacked
        emlfile = os.path.join(workDir, xmlfiles[0])
        emldata = parseAndPopulateEMLDicts(emlfile, self.logger)
        with open(emldatafile,'w') as datafile:
            datafile.write(repr(emldata))


    @errHandledWorkflowTask(taskName="Retrieve and unzip data")
    def retrieveData(self, workDir):
        emldata = self.getEMLdata(workDir)
        urlobj = [item for item in emldata if item["name"] == "url"]
        if not urlobj:
            raise Exception("URL item not found in eml data.")
        dataloc = urlobj[0]["content"]
        try:
            resourceName = dataloc[dataloc.rindex("/") + 1 :]
            sdatafile = os.path.join(workDir,resourceName)
            resource = urllib2.urlopen(dataloc)
            with open(sdatafile,'wb') as dest:
                copyfileobj(resource,dest)
        except Exception as e:
            raise Exception(e.message)
        finally:
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
                self.parseEML(workdir)
                self.retrieveData(workdir)
            except Exception as err:
                self.logger.logMessage(WARN, "The data in %s will not be processed. %s" % (pkg, err.message))
            else:
                carryForwardList.append(workdir)
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
    def examineEMLforType(self, emlData):
        spatialTypeItem = [item for item in emlData if item["name"] == "spatialType"][0]
        if spatialTypeItem["content"] == "vector":
            retval = GeoNISDataType.SPATIALVECTOR
        elif spatialTypeItem["content"] == "raster":
            retval = GeoNISDataType.SPATIALRASTER
        else:
            self.logger.logMessage(WARN,"EML spatial type not set, implying 'spatialVector' or 'spatialRaster' node not found.")
            raise Exception("EML spatialType node not found.")
        # now see if can find out more specifically
        entDescItem = [item for item in emlData if item["name"] == "entityDescription"][0]
        entDescStr = entDescItem["content"].lower()
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
    def acceptableDataType(self, apackageDir, hint = None):
        if not os.path.isdir(apackageDir):
            self.logger.logMessage(WARN,"Parameter not a directory.")
            return (None, GeoNISDataType.NA)
        contents = [os.path.join(apackageDir,item) for item in os.listdir(apackageDir)]
        #self.logger.logMessage(DEBUG, str(contents))
        #array of tuples, one of which we will return
        allPotentialFiles = []
        #special handling - if we have interchange file, E00, then import it, reset the hint, and continue
        interchangeF = [f for f in contents if isEsriE00(f)]
        if len(interchangeF):
            #reset the hint
            if hint == GeoNISDataType.ESRIE00:
                spatialTypeItem = [item for item in self.getEMLdata(apackageDir) if item["name"] == "spatialType"][0]
                if spatialTypeItem["content"] == "vector":
                    hint = GeoNISDataType.SPATIALVECTOR
                elif spatialTypeItem["content"] == "raster":
                    hint = GeoNISDataType.SPATIALRASTER
            arcpy.env.workspace = apackageDir
            exchangeFile = interchangeF[0]
            fileName, ext = os.path.splitext(os.path.basename(exchangeFile))
            arcpy.ImportFromE00_conversion(exchangeFile, apackageDir, fileName)
            #for now, lets not delete. takes a while to download  os.remove(exchangeFile)
            #redo our contents list
            contents = [os.path.join(apackageDir,item) for item in os.listdir(apackageDir)]
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
            #list of all types found for easy checking
            allTypesFound = [item[1] for item in allPotentialFiles]
            #files with world files or projections are good bets
            if (GeoNISDataType.TFW in allTypesFound or GeoNISDataType.PRJ in allTypesFound) and GeoNISDataType.TIF in allTypesFound:
                fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.TIF).next()
            elif (GeoNISDataType.JPGW in allTypesFound or GeoNISDataType.PRJ in allTypesFound) and GeoNISDataType.JPEG in allTypesFound:
                fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.JPEG).next()
            elif GeoNISDataType.FILEGEODB in allTypesFound:
                fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.FILEGEODB).next()
            elif GeoNISDataType.SHAPEFILE in allTypesFound:
                fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.SHAPEFILE).next()
            elif GeoNISDataType.KML in allTypesFound:
                fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.KML).next()
            elif GeoNISDataType.ASCIIRASTER in allTypesFound:
                fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.ASCIIRASTER).next()
            elif GeoNISDataType.TIF in allTypesFound:
                # Tif without world file or prj file?
                fileHit, itsType = (item for item in allPotentialFiles if item[1] == GeoNISDataType.TIF).next()
                self.logger.logMessage(WARN, "%s seems to be tif with no prj or tfw." % (fileHit,))
            else:
                fileHit, itsType = (None, GeoNISDataType.NA)
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
                self.logger.logMessage(INFO, "working in: " + dataDir)
                try:
                    emldata = self.getEMLdata(dataDir)
                    #simple lookup when we expect exactly one value
                    getEMLitem = lambda ky : [item["content"] for item in emldata if item["name"] == ky][0]
                    #get packageId from emldata
                    pkgId = getEMLitem("packageId")
                    shortPkgId = pkgId[9:]
                    notesfilePath = os.path.join(dataDir, "geonis_notes.txt")
                    reportfilePath = os.path.join(dataDir, shortPkgId + "_geonis_report.txt")
                    with open(notesfilePath,'w') as notesfile:
                        entityName = getEMLitem("entityName")
                        notesfile.write("PackageId:%s\n" % (pkgId,))
                        notesfile.write("EntityNameFound:%s\n" % (entityName,))
                        hint = self.examineEMLforType(emldata)
                        notesfile.write("TYPE(eml):%s\n" % (hint,))
                        foundFile, spatialType = self.acceptableDataType(dataDir, hint)
                        if spatialType == GeoNISDataType.NA:
                            notesfile.write("TYPE:NOT FOUND\n")
                            raise Exception("No compatible data found in %s" % dataDir)
                        notesfile.write("DatafilePath:%s\n" % (foundFile,))
                        nameMatch = self.entityNameMatch(entityName, foundFile)
                        notesfile.write("DatafileMatchesEntity:%s\n" % (nameMatch,))
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
                            #need to examine file gdb to see what is there, or rely on EML?
                        if spatialType == GeoNISDataType.ESRIE00:
                            self.logger.logMessage(INFO, "arcinfo e00  found")
                            notesfile.write('TYPE:ArcInfo Exchange (e00)\n')
                            #need to import this, and see what it is
                except Exception as e:
                    with open(notesfilePath,'w') as notesfile:
                        notesfile.write("Exception:%s\n", (e.message,))
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
    def loadShapefile(self, site, name, path):
        """call feature class to feature class to copy shapefile to geodatabase"""
        self.logger.logMessage(INFO,"Loading %s to %s/%s as %s\n" % (path, geodatabase, site, name))
        addedFC = []
        #if no dataset, make one
        if not arcpy.Exists(os.path.join(geodatabase,site)):
            arcpy.CreateFeatureDataset_management(out_dataset_path = geodatabase,
                                                out_name = site,
                                                spatial_reference = self.spatialRef)
        arcpy.FeatureClassToFeatureClass_conversion(in_features = path,
                                    out_path = os.path.join(geodatabase,site),
                                    out_name = name)
        addedFC.append(geodatabase + os.sep + site + os.sep + name)
        return addedFC


    @errHandledWorkflowTask(taskName="Load KML")
    def loadKml(self, site, name, path):
        """call KML to Layer tool to copy kml contents to file gdb, then loop over features
        and load each to geodatabase"""
        self.logger.logMessage(INFO,"Loading %s to %s/%s as %s\n" % (path, geodatabase, site, name))
        addedFC = []
        #if no dataset, make one
        if not arcpy.Exists(os.path.join(geodatabase,site)):
            arcpy.CreateFeatureDataset_management(out_dataset_path = geodatabase,
                                                out_name = site,
                                                spatial_reference = self.spatialRef)
        arcpy.KMLToLayer_conversion( in_kml_file = path,
                                    output_folder = os.path.dirname(path),
                                    output_data = name)
        # load resulting feature classes out of fgdb just created
        fgdb = os.path.join(os.path.dirname(path), name + '.gdb')
        arcpy.env.workspace = fgdb
        fclasses = arcpy.ListFeatureClasses(wild_card = '*', feature_type = '', feature_dataset = "Placemarks")
        for feature in fclasses:
            fcpath = fgdb + os.sep + "Placemarks" + os.sep + feature
            outDS = os.path.join(geodatabase, site)
            outF = name + '_' + feature
            arcpy.FeatureClassToFeatureClass_conversion(in_features = fcpath,
                                                        out_path = outDS,
                                                        out_name = outF)
            addedFC.append(outDS + os.sep + outF)
        return addedFC


    @errHandledWorkflowTask(taskName="Merge metadata")
    def mergeMetadata(self, workDir, loadedFeatureClasses):
        if not loadedFeatureClasses:
            return
        emldataObj = self.getEMLdata(workDir)
        xmlSuppFile = os.path.join(workDir, "supp_metadata.xml")
        createSuppXML(emldataObj, xmlSuppFile)
        if not os.path.isfile(xmlSuppFile):
            self.logger.logMessage(WARN, "Supplemental metadata file missing in %s" % (workDir,))
            return
        arcpy.env.workspace = workDir
        for fc in loadedFeatureClasses:
            result = arcpy.XSLTransform_conversion(fc, pathToMetadataMerge, "merged_metadata.xml", xmlSuppFile)
            result2 = arcpy.MetadataImporter_conversion("merged_metadata.xml", fc)



    def execute(self, parameters, messages):
        super(LoadVectorTypes, self).execute(parameters, messages)
##        arcpy.env.overwriteOutput = True
##        arcpy.env.scratchWorkspace = r"C:\Users\ron\Documents\geonis_tests\scratch"
##        arcpy.SaveSettings(r"C:\Users\ron\Documents\geonis_tests\savedEnv.xml")
        for dir in self.inputDirs:
            datafilePath, pkgId, datatype, entityname = ("" for i in range(4))
            loadedFeatureClasses = []
            try:
                with open(os.path.join(dir,"geonis_notes.txt"),'r') as notesfile:
                    notes = notesfile.readlines()
                for line in notes:
                    if ':' in line:
                        lineval = line[line.index(':') + 1 : -1]
                        if line.startswith("PackageId"):
                            pkgId = lineval
                        elif line.startswith("DatafilePath"):
                            datafilePath = lineval
                        elif line.startswith("TYPE"):
                            datatype = lineval
                        elif line.startswith("EntityName"):
                            entityname = lineval
                siteId = siteFromId(pkgId)
                if 'shapefile' in datatype:
                    loadedFeatureClasses = self.loadShapefile(siteId, entityname, datafilePath)
                elif 'kml' in datatype:
                    loadedFeatureClasses = self.loadKml(siteId, entityname, datafilePath)
                else:
                    # no vector data here; continue to next dir, placing this one into the output set
                    self.outputDirs.append(dir)
                    continue
                # amend metadata
                self.mergeMetadata(dir, loadedFeatureClasses)
                # add dir for next tool, in any case except exception
                self.outputDirs.append(dir)
            except Exception as err:
                self.logger.logMessage(WARN, "Exception loading %s. %s\n" % (datafilePath, err.message))
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
    def prepareStorage(self, site, datapath, name):
        """ Create the directories necessary for storing the raw data, and return path to location.
            Also create mosaic dataset for site if needed.
        """
        siteStore = os.path.join(pathToRasterData,site)
        #name, ext =  os.path.splitext( os.path.basename(datapath))
        storageLoc = siteStore + os.sep + name
        #if no site folder, make one
        if not os.path.exists(siteStore):
            os.mkdir(siteStore)
        #if no mosaic dataset, make it
        siteMosDS = pathToRasterMosaicDatasets + os.sep + site
        if not arcpy.Exists(siteMosDS):
            result = arcpy.Copy_management(pathToRasterMosaicDatasets + os.sep + "Template", siteMosDS)
        else:
            #if raster exists, delete it?
            pass
        i = 1
        while os.path.isdir(storageLoc):
            storageLoc = "%s_%s" % (storageLoc, i)
            i += 1
        return storageLoc


    @errHandledWorkflowTask(taskName="Copy raster")
    def copyRaster(self, path, storageLoc):
        """Copy raster data to permanent home. Path must lead to raster dataset of some type."""
        self.logger.logMessage(INFO,"Copying %s to %s\n" % (path, storageLoc))
        data = storageLoc + os.sep + os.path.basename(path)
        #name, ext = os.path.splitext(os.path.basename(path))
        result = arcpy.Copy_management(path, data)
        while result.status < 4:
            time.sleep(.5) #in case it's working in background
        if result.status != 4:
            raise Exception(WARN, "Copying %s to %s did not succeed. Status: %d\n" % (path, storageLoc, result.status))
        return data

    @errHandledWorkflowTask(taskName="Load raster")
    def loadRaster(self, site, path, pId):
        """Load raster to mosaic dataset. Path must lead to raster dataset in permanent home."""
        self.logger.logMessage(INFO,"Loading raster %s to %s\n" % (path, site))
        siteMosDS = pathToRasterMosaicDatasets + os.sep + site
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
        emldataObj = self.getEMLdata(workDir)
        xmlSuppFile = os.path.join(workDir, "supp_metadata.xml")
        createSuppXML(emldataObj, xmlSuppFile)
        if not os.path.isfile(xmlSuppFile):
            self.logger.logMessage(WARN, "Supplemental metadata file missing in %s" % (workDir,))
            return False
        arcpy.env.workspace = workDir
        result = arcpy.XSLTransform_conversion(raster, pathToMetadataMerge, "merged_metadata.xml", xmlSuppFile)
        if result.status == 4:
            result2 = arcpy.MetadataImporter_conversion("merged_metadata.xml", raster)
        else:
            self.logger.logMessage(WARN, "XSLT failed with status %d" % (result.status,))
            return False
        if result2.status != 4:
            self.logger.logMessage(WARN, "Reloading of metadata failed with code %d" % (result2.status,))
            return False
        return True



    def execute(self, parameters, messages):
        super(LoadRasterTypes, self).execute(parameters, messages)
        self.supportedTypes = ("tif", "ascii grid", "coverage", "jpeg", "raster dataset")
        for dir in self.inputDirs:
            datafilePath, pkgId, datatype, entityname = ("" for i in range(4))
            loadedRaster = None
            try:
                with open(os.path.join(dir,"geonis_notes.txt"),'r') as notesfile:
                    notes = notesfile.readlines()
                for line in notes:
                    if ':' in line:
                        lineval = line[line.index(':') + 1 : -1]
                        if line.startswith("PackageId"):
                            pkgId = lineval
                        elif line.startswith("DatafilePath"):
                            datafilePath = lineval
                        elif line.startswith("TYPE"):
                            datatype = lineval
                        elif line.startswith("EntityName"):
                            entityname = lineval
                #check for supported type
                if not self.isSupported(datatype):
                    self.outputDirs.append(dir)
                    continue
                siteId = siteFromId(pkgId)
                rawDataLoc = self.prepareStorage(siteId, datafilePath, entityname)
                os.mkdir(rawDataLoc)
                raster = self.copyRaster(datafilePath, rawDataLoc)
                # amend metadata in place
                if self.mergeMetadata(dir, raster):
                    result = self.loadRaster(siteId, raster, pkgId)
                    if result != 4:
                        self.logger.logMessage(WARN, "Loading %s did not succeed, with code %d.\n" % (raster, result))
                    else:
                        # add dir for next tool, in any case except exception
                        self.outputDirs.append(dir)
                else:
                    self.logger.logMessage(WARN, "Metadata function returned False.\n")
            except Exception as err:
                self.logger.logMessage(WARN, "Exception loading %s. %s\n" % (datafilePath, err.message))
        #pass the list on
        arcpy.SetParameterAsText(3, ";".join(self.outputDirs))


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
                LoadRasterTypes ]


