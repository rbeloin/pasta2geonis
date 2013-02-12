'''
Config data for pasta2geonis workflow

Created on Jan 28, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
from logging import DEBUG, INFO, WARN

defaultLoggingLevel = INFO
#set the default value for the verbose switch for each tool. Verbose forces DEBUG logging
defaultVerboseValue = True
#set name of metadata temp file used in workflow
tempMetadataFilename = "temp_meta.data"
#path to env settings file. settings loaded by base execute method
envSettingsPath = r"C:\Users\ron\Documents\geonis_tests\savedEnv.xml"
#file gdb for dev
myFileGDB = r"C:\Users\ron\Documents\geonis_tests\geonis.gdb"
#metadata stylesheet
pathToMetadataMerge = r"Z:\docs\local\git\pasta2geonis_sg\metadataMerge.xsl"
#raster data storage
pathToRasterData = r"C:\Users\ron\Documents\geonis_tests\raster_data"
#raster mosaic datasets
pathToRasterMosaicDatasets = r"C:\Users\ron\Documents\geonis_tests\raster_mosaic_ds.gdb"

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


