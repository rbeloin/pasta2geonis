'''
Config data for pasta2geonis workflow

Created on Jan 28, 2013
Major mod on Apr 23, 2013 most of config info moved to database,
allowing a schema search path to determine test mode or production mode

@change: https://github.com/rbeloin/pasta2geonis

@author: Ron Beloin & Jack Peterson
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

# *********** Machine/mode dependent paths and values *************
if platform.node().lower() == "maps3":
    baseURL = "http://pasta.lternet.edu/package/eml"
    #DSN file
    #dsnfile = r"C:\pasta2geonis\sdeDSN.txt"
    #dsnfile = r"C:\pasta2geonis\geonisDSN.txt"
    dsnfile = r"C:\pasta2geonis\workflowDSN.txt"
    # smtp stuff
    smtpfile = r"C:\pasta2geonis\mailCred.txt"
    #publisher conn
    pubConnection = r"C:\pasta2geonis\Maps3.lternet.edu_6080(publisher).ags"
    #arcgis credentials for script admin of services
    arcgiscred = r"C:\pasta2geonis\arcgis_cred.txt"
    #path to env settings file. settings loaded by base execute method
    envSettingsPath = r"C:\pasta2geonis\savedEnv.xml"
    #path to stylesheets
    pathToStylesheets = r"C:\pasta2geonis\stylesheets"
    #raster data storage
    pathToRasterData = r"C:\pasta2geonis\Gis_data\Raster_raw"
    #raster mosaic datasets
    pathToRasterMosaicDatasets = r"C:\pasta2geonis\Gis_data\Raster_md.gdb"
    #geodatabase connection
    #geodatabase = r"C:\pasta2geonis\geonisOnMaps3.sde"
    geodatabase = r"Database Connections\Connection to Maps3.sde"
    #map doc
    pathToMapDoc = r"C:\pasta2geonis\Arcmap_mxd"
    #map service layer query
    layerQueryURI = "http://maps3.lternet.edu/arcgis/rest/services/%s/%s/MapServer/layers?f=json"
    #scratchWorkspace is NOT saved in settings
    scratchWS = r"C:\Temp"
    #db schema
    workflowSchema = "workflow_d"
    #map service info
    mapServInfo = {'service_name':"", 'service_folder':"Test", 'tags':"GEONIS",'summary':"Testing vector data map service."}
elif platform.node().lower() == "invent":
    #DSN file
    dsnfile = r"C:\pasta2geonis\geonisDSN.txt"
    # smtp stuff
    smtpfile = r"C:\pasta2geonis\mailCred.txt"
    #publisher conn
    pubConnection = r"C:\pasta2geonis\Maps3.lternet.edu_6080(publisher).ags"
    #arcgis credentials for script admin of services
    arcgiscred = r"C:\pasta2geonis\arcgis_cred.txt"
    #path to env settings file. settings loaded by base execute method
    envSettingsPath = r"C:\pasta2geonis\savedEnv.xml"
    #path to stylesheets
    pathToStylesheets = r"C:\pasta2geonis\stylesheets"
    #raster data storage
    pathToRasterData = r"C:\pasta2geonis\Gis_data\Raster_raw"
    #raster mosaic datasets
    pathToRasterMosaicDatasets = r"C:\pasta2geonis\Gis_data\Raster_md.gdb"
    #geodatabase connection
    geodatabase = r"C:\pasta2geonis\geonisOnMaps3.gdb"
    #map doc
    pathToMapDoc = r"C:\pasta2geonis\Arcmap_mxd"
    #map service layer query
    layerQueryURI = "http://maps3.lternet.edu/arcgis/rest/services/%s/%s/MapServer/layers?f=json"
    #scratchWorkspace is NOT saved in settings
    scratchWS = r"C:\TEMP\scratch"
    #db schema
    workflowSchema = "workflow_d"
    #map service info
    mapServInfo = {'service_name':"", 'service_folder':"Test", 'tags':"GEONIS",'summary':"Testing vector data map service."}
else:
    # dsn to postgresql running on mac host
    dsnfile = r"Z:\docs\local\git\pasta2geonis_sg\geonisDSN.txt"
    # smtp stuff
    smtpfile = r"Z:\docs\local\git\pasta2geonis_sg\mailCred.txt"
    #publisher conn is N/A on dev machine
    pubConnection = ""
##    #path to env settings file. settings loaded by base execute method
##    envSettingsPath = r"C:\Users\ron\Documents\geonis_tests\savedEnv.xml"
##    #file gdb for dev
##    geodatabase = r"C:\Users\ron\Documents\geonis_tests\geonis.gdb"
##    #metadata stylesheet
##    pathToStylesheets = r"Z:\docs\local\git\pasta2geonis_sg\stylesheets"
##    #raster data storage
##    pathToRasterData = r"C:\Users\ron\Documents\geonis_tests\raster_data"
##    #raster mosaic datasets
##    pathToRasterMosaicDatasets = r"C:\Users\ron\Documents\geonis_tests\raster_md.gdb"
##    #map doc
##    pathToMapDoc = r"Z:\docs\local"
##    #map service layer query
##    layerQueryURI = "http://maps3.lternet.edu/arcgis/rest/services/Test/VectorData/MapServer/layers?f=json"
##    #scratchWorkspace is NOT saved in settings
##    scratchWS = r"C:\Users\ron\AppData\Local\Temp"
##    #db schema
##    workflowSchema = "workflow"
##    #publisher conn
##    pubConnection = None
##    #map service info
##    mapServInfo = {'service_name':"VectorData",'service_folder':"Test",'tags':"GEONIS",'summary':"Testing vector data map service."}

class GeoNISDataType:
    """ 
    Members of this class serve as both enum type values for data types,
    and hold simple data for helper function to test for type.
    A full list of supported raster data types is at:
    http://resources.arcgis.com/en/help/main/10.1/index.html#//009t0000000q000000
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
    RST = ('.rst',) # IDRISI raster format
#class AllRasterTypes:
    IMG = ('.img',)
    MRSID = ('.sid', '.sdw')
    OVR = ('.ovr',)
    LGG = ('.lgg',)
    BAND = ('.bil', '.bip', '.bsq')
    BAG = ('.bag',)
    BT = ('.bt',)
    BMP = ('.bmp',)
    BSB = ('.bsb', '.cap', '.kap')
    RAW = ('.raw',)
    DTED = ('.dt0', '.dt1', '.dt2')
    ELAS = ('.elas',)
    ECW = ('.ecw',)
    FST = ('.fst',)
    ERS = ('.ers',)
    GIS = ('.gis',)
    LAN = ('.lan',)
    IGE = ('.ige',)
    STK = ('.stk',)
    SDF = ('.sdf',)
    FLT = ('.flt',)
    VRT = ('.vrt',)
    GRD = ('.grd',)
    GIF = ('.gif',)
    GRB = ('.grb',)
    GXF = ('.gxf',)
    HDF = ('.hdf', '.h5', '.hdf5')
    HF = ('.hf2',)
    HGT = ('.hgt',)
    CUB = ('.cub',)
    MPR = ('.mpr',)
    CIT = ('.cit',)
    COT = ('.cot',)
    JAXA = ('.5gud', '.1__a')
    JPEG2000 = ('.jp2', '.j2c', '.j2k', '.jpx')
    BLXXLB = ('.blx', '.xlb')
    MAP = ('.map',)
    NTF = ('.ntf',)
    NOAAPOD = ('.1b', '.sv', '.gc')
    AUX = ('.aux',)
    PIX = ('.pix',)
    PERSONALGEODB = ('.mdb',)
    LBL = ('.lbl',)
    PNG = ('.png',)
    GFF = ('.gff',)
    SAGA = ('.sdat', '.sgrd')
    HGT = ('.hgt',)
    DDF = ('.ddf',)
    TERRAIN = ('.ter', '.terrain')
    GTX = ('.gtx',)
    DEM = ('.dem',)
    DOQ = ('.doq', '.nes', '.nws', '.ses', '.sws')
    XPM = ('.xpm',)