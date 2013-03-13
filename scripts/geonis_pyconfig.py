'''
Config data for pasta2geonis workflow

Created on Jan 28, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import platform
from logging import DEBUG, INFO, WARN

defaultLoggingLevel = INFO
#set the default value for the verbose switch for each tool. Verbose forces DEBUG logging
defaultVerboseValue = True
#set name of metadata temp file used in workflow
tempMetadataFilename = "temp_meta.data"

# *********** Machine dependent paths *************
if platform.node() == "Maps3":
    #path to env settings file. settings loaded by base execute method
    envSettingsPath = r"C:\pasta2geonis\savedEnv.xml"
    #path to stylesheets
    pathToStylesheets = r"C:\pasta2geonis\stylesheets"
    #raster data storage
    pathToRasterData = r"C:\pasta2geonis\Gis_data\Raster_raw"
    #raster mosaic datasets
    pathToRasterMosaicDatasets = r"C:\pasta2geonis\Gis_data\Raster_md.gdb"
    #geodatabase connection
    geodatabase = r"C:\pasta2geonis\geonisOnMaps3.sde"
    #DSN file
    dsnfile = r"C:\pasta2geonis\geonisDSN.txt"
    #map doc
    pathToMapDoc = r"C:\pasta2geonis\Arcmap_mxd\MapTest.mxd"
    #map service layer query
    layerQueryURI = "http://maps3.lternet.edu/arcgis/rest/services/Test/VectorData/MapServer/layers?f=json"
    #scratchWorkspace is NOT saved in settings
    scratchWS = r"C:\Temp"
    #publisher conn
    pubConnection = r"C:\pasta2geonis\Maps3.lternet.edu_6080(publisher).ags"
    #map service info
    mapServInfo = {'service_name':"VectorData",'tags':"GEONIS",'summary':"Testing vector data map service."}
else:
    #path to env settings file. settings loaded by base execute method
    envSettingsPath = r"C:\Users\ron\Documents\geonis_tests\savedEnv.xml"
    #file gdb for dev
    geodatabase = r"C:\Users\ron\Documents\geonis_tests\geonis.gdb"
    #metadata stylesheet
    pathToStylesheets = r"Z:\docs\local\git\pasta2geonis_sg\stylesheets"
    #raster data storage
    pathToRasterData = r"C:\Users\ron\Documents\geonis_tests\raster_data"
    #raster mosaic datasets
    pathToRasterMosaicDatasets = r"C:\Users\ron\Documents\geonis_tests\raster_md.gdb"
    #no dsn
    dsnfile = r"Z:\docs\local\git\pasta2geonis_sg\geonisDSN.txt"
    #map doc
    pathToMapDoc = r"Z:\docs\local\mapserve.mxd"
    #map service layer query
    layerQueryURI = "http://maps3.lternet.edu/arcgis/rest/services/Test/VectorData/MapServer/layers?f=json"
    #scratchWorkspace is NOT saved in settings
    scratchWS = r"C:\Users\ron\AppData\Local\Temp"
    #publisher conn
    pubConnection = None
    #map service info
    mapServInfo = {'service_name':"VectorData",'tags':"GEONIS",'summary':"Testing vector data map service."}

class GeoNISDataType:
    """ members of this class serve as both enum type values for data types,
        and hold simple data for helper function to test for type
    """
    NA = object() # not acceptable type
    SPATIALVECTOR = ('any vector',) # for expected type, from EML
    SPATIALRASTER = ('any raster',) # for expected type, from EML
    SHAPEFILE = ('.shp',)
    KML = ('.kml', '.kmz')
    TIF = ('.tif', '.tiff', '.tff')
    TFW = ('.tfw',)
    FILEGEODB = ('.gdb',)
    ASCIIRASTER = ('.txt', '.asc')
    JPEG = ('.jpg', '.jpeg', '.jpc', '.jpe')
    JPGW = ('.jgw',)
    ESRIE00 = ('.e00',)
    PRJ = ('.prj',)


