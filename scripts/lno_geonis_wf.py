'''

Created on Jan 14, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import sys, os, re
import copy
import time, datetime
import json
import httplib, urllib, urllib2, urlparse
from HTMLParser import HTMLParser
import psycopg2
from shutil import copyfileobj, rmtree
from shutil import copy as copyFileToFileOrDir
from cStringIO import StringIO
from zipfile import ZipFile
from lxml import etree
import arcpy
from geonis_log import EvtLog, errHandledWorkflowTask
from arcpy import AddMessage as arcAddMsg, AddError as arcAddErr, AddWarning as arcAddWarn
from arcpy import Parameter
from logging import DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL
from lno_geonis_base import ArcpyTool
from geonis_pyconfig import GeoNISDataType, tempMetadataFilename, dsnfile, pubConnection, arcgiscred, geodatabase
#from geonis_helpers import isShapefile, isKML, isTif, isTifWorld, isASCIIRaster, isFileGDB, isJpeg, isJpegWorld, isEsriE00, isRasterDS, isProjection, isIdrisiRaster
from geonis_helpers import *
#from geonis_helpers import siteFromId, getToken, sendEmail, composeMessage
from geonis_emlparse import createEmlSubset, createEmlSubsetWithNode, writeWorkingDataToXML, readWorkingData, readFromEmlSubset, createSuppXML, stringToValidName, createDictFromEmlSubset
from geonis_postgresql import cursorContext, getEntityInsert, getConfigValue
import pdb
import platform
from pprint import pprint

## *****************************************************************************
class Setup(ArcpyTool):
    """Setup selects test mode or production mode, and stores optional set of identifiers to process, instead of all identifiers."""
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = "Selects mode (test or production), and stores identifiers to process"
        self._label = "Setup"
        self._alias = "setup"

    def getParameterInfo(self):
        params = super(Setup, self).getParameterInfo()
        params.append(arcpy.Parameter(
                  displayName = 'Testing',
                  name = 'testing_mode',
                  datatype = 'Boolean',
                  direction = 'Input',
                  parameterType = 'Required'))
        params.append(arcpy.Parameter(
                  displayName = 'Go to PASTA staging server',
                  name = 'staging',
                  datatype = 'Boolean',
                  direction = 'Input',
                  parameterType = 'Required'))
        params.append(arcpy.Parameter(
                  displayName = 'Scopes/Identifiers to Include',
                  name = 'include_list',
                  datatype = 'GPValueTable',
                  direction = 'Input',
                  parameterType = 'Optional'))
        params.append(arcpy.Parameter(
                  displayName = 'Also remove any matching packages',
                  name = 'cleanup',
                  datatype = 'Boolean',
                  direction = 'Input',
                  parameterType = 'Required'))
                  
        #testing true by default
        params[2].value = True
        params[3].value = True
        params[5].value = False
        params[4].columns = [['GPString','Scope'],['GPString','Identifier(CSV list or range)']]
        return params

    def updateParameters(self, parameters):
        """  """
        super(Setup, self).updateParameters(parameters)
        if parameters[2].value:
            parameters[3].enabled = True
        else:
            parameters[3].value = False
            parameters[3].enabled = False

    def updateMessages(self, parameters):
        """ puts up warning if running in production """
        super(Setup, self).updateMessages(parameters)
        if not parameters[2].value:
            parameters[2].setWarningMessage("Workflow to run in production mode.")
            if parameters[5].value:
                parameters[5].setWarningMessage("About to delete data from production storage.")
            else:
                parameters[5].clearMessage()
        else:
            parameters[2].clearMessage()
            parameters[5].clearMessage()

    def cleanUp(self, pkgArray):
        for p in pkgArray:
            self.logger.logMessage(DEBUG, p.values()[0])

        selectFromPackage = "SELECT packageid FROM package WHERE packageid LIKE %s"
        deleteFromPackage = "DELETE FROM package WHERE packageid = %s"
        selectFromGeonisLayer = "SELECT layername FROM geonis_layer WHERE packageid = %s"
        deleteFromGeonisLayer = "DELETE FROM geonis_layer WHERE packageid = %s"
        selectFromEntity = "SELECT entityname, layername, storage FROM entity WHERE packageid = %s"
        deleteFromEntity = "DELETE FROM entity WHERE packageid = %s"

        sitesAlreadyChecked = []
        with cursorContext(self.logger) as cur:
            for pkgset in pkgArray:
                if not pkgset['inc']:
                    continue
                pkg = pkgset['inc']

                site = pkg.split('-')[2].split('.')[0]
                siteWF = site + getConfigValue('datasetscopesuffix')

                # Handle wildcard, e.g. knb-lter-knz.*
                # Remove *, append %, then select ... where packageid like ...,
                # 'knb-lter-knz.100%' or 'knb-lter-knz.%'
                if pkg[-1:] == '*':
                    srch = pkg[:-1] + '%'
                else:
                    srch = pkg + '%'
                cur.execute(selectFromPackage, (srch, ))
                allPackages = [row[0] for row in cur.fetchall()]

                for package in allPackages:
                    if site not in sitesAlreadyChecked:
                        sitesAlreadyChecked.append(site)

                        # Verify that the map service exists
                        self.logger.logMessage(INFO, "Checking for " + site + " map service")
                        mapServInfoString = getConfigValue('mapservinfo')
                        mapServInfoItems = mapServInfoString.split(';')
                        if len(mapServInfoItems) != 4:
                            self.logger.logMessage(
                                WARN,
                                "Wrong number of items in map serv info: %s" % mapServInfoString
                            )
                            # maybe we have the name and folder
                            mapServInfoItems = [
                                mapServInfoItems[0],
                                mapServInfoItems[1],
                                '',
                                '',
                            ]
                        mapServInfo = {
                            'service_name': mapServInfoItems[0],
                            'service_folder': mapServInfoItems[1],
                            'tags': mapServInfoItems[2],
                            'summary': mapServInfoItems[3]
                        }
                        self.serverInfo = copy.copy(mapServInfo)
                        self.serverInfo["service_name"] = site + getConfigValue('mapservsuffix')

                        available = False
                        tries = 0
                        layerQueryURI = getConfigValue("layerqueryuri")
                        layersUrl = layerQueryURI % (
                            self.serverInfo["service_folder"],
                            self.serverInfo["service_name"]
                        )
                        layerInfoJson = urllib2.urlopen(layersUrl)
                        layerInfo = json.loads(layerInfoJson.readline())
                        del layerInfoJson
                        available = "error" not in layerInfo

                        # Service might still be starting up
                        while not available and tries < 10:
                            time.sleep(5)
                            tries += 1
                            layerInfoJson = urllib2.urlopen(layersUrl)
                            layerInfo = json.loads(layerInfoJson.readline())
                            available = "error" not in layerInfo
                        if not available:
                            self.logger.logMessage(
                                WARN,
                                "Could not connect to %s" % (layersUrl, )
                            )

                        # Stop map service
                        else:
                            pathToServiceDoc = getConfigValue("pathtomapdoc") + os.sep + "servicedefs"
                            self.logger.logMessage(
                                INFO,
                                "Found map services %s" % pathToServiceDoc
                            )
                            with open(arcgiscred) as f:
                                cred = eval(f.readline())
                            token = getToken(cred['username'], cred['password'])
                            if token:
                                serviceStopURL = "/arcgis/admin/services/%s/%s.MapServer/stop" % (
                                    self.serverInfo["service_folder"],
                                    self.serverInfo["service_name"]
                                )
                                self.logger.logMessage(DEBUG, "stopping %s" % (serviceStopURL,))
                                # This request only needs the token and the response formatting parameter
                                params = urllib.urlencode({'token': token, 'f': 'json'})
                                headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                                # Connect to URL and post parameters
                                httpConn = httplib.HTTPConnection("localhost", "6080")
                                httpConn.request("POST", serviceStopURL, params, headers)
                                response = httpConn.getresponse()
                                if (response.status != 200):
                                    self.logger.logMessage(WARN, "Error while attempting to stop service.")
                                httpConn.close()
                            else:
                                self.logger.logMessage(WARN, "Error while attempting to get admin token.")

                        # If this package exists in the map, (1) delete any layers already in the
                        # geonis_layer table from both the map and geonis_layer, and (2) clear
                        # any feature selections (map services will not publish with selected features)
                        if site + '.mxd' in os.listdir(getConfigValue('pathtomapdoc')):
                            self.logger.logMessage(INFO, "Found " + site + ".mxd")
                            mxdfile = getConfigValue('pathtomapdoc') + os.sep + site + '.mxd'

                            mxd = arcpy.mapping.MapDocument(mxdfile)

                            # First, clear selections
                            df = arcpy.mapping.ListDataFrames(mxd)[0]
                            for lyr in arcpy.mapping.ListLayers(mxd):
                                self.logger.logMessage(INFO, "Clear selection: " + lyr.name)
                                arcpy.SelectLayerByAttribute_management(lyr, 'CLEAR_SELECTION')
                            for aTable in arcpy.mapping.ListTableViews(mxd):
                                self.logger.logMessage(INFO, "Clear selection: " + aTable.name)
                                arcpy.SelectLayerByAttribute_management(aTable, 'CLEAR_SELECTION')

                            # Now clear layers
                            layersFrame = arcpy.mapping.ListDataFrames(mxd, 'layers')[0]
                            mapLayerObjectList = arcpy.mapping.ListLayers(mxd, '', layersFrame)
                            mapLayerList = [layer.name.split('.')[-1] for layer in mapLayerObjectList]

                            cur.execute(selectFromGeonisLayer, (package, ))

                            if cur.rowcount:
                                dbMapLayerList = [row[0] for row in cur.fetchall()]

                                # Remove layers from the MXD file that are listed in geonis_layer
                                for layer in dbMapLayerList:
                                    if layer in mapLayerList:
                                        self.logger.logMessage(INFO, "Removing layer: " + layer)
                                        layerToRemove = mapLayerObjectList[mapLayerList.index(layer)]
                                        arcpy.mapping.RemoveLayer(layersFrame, layerToRemove)

                                mxd.save()

                                # Set layerid to -1 in geonis_layer to force mxd to appear in
                                # view vw_stalemapservices
                                cur.execute(
                                    "UPDATE geonis_layer SET layerid = %s WHERE scope = %s",
                                    ('-1', site)
                                )

                            del layersFrame, mxd

                    # Delete from geonis_layer table
                    cur.execute(deleteFromGeonisLayer, (package, ))

                    # Check entity table for package
                    cur.execute(selectFromEntity, (package, ))
                    layersInEntity = None
                    if cur.rowcount:
                        result = cur.fetchall()
                        layersInEntity = [row[0] for row in result if row[0] is not None]
                        layersInEntity.extend([row[1] for row in result if row[1] is not None])
                        cur.execute(deleteFromEntity, (package, ))

                    # Drop tables from geodb
                    geodbTable = getConfigValue('geodatabase') + os.sep + siteWF
                    if arcpy.Exists(geodbTable):
                        arcpy.Delete_management(geodbTable)
                        self.logger.logMessage(
                            INFO,
                            "Dropped " + geodbTable + " from geodatabase"
                        )

                    # Delete rows from the package table
                    cur.execute(deleteFromPackage, (package, ))

                    # Delete folders in the raster data folder
                    rasterFolder = getConfigValue('pathtorasterdata') + os.sep + siteWF
                    if os.path.isdir(rasterFolder):
                        rasterSubfolders = os.listdir(rasterFolder)
                        if rasterSubfolders is not None and layersInEntity is not None:
                            for layer in layersInEntity:
                                for f in rasterSubfolders:
                                    if f.startswith(layer):
                                        rmtree(rasterFolder + os.sep + f)
                                        self.logger.logMessage(
                                            INFO,
                                            "Removed %s" % rasterFolder + os.sep + f
                                        )

                    # Delete entries from raster mosaic datasets
                    mosaicDataset = getConfigValue('pathtorastermosaicdatasets') + os.sep + siteWF
                    if arcpy.Exists(mosaicDataset) and layersInEntity is not None:
                        for layer in layersInEntity:
                            try:
                                arcpy.RemoveRastersFromMosaicDataset_management(
                                    mosaicDataset,
                                    "Name='%s'" % layer
                                )
                                self.logger.logMessage(
                                    INFO,
                                    "Removed %s from raster mosaic %s" % (layer, mosaicDataset)
                                )
                            except ExecuteError:
                                pass

        # Now that we're done making changes, refresh the map services
        # if available:
        RMS = RefreshMapService()
        RMS._isRunningAsTool = False
        paramsRMS = RMS.getParameterInfo()
        paramsRMS[0].value = True
        paramsRMS[1].value = self.logfile
        RMS.execute(paramsRMS, [])
        del RMS

    def execute(self, parameters, messages):
        """ alters role of geonis to set search_path to point to test tables or production tables.
        inserts list of scope.identifier values into limit_identifier table for later tool """
        super(Setup, self).execute(parameters, messages)
        self.logfile = parameters[1].value
        testingMode = parameters[2].value
        staging = parameters[3].value
        # "$user" is required to be first schema to satisfy esri tools
        if testingMode is True:
            stmt1 = 'alter role geonis in database geonis set search_path = "$user",workflow_d,workflow,sde,public;'
            if staging:
                stmt3 = "update workflow_d.wfconfig set strvalue = 'https://pasta-s.lternet.edu' where name = 'pastaurl';"
            else:
                stmt3 = "update workflow_d.wfconfig set strvalue = 'https://pasta.lternet.edu' where name = 'pastaurl';"
        else:
            stmt1 = 'alter role geonis in database geonis set search_path = "$user",workflow,sde,public;'
            stmt3 = None
        stmt2 = "delete from limit_identifier;"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt1)
            cur.execute(stmt2)
            if stmt3 is not None:
                cur.execute(stmt3)
        limitsParam = self.getParamAsText(parameters,4)
        if limitsParam and limitsParam != '' and limitsParam != '#':
            valsArr = []
            # Insert scope and ID values manually for testing
            if hasattr(self, 'setScopeIdManually') and self.setScopeIdManually:

                # "all" or "*" command-line argument means to find all
                # packages on pasta or pasta-s server
                # (limit to all packages beginning with "knb-lter-")
                if self.scope == 'all' or self.scope == '*':
                    scopeList = [s.split('-')[-1] for s in urllib2.urlopen(
                        getConfigValue('pastaurl') + '/package/eml'
                    ).read().split('\n') if s.startswith('knb-lter-')]
                else:
                    scopeList = [self.scope]

                # Get ids for every site
                for s in scopeList:

                    # "all" or "*" command-line argument means find all entities within
                    # selected packages
                    if self.id == 'all' or self.id == '*':
                        idList = urllib2.urlopen(
                            getConfigValue('pastaurl') + '/package/eml/knb-lter-' + s
                        ).read().split('\n')
                        for id in idList:
                            valsArr.append({'inc': 'knb-lter-' + s + '.' + id})

                    # A hyphen in the id argument indicates a range of values
                    elif '-' in self.id:
                        idList = urllib2.urlopen(
                            getConfigValue('pastaurl') + '/package/eml/knb-lter-' + s
                        ).read().split('\n')
                        idRange = [int(j) for j in self.id.split('-')]
                        for j in xrange(idRange[0], idRange[1]+1):
                            if str(j) in idList:
                                valsArr.append({'inc': 'knb-lter-' + s + '.' + str(j)})

                    # Otherwise, only look up a single id
                    else:
                        valsArr.append({'inc': 'knb-lter-' + s + '.' + str(self.id)})

            else:
                limitStrings = limitsParam.split(';')
                limits = [lim.split(' ') for lim in limitStrings]
                for item in limits:
                    scope = 'knb-lter-%s' % (str(item[0]).strip(),)
                    idlist = []
                    ids = str(item[1]).strip()
                    if ',' in ids:
                        for idnum in ids.split(','):
                            if idnum.isdigit():
                                idlist.append(idnum.strip())
                    elif '-' in ids:
                        rng = ids.split('-')
                        low = int(rng[0].strip())
                        hi = int(rng[1].strip()) + 1
                        for i in range(low,hi):
                            idlist.append(str(i))
                    elif '#' in ids or ids == '':
                        idlist.append('*')
                    else:
                        if ids.isdigit():
                            idlist.append(ids)
                    for idn in idlist:
                        valsArr.append({'inc':'%s.%s' % (scope,idn)})
                    
            valsTuple = tuple(valsArr)
            with cursorContext() as cur:
                stmt3 = "insert into limit_identifier values(%(inc)s);"
                cur.executemany(stmt3, valsTuple)
            if parameters[5].value:
                self.cleanUp(valsArr)



## *****************************************************************************
class QueryPasta(ArcpyTool):
    """  """
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = """Makes requests via PASTA REST API to get the latest revisions of all packages,
                            then makes inserts into workflow.package table, checks eml for spatial nodes,
                            and records the number found. Where spatial nodes > 0, downloads the EML."""
        self._label = "S1. Query PASTA"
        self._alias = "query_pasta"

    def getParameterInfo(self):
        params = super(QueryPasta, self).getParameterInfo()
        params.append(arcpy.Parameter(
                        displayName = "Directory of Packages",
                        name = "in_dir",
                        datatype = "Folder",
                        parameterType = "Optional",
                        direction = "Input"))
        params.append(arcpy.Parameter(
                        displayName = "Directory of Packages",
                        name = "out_dir",
                        datatype = "Folder",
                        parameterType = "Derived",
                        direction = "Output"))
        return params

    def updateParameters(self, parameters):
        """called whenever user edits parameter in tool GUI. Can adjust other parameters here. """
        super(QueryPasta, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        """called after all of the update parameter calls. Call attach messages to parameters, usually warnings."""
        super(QueryPasta, self).updateMessages(parameters)

    @errHandledWorkflowTask(taskName="Get scope list")
    def getScopeList(self):
        """ """
        URL = getConfigValue("pastaurl") + "/package/eml"
        resp = None
        try:
            resp = urllib2.urlopen(URL)
            if resp.getcode() == 200:
                return [scope.strip() for scope in resp.readlines() if scope.startswith('knb-lter-')]
            else:
                self.logger.logMessage(WARN, "Bad response from %s" % (URL,))
                return []
        except urllib2.HTTPError:
            self.logger.logMessage(WARN, "Bad response from %s" % (URL,))
            return []
        finally:
            if resp:
                del resp


    @errHandledWorkflowTask(taskName="Get packageId list")
    def getPackageIds(self, scope, limitIdents):
        """ Returns list of latest revision only of packages in the given scope. """
        baseURL = getConfigValue("pastaurl") + "/package/eml"
        retval = []
        #get list of identifiers
        self.logger.logMessage(INFO, "Getting all packages in %s" % (scope,))
        identUrl = "%s/%s" % (baseURL, scope)
        #print identUrl
        resp = urllib2.urlopen(identUrl)
        if resp.getcode() == 200:
            identList = [int(line.strip()) for line in resp.readlines() if line.strip().isdigit()]
        else:
            return retval
        del resp
        #TODO: handle whildcard * in limitIdents
        if limitIdents:
            limitedIdentList = [ident for ident in identList if str(ident) in limitIdents]
        else:
            limitedIdentList = identList
        for i in limitedIdentList:
            revUrl = "%s/%s/%s" % (baseURL, scope, str(i))
            resp = urllib2.urlopen(revUrl)
            if resp.getcode() == 200:
                parts = (scope, str(i), str(max([int(line.strip()) for line in resp.readlines() if line.strip().isdigit()])))
                retval.append('.'.join(parts))
            del resp
            time.sleep(.2)
        return retval


    @errHandledWorkflowTask(taskName="Inserts into package table")
    def packageTableInsert(self, pkidList):
        stmt = "INSERT INTO package (packageid) VALUES (%(packageid)s) EXCEPT SELECT packageid FROM package;"
        with cursorContext(self.logger) as cur:
            dictTupe = tuple([{'packageid':p} for p in pkidList])
            cur.executemany(stmt, dictTupe)
        stmt2 = "UPDATE package SET scope = substring(packageid from 10 for 3),\
                  identifier = CAST( substring(packageid from '\d+') as integer),\
                  revision = CAST (substring (packageid from '\d+$') as integer)\
                  WHERE scope is null;"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt2)


    @errHandledWorkflowTask(taskName="Finding spatial data")
    def findSpatialData(self, scope):
        """ Look at eml for spatial nodes, record number in workflow.package """
        baseURL = getConfigValue("pastaurl") + "/package/metadata/eml"
        stmt = "SELECT * FROM vw_newpackage WHERE scope = %s;"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt, (scope[9:],))
            rows = cur.fetchall()
        #print "found ", len(rows)
        self.logger.logMessage(DEBUG, " new packages found %s" % (len(rows),))
        for row in rows:
            count = 0
            pid, site, ident, rev = row
            url = "%s/%s/%s/%s" % (baseURL, scope, ident, rev)
            try:
                resp = urllib2.urlopen(url)
            except urllib2.HTTPError:
                continue
            if resp.getcode() == 200:
                self.logger.logMessage(DEBUG, "Reading eml from %s" % (url,))
                eml = resp.readlines()
                for line in eml:
                    if "<spatialVector" in line or "<spatialRaster" in line:
                        count += 1
                #update table with spatial count
                #print row, count
                stmt = "UPDATE package SET spatialcount = %s WHERE packageid = %s"
                with cursorContext(self.logger) as cur:
                    cur.execute(stmt, (count, pid))
            del resp
            time.sleep(0.2)


    @errHandledWorkflowTask(taskName="Downloading EML")
    def getEML(self, scope, packageDir):
        """ Query db to get list of packages with spatial, where eml not yet downloaded """
        baseURL = getConfigValue("pastaurl") + "/package/metadata/eml"
        stmt = "SELECT * FROM vw_newspatialpackage WHERE scope = %s;"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt, (scope[9:],))
            rows = cur.fetchall()
        for row in rows:
            pid, site, ident, rev = row
            url = "%s/%s/%s/%s" % (baseURL, scope, ident, rev)
            try:
                resp = urllib2.urlopen(url)
            except urllib2.HTTPError:
                continue
            if resp.getcode() == 200:
                with open(os.path.join(packageDir, pid + '.xml'), 'w') as emlfile:
                    emlfile.writelines(resp.readlines())
                #update table with downloaded timestamp
                stmt = "UPDATE package SET downloaded = %s WHERE packageid = %s"
                with cursorContext(self.logger) as cur:
                    cur.execute(stmt, (datetime.datetime.now(), pid))
            else:
                self.logger.logMessage(WARN, "EML not found for %s" % (url,))
            del row
        del rows



    def execute(self, parameters, messages):
        """
        Fetches a list of updated packages, and inserts their ID's into the
		package table.  Searches the EML metadata for spatial data marked by
		"spatialVector" or "spatialRaster" tags, then inserts the count of
		entities containing spatial information into the package table.
        """
        super(QueryPasta, self).execute(parameters, messages)
        
        # Clear out temp files & folders
        tempXML = getConfigValue("pathtodownloadedpkgs")
        tempDir = getConfigValue("pathtoprocesspkgs")
        for f in os.listdir(tempXML):
            if f.endswith(".xml"):
                os.remove(tempXML + os.sep + f)        
                self.logger.logMessage(INFO, "Removed " + tempXML + os.sep + f)
        for folder in os.listdir(tempDir):
            rmtree(tempDir + os.sep + folder)
            self.logger.logMessage(INFO, "Removed " + tempDir + os.sep + folder)
       
        packageDir = self.getParamAsText(parameters,2)
        if packageDir is None or packageDir == '' or packageDir == '#':
            packageDir = getConfigValue("pathtodownloadedpkgs")
        #check db for limits to scopes/identifiers
        with cursorContext(self.logger) as cur:
            stmt1 = "delete from errornotify;"
            cur.execute(stmt1)
            stmt2 = "select * from limit_identifier;"
            cur.execute(stmt2)
            rows = cur.fetchall()
            limits = [r[0] for r in rows]
        if limits:
            scopelimit = [lim.split('.')[0] for lim in limits]
        allscopes = self.getScopeList()
        if scopelimit:
            scopes = [s for s in allscopes if s in scopelimit]
        else:
            scopes = allscopes
        for scope in scopes:
            if limits:
                identArray = [lim.split('.')[1] for lim in limits if lim.split('.')[0] == scope]
            else:
                identArray = []
            try:
                pids = self.getPackageIds(scope, identArray)
                #pids = ['knb-lter-knz.2.7', 'knb-lter-knz.3.9', 'knb-lter-knz.4.8', 'knb-lter-knz.5.7', 'knb-lter-knz.6.7', 'knb-lter-knz.7.7', 'knb-lter-knz.9.8', 'knb-lter-knz.10.7', 'knb-lter-knz.11.7', 'knb-lter-knz.12.7', 'knb-lter-knz.13.7', 'knb-lter-knz.14.7', 'knb-lter-knz.16.7', 'knb-lter-knz.17.6', 'knb-lter-knz.18.6', 'knb-lter-knz.19.6', 'knb-lter-knz.23.6', 'knb-lter-knz.24.6', 'knb-lter-knz.25.6', 'knb-lter-knz.26.6', 'knb-lter-knz.27.6', 'knb-lter-knz.28.6', 'knb-lter-knz.29.6', 'knb-lter-knz.30.6', 'knb-lter-knz.32.6', 'knb-lter-knz.33.6', 'knb-lter-knz.34.6', 'knb-lter-knz.37.6', 'knb-lter-knz.38.6', 'knb-lter-knz.46.4', 'knb-lter-knz.47.4', 'knb-lter-knz.49.4', 'knb-lter-knz.50.4', 'knb-lter-knz.51.4', 'knb-lter-knz.55.6', 'knb-lter-knz.57.4', 'knb-lter-knz.58.4', 'knb-lter-knz.59.4', 'knb-lter-knz.60.4', 'knb-lter-knz.61.4', 'knb-lter-knz.63.4', 'knb-lter-knz.64.4', 'knb-lter-knz.66.4', 'knb-lter-knz.68.4', 'knb-lter-knz.70.4', 'knb-lter-knz.76.6', 'knb-lter-knz.77.6', 'knb-lter-knz.95.4', 'knb-lter-knz.200.3', 'knb-lter-knz.201.3', 'knb-lter-knz.202.3', 'knb-lter-knz.205.2', 'knb-lter-knz.210.1', 'knb-lter-knz.211.2', 'knb-lter-knz.222.2', 'knb-lter-knz.230.1', 'knb-lter-knz.240.2', 'knb-lter-knz.245.2']
                #print len(pids)
                self.packageTableInsert(pids)
                self.findSpatialData(scope)
                self.getEML(scope, packageDir)
            except Exception as err:
                self.logger.logMessage(WARN, err.message)
        #pass the package download dir to workflow
        arcpy.SetParameterAsText(3, packageDir)


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
        #not zipping downloaded eml; just copy to dest
        if apackage.endswith(".zip"):
            with ZipFile(apackage) as pkg:
                if pkg.testzip() is None:
                    pkg.extractall(destpath)
                else:
                    self.logger.logMessage(WARN,"%s did not pass zip test." % (apackage,))
                    raise Exception("Zip test fail.")
        else:
            os.mkdir(destpath)
            copyFileToFileOrDir(apackage, destpath)
        return destpath

    @errHandledWorkflowTask(taskName="Parse EML")
    def parseEML(self, workDir):
        retval = []
        if not os.path.isdir(workDir):
            self.logger.logMessage(WARN,"Not a directory %s" % (workDir,))
            raise Exception("No directory passed.")
        allfiles = os.listdir(workDir)
        xmlfiles = [f for f in allfiles if f[-4:].lower() == '.xml']
        if len(xmlfiles) == 0:
            self.logger.logMessage(WARN,"No xml files in %s" % (workDir,))
            raise Exception("No xml file in package.")
        elif len(xmlfiles) > 1:
            pkgfiles = [f for f in xmlfiles if f[:8].lower() == 'knb-lter']
            if len(pkgfiles) != 1:
                self.logger.logMessage(WARN,"More than one EML file in %s ?" % (workDir,))
                if len(pkgfiles) == 0:
                    raise Exception("No EML file in package.")
        else:
            pkgfiles = xmlfiles
        emlfile = os.path.join(workDir, pkgfiles[0])
        pkgId, dataEntityNum = createEmlSubset(workDir, emlfile)
        if dataEntityNum > 1:
            for i in range(1, dataEntityNum + 1):
                parentDir = os.path.dirname(workDir)
                path = parentDir + os.sep + pkgId + "." + str(i)
                if not os.path.exists(path):
                    os.mkdir(path)
                createEmlSubsetWithNode(workDir, path, i, self.logger)
                retval.append(path)
        else:
            createEmlSubsetWithNode(workDir, logger = self.logger)
            retval.append(workDir)
        return (pkgId, retval)
##        emldata = parseAndPopulateEMLDicts(emlfile, self.logger)
##        with open(emldatafile,'w') as datafile:
##            datafile.write(repr(emldata))

##    @errHandledWorkflowTask(taskName="Package initial entry")
##    def makePackageRec(self, pkgId):
##        """Inserts record into package table """
##        stmt, vals = getPackageInsert()
##        vals["packageid"] = pkgId
##        scope, id, rev = siteFromId(pkgId)
##        vals["scope"] = scope
##        vals["identifier"] = id
##        vals["revision"] = rev
##        with cursorContext(self.logger) as cur:
##            cur.execute(stmt, vals)

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
        resource = None
        if dataloc is not None:
            try:
                #TODO: trap httperror, check return code
                #uri = HTMLParser().unescape(dataloc)
                uri = dataloc
                sdatafile = os.path.join(workDir,emldata["shortEntityName"] + '.zip')
                try:
                    resource = urllib2.urlopen(uri)                                      
                    contentLength = resource.info().get('Content-Length', '')
                    try:
                        contentLength = int(contentLength)
                    except ValueError:
                        contentLength = None

                except urllib2.HTTPError as httperr:
                    errorText = "Request to %s returned error, code %i." % (uri, httperr.code)
                    if httperr.code == 404 and r'%' in uri:
                        errorText += " This address includes special percent-encoded characters, which may make the address invalid."
                    raise Exception(errorText)
                
                if resource and resource.getcode() == 200:
                    with open(sdatafile,'wb') as dest:
                        copyfileobj(resource, dest)
                    
                    # Check file size
                    dataLength = os.stat(sdatafile).st_size
                    if contentLength is not None and contentLength != dataLength:
                        self.logger.logMessage(WARN, str(dataLength) + " bytes read, incomplete download (content-length: " + str(contentLength) + ")")
                        raise urllib2.URLError('Incomplete download')
                    else:
                        self.logger.logMessage(INFO, str(dataLength) + " bytes read, content-length ok")

                    # Check magic number
                    with open(sdatafile, 'rb') as dest:
                        magicNum = dest.read(4)
                        if magicNum != '\x50\x4b\x03\x04':
                            self.logger.logMessage(WARN, "Zipfile magic number mismatch: " + repr(magicNum))
                    
                else:
                    raise Exception("Request to %s failed." % (uri,) )
            except Exception as e:
                raise Exception("Error attempting to download data.\n" + e.message)
            finally:
                if resource:
                    resource.close()
            if not os.path.exists(sdatafile):
                raise Exception("spatial data file %s missing after download" % (sdatafile,))

            with ZipFile(sdatafile, 'r') as sdata:
                
                # Check for nested zip files
                nestedZip = False
                for name in sdata.namelist():
                    if re.search(r'\.zip$', name) != None:
                        nestedZip = True
                        sdataread = StringIO(sdata.read(name))
                        with ZipFile(sdataread) as sdataInner:
                            if sdataInner.testzip() is None:
                                sdataInner.extractall(workDir)
                            else:
                                self.logger.logMessage(WARN,"%s did not pass zip test." % (sdatafile,))
                                raise Exception("Zip test fail.")                    
                    else:
                        sdata.extract(name, workDir)
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
        self.logger.logMessage(DEBUG,  "in: %s; out: %s" % (packageDir, outputDir))
        if not os.path.isdir(outputDir):
            os.mkdir(outputDir)
        #allpackages = [os.path.join(packageDir,f) for f in os.listdir(packageDir) if os.path.isfile(os.path.join(packageDir,f)) and f[-4:].lower() == '.zip']
        allpackages = [os.path.join(packageDir,f) for f in os.listdir(packageDir) if os.path.isfile(os.path.join(packageDir,f)) and f[-4:].lower() == '.xml']
        #loop over packages, handling one at a time. an error will drop the current package and go to the next one
        for pkg in allpackages:
            self.logger.logMessage(DEBUG, "Starting work on %s" % (pkg,))
            try:
                workdir = self.unzipPkg(pkg, outputDir)
                packageId, dataDirs = self.parseEML(workdir)
                for dir in dataDirs:
                    #loop over data package dirs, in most cases just one, if error keep trying others
                    try:
                        initWorkingData = readWorkingData(dir, self.logger)
                        if initWorkingData["spatialType"] is None:
                            self.logger.logMessage(WARN, "No EML spatial node. The data in %s with id %s will not be processed." % (pkg, packageId))
                            continue
                    except Exception as err:
                        self.logger.logMessage(WARN, "The data in %s will not be processed. %s" % (dir, err.message))
                        if packageId:
                            with cursorContext(self.logger) as cur:
                                cur.execute("UPDATE package set report = %s WHERE packageid = %s;",(err.message,packageId))
                    try:
                        self.readURL(dir)
                        self.retrieveData(dir)
                        self.makeEntityRec(dir)
                        carryForwardList.append(dir)
                    except Exception as err:
                        self.logger.logMessage(WARN, "The data in %s will not be processed. %s" % (dir, err.message))
                        emldata = readWorkingData(dir, self.logger)
                        contact = emldata["contact"]
                        if packageId:
                            with cursorContext(self.logger) as cur:
                                cur.execute("SELECT addpackageerrorreport(%s,%s,%s);", (packageId, contact, err.message ))
                                #cur.execute("UPDATE package set report = %s WHERE packageid = %s;",(err.message,packageId))
                                #cur.execute("INSERT INTO errornotify VALUES (%s,%s);", (packageId,contact))
            except Exception as err:
                self.logger.logMessage(WARN, "The data in %s will not be processed. %s" % (pkg, err.message))
                emldata = readWorkingData(workdir, self.logger)
                pkgId = emldata["packageId"]
                contact = emldata["contact"]
                if pkgId:
                    with cursorContext(self.logger) as cur:
                        cur.execute("SELECT addpackageerrorreport(%s,%s,%s);", (pkgId, contact, err.message ))
                        #cur.execute("UPDATE package set report = %s WHERE packageid = %s;",(err.message,pkgId))
                        #cur.execute("INSERT INTO errornotify VALUES (%s,%s);", (pkgId,contact))
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
            self.logger.logMessage(INFO, "Found spatialVector tag")
            retval = GeoNISDataType.SPATIALVECTOR
        elif spatialTypeItem == "spatialRaster":
            self.logger.logMessage(INFO, "Found spatialRaster tag")
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
            elif isIdrisiRaster(afile):
                allPotentialFiles.append((afile, GeoNISDataType.RST))
            else:
                for fileType, isFileType in checkFileTypes.items():
                    if isFileType(afile):
                        allPotentialFiles.append((afile, fileType))
                        
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
                    if hint[0] == 'any raster':
                        self.logger.logMessage(
                            WARN, (
                                "type(eml) has been set to the generic value of 'any raster'; "
                                "instead of extension " + allPotentialFiles[0][1][0]
                            )
                        )
                    else:
                        self.logger.logMessage(
                            WARN, 
                            "Expected data type %s is not exactly found data type %s for %s" \
                            % (hint, allPotentialFiles[0][1], allPotentialFiles[0][0])
                        )
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
    def entityNameMatch(self, emlName, dataFilePath):
        dataFileName = os.path.basename(dataFilePath).lower()
        if emlName.lower() == dataFileName:
            return True
        else:
            name, ext = os.path.splitext(dataFileName)
            if emlName.lower() == name:
                self.logger.logMessage(INFO, "emlName %s matched data name %s" % (emlName, dataFileName))
                return True
            else:
                self.logger.logMessage(WARN, "emlName %s did not match data name %s" % (emlName, dataFileName))
                return False

    @errHandledWorkflowTask(taskName="Attribute name check")
    def attributeNames(self, workDir, dataFilePath):
        # (datadir, datafilepath)
        emlAttNames = []
        entityAttNames = []
        emlTree = etree.parse(os.path.join(workDir,"emlSubset.xml"))
        attNodes = emlTree.xpath("//attributeList/attribute")
        for att in attNodes:
            emlAttNames.append(att.xpath("attributeName")[0].text.upper())
        del emlTree
        fields = arcpy.ListFields(dataFilePath)
        entityAttNames = [str(f.name.upper()) for f in fields]
        diff = list(set(emlAttNames) ^ set(entityAttNames))
        if len(diff) > 0:
            self.logger.logMessage(WARN,"Attribute names in eml and entity did not match. %s" % str(diff))
            self.logger.logMessage(WARN, "EML: " + str(emlAttNames))
            self.logger.logMessage(WARN, "Entity: " + str(entityAttNames))
        return diff

    @errHandledWorkflowTask(taskName="Checking precision")
    def checkPrecision(self, dataFilePath):
        passed = True
        fields = arcpy.ListFields(dataFilePath)
        for fld in fields:
            if fld.type == u'Double' and fld.precision > 15:
                passed = False
            elif fld.type == u'Single' and fld.precision > 6:
                passed = False
            elif fld.type == u'Integer' and fld.precision > 10:
                passed = False
        if not passed:
            self.logger.logMessage(WARN,"Precision test failed.")
        return passed


    @errHandledWorkflowTask(taskName="Format report")
    def getReport(self, pkgId, reportText):
        """eventually when we know the report format, this could be an XSLT from emlSubset+workingData
        to the formatted report, perhaps json, xml, or html """
        if pkgId is None or len(reportText) == 0:
            return ""
        retval = "Package ID with issue: " + pkgId + "\n"
        for item in reportText:
            for kys in item:
                retval += "%s - %s\n" % (kys, item[kys])
        return retval

    def execute(self, parameters, messages):
        super(CheckSpatialData, self).execute(parameters, messages)
        try:
            assert self.inputDirs != None
            assert self.outputDirs != None
            reportText = []
            formattedReport = ''
            for dataDir in self.inputDirs:
                self.logger.logMessage(INFO, "***working in: " + dataDir + "***")
                try:
                    status = "Entering data checks."
                    emldata = readWorkingData(dataDir, self.logger)
                    pkgId = emldata["packageId"]
                    shortPkgId = pkgId[9:]
                    reportfilePath = os.path.join(dataDir, shortPkgId + "_geonis_report.txt")
                    entityName = emldata["entityName"]
                    objectName = emldata["objectName"]
                    hint = self.examineEMLforType(emldata)
                    emldata["type(eml)"] = hint
                    foundFile, spatialType = self.acceptableDataType(dataDir, emldata)
                    if spatialType == GeoNISDataType.NA:
                        emldata["type"] = "NOT FOUND"
                        status = "Data type not found with tentative type %s" % hint
                        raise Exception("No compatible data found in %s" % dataDir)
                    emldata["datafilePath"] = foundFile
                    status = "Found acceptable data file."
                    nameMatch = False
                    if emldata['spatialType'] == 'spatialVector':
                        nameMatch = self.entityNameMatch(objectName, foundFile)
                        emldata["datafileMatchesEntity"] = nameMatch
                    else:
                        emldata["datafileMatchesEntity"] = True
                    #force objectName to have data file path, and use objectName for layer and database
                    if not nameMatch:
                        datafilename = os.path.splitext(os.path.basename(foundFile))[0]
                        if len(datafilename) > 0:
                            datafilename = stringToValidName(datafilename, max = 31)
                            emldata["objectName"] = datafilename
                    if spatialType == GeoNISDataType.KML:
                        self.logger.logMessage(INFO, "kml found")
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
                        self.logger.logMessage(WARN, "arcinfo e00 reported. Should have been unpacked.")
                    if spatialType == GeoNISDataType.TIF:
                        emldata["type"] = "tif"
                    if spatialType == GeoNISDataType.JPEG:
                        emldata["type"] = "jpg"
                    if spatialType == GeoNISDataType.SPATIALRASTER:
                        emldata["type"] = "raster dataset"
                    if spatialType == GeoNISDataType.SPATIALVECTOR:
                        emldata["type"] = "vector"
                    status = "File type assigned"
                    
                    # If this is a vector data set, get list of mismatches in attribute names
                    if emldata['spatialType'] == 'spatialVector':
                        mismatchedAtts = self.attributeNames(dataDir,emldata["datafilePath"])
                        if mismatchedAtts != []:
                            reportText.append({"Fields mismatch":str(mismatchedAtts)})
                            status = "Found mismatch in attribute names"
                        else:
                            status = "Matched all attribute names"

                    if not self.checkPrecision(emldata["datafilePath"]):
                        raise Exception("Precision of field incompatible with geodatabase.")
                except Exception as err:
                    status = "Failed after %s with %s" % (status, err.message)
                    self.logger.logMessage(WARN, err.message)
                    reportText.append({"Status":"Failed"})
                    reportText.append({"Error message":err.message})
                else:
                    status = "Passed checks"
                    #empty reportText => no issues
                    #reportText.append({"Status":"OK"})
                    self.outputDirs.append(dataDir)
                finally:
                    #write status msg to workflow.entity. Need both packagid and entityname to be unique
                    if pkgId and entityName:
                        stmt = "UPDATE entity set status = %s WHERE packageid = %s and entityname = %s;"
                        with cursorContext(self.logger) as cur:
                            cur.execute(stmt, (status[:499], pkgId, entityName))
                    writeWorkingDataToXML(dataDir, emldata, self.logger)
                    formattedReport = self.getReport(pkgId, reportText)
                    if formattedReport != '':
                        if pkgId and entityName:
                            with cursorContext(self.logger) as cur:
                                cur.execute("SELECT addentityerrorreport(%s,%s,%s,%s);", (pkgId, entityName, emldata["contact"], formattedReport ))
                                #stmt2 = "UPDATE entity set report = %s WHERE packageid = %s and entityname = %s;"
                                #cur.execute(stmt2, (formattedReport, pkgId, entityName))
            arcpy.SetParameterAsText(3, ";".join(self.outputDirs))
            arcpy.SetParameterAsText(4,str(formattedReport))
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
        geodatabase = getConfigValue("geodatabase")
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
        geodatabase = getConfigValue("geodatabase")
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
        pathToStylesheets = getConfigValue("pathtostylesheets")
        result = arcpy.XSLTransform_conversion(loadedFeatureClass, pathToStylesheets + os.sep + "metadataMerge.xsl", "merged_metadata.xml", xmlSuppFile)
        result2 = arcpy.MetadataImporter_conversion("merged_metadata.xml", loadedFeatureClass)


    @errHandledWorkflowTask(taskName="Update entity table")
    def updateTable(self, workDir, loadedFeatureClass, pkid, entityName):
        if not loadedFeatureClass:
            return
        scope_data = os.sep.join(loadedFeatureClass.split(os.sep)[-2:])
        stmt = "UPDATE entity set storage = %s WHERE packageid = %s and entityname = %s;"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt, (scope_data, pkid, entityName))

    def execute(self, parameters, messages):
        super(LoadVectorTypes, self).execute(parameters, messages)
        for dir in self.inputDirs:
            datafilePath, pkgId, datatype, entityName, objectName = ("" for i in range(5))
            try:
                status = "Entering load vector"
                emldata = readWorkingData(dir, self.logger)
                pkgId = emldata["packageId"]
                datafilePath = emldata["datafilePath"]
                datatype = emldata["type"]
                entityName = emldata["entityName"]
                objectName = emldata["objectName"]
                siteId, n, m = siteFromId(pkgId)
                pdb.set_trace()
                #TODO: must add site and optionally '_d' to feature class name. Must be unique in geonis db
                fullObjectName = objectName + '_' + siteId
                if getConfigValue("schema").endswith("_d"):
                    fullObjectName = fullObjectName + "_d"
                scopeWithSuffix = siteId + getConfigValue("datasetscopesuffix")
                if 'shapefile' in datatype:

                    # arcpy.FeatureClassToFeatureClass_conversion returns an ERROR 999999 if
                    # it receives a fullObjectName that it doesn't like (e.g. GIS300_knz_d
                    # from the knb-lter-knz.230.2 data set).
                    # Since this seems deterministic, just add an extra _d to the end if
                    # loadShapefile() fails as a workaround...
                    try:
                        loadedFeatureClass = self.loadShapefile(scopeWithSuffix, fullObjectName, datafilePath)
                    except Exception as err:
                        if err[0].find('ERROR 999999') != -1:
                            loadedFeatureClass = self.loadShapefile(scopeWithSuffix, fullObjectName + '_d', datafilePath)
                            self.logger.logMessage(
                                WARN,
                                "Added extra _d suffix in geodatabase due to "
                                + fullObjectName + " returning an error."
                            )

                    status = "Loaded shapefile"
                elif 'kml' in datatype:
                    loadedFeatureClass = self.loadKml(scopeWithSuffix, fullObjectName, datafilePath)
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
                self.updateTable(dir, loadedFeatureClass, pkgId, entityName)
                # add dir for next tool, in any case except exception
                self.outputDirs.append(dir)
                status = "Load with metadata complete"
            except Exception as err:
                status = "Failed after %s with %s" % (status, err.message)
                self.logger.logMessage(WARN, "Exception loading %s. %s\n" % (datafilePath, err.message))
                if emldata and pkgId and entityName:
                    contact = emldata["contact"]
                    with cursorContext(self.logger) as cur:
                        cur.execute("SELECT addentityerrorreport(%s,%s,%s,%s);", (pkgId, entityName, contact, err.message))
            finally:
                #write status msg to db table
                if pkgId and entityName:
                    stmt = "UPDATE entity set status = %s WHERE packageid = %s and entityname = %s;"
                    with cursorContext(self.logger) as cur:
                        cur.execute(stmt, (status[:499], pkgId, entityName))
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
            Appends '_main' or '_test' to scope for storage dir and mosaic dataset name (db terms
            not allowed as ds name--I'm looking at you, and)
        """
        dsName = site + getConfigValue("datasetscopesuffix")
        pathToRasterData = getConfigValue("pathtorasterdata")
        siteStore = os.path.join(pathToRasterData,dsName)

        #name, ext =  os.path.splitext( os.path.basename(datapath))
        storageLoc = siteStore + os.sep + name
        #if no site folder, make one
        if not os.path.exists(siteStore):
            os.mkdir(siteStore)
        #if no mosaic dataset, make it
        pathToRasterMosaicDatasets = getConfigValue("pathtorastermosaicdatasets")
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
        pathToStylesheets = getConfigValue("pathtostylesheets")
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
    def updateTable(self, location, pkid, entityName):
        # get last three parts of location:  scope, entity dir, entity name
        parts = location.split(os.sep)
        if len(parts) > 3:
            loc = os.sep.join(parts[-3:])
        else:
            loc = location[-50:]
        stmt = "UPDATE entity set storage = %s WHERE packageid = %s and entityname = %s;"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt, (loc, pkid, entityName))


    def execute(self, parameters, messages):
        super(LoadRasterTypes, self).execute(parameters, messages)
        #TODO: add file gdb to list, and handle. Could be mosaic ds in file gdb, e.g.
        self.supportedTypes = ("tif", "ascii raster", "coverage", "jpg", "raster dataset")
        for dir in self.inputDirs:
            datafilePath, pkgId, datatype, entityName = ("" for i in range(4))
            loadedRaster = None
            try:
                status = "Entering raster load"
                emldata = readWorkingData(dir, self.logger)
                pkgId = emldata["packageId"]
                datafilePath = emldata["datafilePath"]

                # If there's a 'type' tag in the EML, then use that as a description of the data;
                # otherwise, just make sure it's raster data
                if 'type' in emldata.keys():
                    datatype = emldata['type']
                elif 'spatialType' in emldata.keys() and emldata['spatialType'] == 'spatialRaster':
                    datatype = "raster dataset"
                else:
                    datatype = "vector"
                entityName = emldata["entityName"]
                objectName = emldata["objectName"]
                #check for supported type
                if not self.isSupported(datatype):
                    self.outputDirs.append(dir)
                    continue
                siteId, n, m = siteFromId(pkgId)
                rawDataLoc, mosaicDS = self.prepareStorage(siteId, datafilePath, objectName)
                status = "Storage prepared"
                os.mkdir(rawDataLoc)
                raster = self.copyRaster(datafilePath, rawDataLoc)
                self.updateTable(raster, pkgId, entityName)

                # Add objectName to entity table as "layername" so there is a
                # record of the raster data folder name
                with cursorContext(self.logger) as cur:
                    cur.execute(
                        "UPDATE entity SET layername = %s WHERE entityname = %s", 
                        (objectName, entityName)
                    )

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
                    stmt = "UPDATE entity set status = %s WHERE packageid = %s;"
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
        stmt = "SELECT storage, status FROM entity WHERE packageid = %s and entityname = %s;"
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
        site = siteFromId(workingData["packageId"])[0]
        layerName = workingData["objectName"]
        mxdName = site + ".mxd"
        pathToMapDoc = getConfigValue("pathtomapdoc")
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
        geodatabase = getConfigValue("geodatabase")
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

    @errHandledWorkflowTask(taskName="Insert into layer table")
    def makeLayerRec(self, workDir, pkgId, name):
        """Insert record into workflow.geonis_layer for this entity  """
        insstmt = "INSERT INTO geonis_layer \
         (id, packageid, scope, entityname, entitydescription, title, abstract, purpose, keywords, sourceloc, layername, arcloc, layerid) VALUES \
         (%(id)s, %(pid)s, %(site)s, %(name)s, %(desc)s, %(title)s, %(abstract)s, %(purpose)s, %(keywords)s, %(source)s, %(layer)s, %(arcloc)s, %(layerid)s);"
        selstmt = "SELECT id, status FROM entity WHERE packageid = %s and entityname = %s;"
        with cursorContext(self.logger) as cur:
            cur.execute(selstmt, (pkgId, name))
            row = cur.fetchone()
            if row:
                recId, status = row
            else:
                raise Exception("Entity rec not found %s, %s" % (pkgId, name))
        if status != "Added to map":
            self.logger.logMessage(DEBUG, "Status of entity is %s" % (status,))
        insertObj = createDictFromEmlSubset(workDir)
        insertObj['id'] = recId
        insertObj['pid'] = pkgId
        insertObj['name'] = name
        insertObj['site'] = siteFromId(pkgId)[0]
        insertObj['arcloc'] = None
        insertObj['layerid'] = -1
        #catch some things that might be missing
        if not "layer" in insertObj or insertObj['layer'] is None or insertObj['layer'] == '':
            #there should be a layer name if it was added to a map
            insertObj['layer'] = None
        for optional in ['abstract', 'purpose', 'desc', 'keywords']:
            if not optional in insertObj:
                insertObj[optional] = None
        if len(insertObj) == 13:
            with cursorContext(self.logger) as cur:
                cur.execute(insstmt, insertObj)

    @errHandledWorkflowTask(taskName="Add extra info to error report")
    def modifyErrorReport(self):
        noErrorsFound = "No errors found."
        with cursorContext(self.logger) as cur:
            # May have to remove joins if tables get very large...
            '''
            selectReports = (
                "SELECT ep.*, g.title, g.sourceloc FROM ( "
                    "SELECT "
                        "p.packageid, p.report, e.report, e.id, p.scope, p.identifier, p.revision, e.entityname, "
                        "e.layername, p.downloaded, e.israster, e.isvector, e.mxd, e.status "
                        "FROM package AS p "
                    "FULL JOIN "
                        "entity AS e "
                        "ON p.packageid = e.packageid "
                    #"WHERE e.report IS NOT NULL OR p.report IS NOT NULL "
                ") AS ep "
                "LEFT OUTER JOIN "
                    "geonis_layer AS g "
                    "ON ep.id = g.id "
                "ORDER BY ep.packageid"
            )
            '''
            selectReports = (
                "SELECT "
                    "p.packageid, p.report, e.report, e.id, p.scope, p.identifier, p.revision, e.entityname, "
                    "e.layername, p.downloaded, e.israster, e.isvector, e.mxd, e.status "
                    "FROM package AS p "
                "FULL JOIN "
                    "entity AS e "
                    "ON p.packageid = e.packageid "
                "ORDER BY p.packageid"
            )
            cur.execute(selectReports)
            if cur.rowcount:
                results = cur.fetchall()
                cols = [col.name for col in cur.description]
                for row in results:
                    biography = {
                        'pasta': getConfigValue('pastaurl'),
                        'workflow': getConfigValue('datasetscopesuffix'),
                        'service': getConfigValue('layerqueryuri') % (
                            getConfigValue('mapservinfo').split(';')[1],
                            row[4] + getConfigValue('mapservsuffix'),
                        ),
                    }
                    for idx, d in enumerate(cols):
                        if d == 'downloaded':
                            biography[d] = str(row[idx])
                        elif d != 'report' and d != 'id':
                            biography[d] = row[idx]

                    # Update the entity and package tables
                    report = row[2] if row[2] is not None else noErrorsFound
                    cur.execute(
                        "UPDATE entity SET report = %s WHERE id = %s", 
                        (report + " | " + json.dumps(biography), row[3])
                    )

                    report = row[1] if row[1] is not None else noErrorsFound
                    cur.execute(
                        "UPDATE package SET report = %s WHERE packageid = %s", 
                        (report + " | " + json.dumps(biography), row[0])
                    )


    def execute(self, parameters, messages):
        super(UpdateMXDs, self).execute(parameters, messages)
        for dir in self.inputDirs:
            try:
                status = "Entering add vector to MXD"
                workingData = readWorkingData(dir, self.logger)
                if workingData["spatialType"] == "spatialVector":
                    pkgId = workingData["packageId"]
                    lName, mxdName = self.addVectorData(dir, workingData)
                    with cursorContext(self.logger) as cur:
                        stmt = "UPDATE entity set mxd = %(mxd)s, layername = %(layername)s, completed = %(now)s, status = 'Added to map' \
                         WHERE packageid = %(pkgId)s and entityname = %(entityName)s;"
                        cur.execute(stmt,
                         {'mxd': mxdName, 'layername' : lName, 'now' : datetime.datetime.now(), 'pkgId': pkgId, 'entityName' : workingData["entityName"]})
                    self.makeLayerRec(dir, pkgId, workingData["entityName"] )
                    status = "Ready for map service"
                else:
                    status = "Carried forward to next tool"
                self.outputDirs.append(dir)
            except Exception as err:
                status = "Failed after %s with %s" % (status, err.message)
                self.logger.logMessage(WARN, err.message)
                if workingData:
                    contact = workingData["contact"]
                    pkgId = workingData["packageId"]
                    entityName = workingData["entityName"]
                    with cursorContext(self.logger) as cur:
                        cur.execute("SELECT addentityerrorreport(%s,%s,%s,%s);", (pkgId, entityName, contact, err.message ))
            finally:
                #write status msg to db table
                if workingData:
                    stmt = "UPDATE entity set status = %s WHERE packageid = %s  and entityname = %s;"
                    with cursorContext(self.logger) as cur:
                        cur.execute(stmt, (status[:499], workingData["packageId"], workingData["entityName"]))

        # Add extra info to the error report as needed
        self.modifyErrorReport()

        #pass the list on
        arcpy.SetParameterAsText(3, ";".join(self.outputDirs))


## *****************************************************************************
class RefreshMapService(ArcpyTool):
    """Adds new vector data to map, creates service def draft, modifies it to replace, uploads and starts service,
       waits for service to start, gets list of layers, updates table with layer IDs. """
    def __init__(self):
        ArcpyTool.__init__(self)
        self._description = "Creates service def draft, modifies it to replace, uploads and starts service, waits for service to start, gets list of layers, updates table with layer IDs."
        self._label = "Refresh Map Service"
        self._alias = "refreshMapServ"

    def getParameterInfo(self):
        return super(RefreshMapService, self).getParameterInfo()

    def updateParameters(self, parameters):
        """called whenever user edits parameter in tool GUI. Can adjust other parameters here. """
        super(RefreshMapService, self).updateParameters(parameters)

    def updateMessages(self, parameters):
        """called after all of the update parameter calls. Call attach messages to parameters, usually warnings."""
        super(RefreshMapService, self).updateMessages(parameters)


    @errHandledWorkflowTask(taskName="Create service draft")
    def draftSD(self, mxdname):
        """Stops service, creates SD draft, modifies it"""
        """http://maps3.lternet.edu:6080/arcgis/admin/services/Test/VectorData.MapServer/stop"""
        pathToMapDoc = getConfigValue("pathtomapdoc")
        arcpy.env.workspace = pathToMapDoc
        pathToServiceDoc = arcpy.env.workspace + os.sep + "servicedefs"
        site, ext = mxdname.split('.')
        self.serverInfo["service_name"] = site + getConfigValue('mapservsuffix')
        #stop service first
        with open(arcgiscred) as f:
            cred = eval(f.readline())
        token = getToken(cred['username'], cred['password'])
        if token:
            serviceStopURL = "/arcgis/admin/services/%s/%s.MapServer/stop" % (self.serverInfo["service_folder"],self.serverInfo["service_name"])
            self.logger.logMessage(DEBUG,"stopping %s" % (serviceStopURL,))
            # This request only needs the token and the response formatting parameter
            params = urllib.urlencode({'token': token, 'f': 'json'})
            headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
            # Connect to URL and post parameters
            httpConn = httplib.HTTPConnection("localhost", "6080")
            httpConn.request("POST", serviceStopURL, params, headers)
            response = httpConn.getresponse()
            if (response.status != 200):
                self.logger.logMessage(WARN, "Error while attempting to stop service.")
            httpConn.close()
        else:
             self.logger.logMessage(WARN, "Error while attempting to get admin token.")
        mxd = arcpy.mapping.MapDocument(pathToMapDoc + os.sep + mxdname)
        sdDraft = pathToServiceDoc + os.sep + self.serverInfo['service_name'] + ".sddraft"
        self.logger.logMessage(DEBUG,"Draft loc: %s" % (sdDraft,))
        arcpy.mapping.CreateMapSDDraft(mxd, sdDraft, self.serverInfo['service_name'],
        "ARCGIS_SERVER", pubConnection, False, self.serverInfo["service_folder"], self.serverInfo['summary'], self.serverInfo['tags'])
        del mxd
        #now we need to change one tag in the draft to indicate this is a replacement service
        self.logger.logMessage(DEBUG,"reading back draft to parse xml")
        draftXml = etree.parse(sdDraft)
        typeNode = draftXml.xpath("/SVCManifest/Type")
        if typeNode and etree.iselement(typeNode[0]):
            self.logger.logMessage(DEBUG,"Found node to modify in draft xml")
            typeNode[0].text = "esriServiceDefinitionType_Replacement"
            with open(sdDraft,'w') as outfile:
                outfile.write(etree.tostring(draftXml, xml_declaration = False))
            #save backup for debug
            self.logger.logMessage(DEBUG,"saving backup draft")
            with open(sdDraft + '.bak', 'w') as bakfile:
                bakfile.write(etree.tostring(draftXml, xml_declaration = False))
        del typeNode, draftXml
        return sdDraft

    @errHandledWorkflowTask(taskName="Replace service")
    def replaceService(self, mxdname, sdDraft):
        """Creates SD, uploads to server"""
        pathToMapDoc = getConfigValue("pathtomapdoc")
        arcpy.env.workspace = pathToMapDoc
        pathToServiceDoc = arcpy.env.workspace + os.sep + "servicedefs"
        mxd = arcpy.mapping.MapDocument(pathToMapDoc + os.sep + mxdname)
        sdFile = pathToServiceDoc + os.sep + self.serverInfo['service_name'] + ".sd"
        if os.path.exists(sdFile):
            os.remove(sdFile)
        
        # Check for ERROR 001272: Analyzer errors were encountered (codes = 3, 3, 3, ...),
        # which in ArcCatalog is reported as "the base table definition string is invalid"
        # May be caused when map layers do not correspond to db entries.
        # Workaround: drop all non-base layers from the map if this error is encountered.
        try:
            arcpy.StageService_server(sdDraft)
        except Exception as err:
            if err[0].find('ERROR 001272') != -1 and err[0].find('codes = 3') != -1:
                self.logger.logMessage(WARN, "Encountered ERROR 001272, attempting workaround")

                # Only drop layers listed in entity table so we don't remove the base layer
                with cursorContext(self.logger) as cur:
                    cur.execute(
                        "SELECT layername FROM entity WHERE packageid LIKE %s", 
                        ('%' + mxdname.split('.')[0] + '%', )
                    )
                    entityLayerList = [row[0] for row in cur.fetchall() if row[0] is not None]

                # First drop all layers from the MXD file and save it
                layersFrame = arcpy.mapping.ListDataFrames(mxd, 'layers')[0]
                mapLayerObjectList = arcpy.mapping.ListLayers(mxd, '', layersFrame)
                mapLayerList = [layer.name.split('.')[-1] for layer in mapLayerObjectList]
                for layer in mapLayerList:
                    if layer in entityLayerList:
                        self.logger.logMessage(INFO, "Removing layer " + layer)
                        layerToRemove = mapLayerObjectList[mapLayerList.index(layer)]
                        arcpy.mapping.RemoveLayer(layersFrame, layerToRemove)
                    else:
                        self.logger.logMessage(INFO, "Skipping layer " + layer)
                mxd.save()
                del layersFrame

            # Try to stage the service again
            arcpy.StageService_server(sdDraft)                
        
        # by default, writes SD file to same loc as draft, then DELETES DRAFT        
        if os.path.exists(sdFile):
            arcpy.UploadServiceDefinition_server(in_sd_file = sdFile, in_server = pubConnection, in_startupType = 'STARTED')
        else:
            raise Exception("Staging failed to create %s" % (sdFile,))


    @errHandledWorkflowTask(taskName="Update layers table")
    def updateLayerIds(self, site):
        """Updates layer ids in search table with service info query"""
        # get list of layer names from service
        available = False
        tries = 0
        layerQueryURI = getConfigValue("layerqueryuri")
        layersUrl = layerQueryURI % (self.serverInfo["service_folder"], self.serverInfo["service_name"])
        layerInfoJson = urllib2.urlopen(layersUrl)
        layerInfo = json.loads(layerInfoJson.readline())
        del layerInfoJson
        available = "error" not in layerInfo
        # service might still be starting up
        while not available and tries < 10:
            time.sleep(5)
            tries += 1
            layerInfoJson = urllib2.urlopen(layersUrl)
            layerInfo = json.loads(layerInfoJson.readline())
            available = "error" not in layerInfo
        if not available:
            self.logger.logMessage(WARN, "Could not connect to %s" % (layersUrl,))
            return
        self.logger.logMessage(DEBUG, "service conn attempts %d" % (tries,))
        # make list of dict with just name and id of feature layers
        layers = [{'name':lyr["name"],'id':int(lyr['id'])} for lyr in layerInfo["layers"] if lyr["type"] == "Feature Layer"]
        arcloc = self.serverInfo["service_folder"] + "/" + self.serverInfo["service_name"]
        # shorten names that have db and schema in the name
        for lyr in layers:
            while lyr['name'].startswith("geonis."):
                lyr['name'] = lyr['name'][7:]
            lyr["scope"] = site
            lyr["arcloc"] = arcloc
        # update table, set arcloc field for layers that are newly added
        stmt = "UPDATE geonis_layer set arcloc = %s WHERE scope = %s AND (layerid = -1 OR layerid is null);"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt, (arcloc, site) )
        # update table with ids of layers for all layers (not just newly added)
        valObj = tuple(layers)
        stmt = "UPDATE geonis_layer set layerid = %(id)s WHERE scope = %(scope)s AND layername = %(name)s and arcloc = %(arcloc)s;"
        with cursorContext(self.logger) as cur:
            cur.executemany(stmt, valObj )


    @errHandledWorkflowTask(taskName="Send email report")
    def sendEmailReport(self):
        stmt = "SELECT DISTINCT * FROM errornotify;"
        with cursorContext(self.logger) as cur:
            cur.execute(stmt)
            rows = cur.fetchall()
        if rows:
            group = getConfigValue("emailgroup").split(';')
            for row in rows:
                pkgid, contact = row
                if contact is not None:
                    toList =[contact]
                else:
                    toList = []
                # Only send to jack@tinybike.net for testing!
                #toList += group
                toList = group
                self.logger.logMessage(INFO,"Mailing %s about %s." % (str(toList),pkgid))
                #bypass for testing, ignore contact
                sendEmail(group, composeMessage(pkgid))

    def execute(self, parameters, messages):
        super(RefreshMapService, self).execute(parameters, messages)
        mapServInfoString = getConfigValue("mapservinfo")
        mapServInfoItems = mapServInfoString.split(';')
        if len(mapServInfoItems) != 4:
            self.logger.logMessage(WARN,"Wrong number of items in map serv info: %s" % (mapServInfoString,))
            #maybe we have the name and folder
            mapServInfoItems = [mapServInfoItems[0],mapServInfoItems[1],"",""]
        mapServInfo = {'service_name':mapServInfoItems[0], 'service_folder':mapServInfoItems[1], 'tags':mapServInfoItems[2], 'summary':mapServInfoItems[3]}
        self.serverInfo = copy.copy(mapServInfo)
        try:

            # If execute has been called programatically, then only
            # refresh the specified services
            #if hasattr(self, 'calledFromScript'):
            #    mxds = [self.calledFromScript + '.mxd']

            # Otherwise, get list of map services where entity record
            # exists, is OK, has mxd, but not in geonis_layer
            #else:
            stmt = "SELECT * FROM vw_stalemapservices;"
            with cursorContext(self.logger) as cur:
                cur.execute(stmt)
                rows = cur.fetchall()
                mxds = [cols[0] for cols in rows]
            if hasattr(self, 'calledFromScript'):
                mxds.extend([s + '.mxd' for s in self.calledFromScript])
            del rows

            if not mxds:
                self.logger.logMessage(INFO, "No new vector data added to any maps.")
                #return
            for map in mxds:
                self.logger.logMessage(INFO, "Refreshing map service %s" % (map,))
                draft = self.draftSD(map)
                self.replaceService(map, draft)
                #delay for service to start, get layer info
                time.sleep(20)
                site = map.split('.')[0]
                self.updateLayerIds(site)
            if hasattr(self, 'sendReport') or self._isRunningAsTool:
                self.sendEmailReport()
        except Exception as err:
            self.logger.logMessage(ERROR, err.message)


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
toolclasses =  [Setup,
                QueryPasta,
                UnpackPackages,
                CheckSpatialData,
                LoadVectorTypes,
                LoadRasterTypes,
                UpdateMXDs,
                RefreshMapService ]
