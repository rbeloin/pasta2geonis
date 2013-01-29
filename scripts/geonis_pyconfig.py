'''
Config data for pasta2geonis workflow

Created on Jan 28, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
from logging import DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL

defaultLoggingLevel = INFO
 #set the default value for the verbose switch for each tool. Verbose forces DEBUG logging
defaultVerboseValue = True

class GeoNISDataType:
    """ members of this class serve as both enum type values for data types,
        and hold simple data for helper function to test for type
    """
    NA = object() # not acceptable type
    SHAPEFILE = ('.shp',)
    KML = ('.kml','.kmz')
    TIF = ('.tif','.tiff')


