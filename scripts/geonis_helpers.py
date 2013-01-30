'''
Created on Jan 28, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import os
from geonis_pyconfig import GeoNISDataType
from functools import partial

def fileExtensionMatch(extensions, pathToFile):
    name, ext = os.path.splitext(pathToFile)
    return (ext != '' and ext.lower() in extensions)

'''
File extension enough to identify a spatial data file
'''
isShapefile = partial(fileExtensionMatch, GeoNISDataType.SHAPEFILE)
isKML = partial(fileExtensionMatch, GeoNISDataType.KML)
isTif = partial(fileExtensionMatch, GeoNISDataType.TIF)
isTifWorld = partial(fileExtensionMatch, GeoNISDataType.TFW)
isJpeg = partial(fileExtensionMatch, GeoNISDataType.JPEG)
isJpegWorld = partial(fileExtensionMatch, GeoNISDataType.JPGW)
isEsriE00 = partial(fileExtensionMatch, GeoNISDataType.ESRIE00)

'''
Bit more work needed for some
'''
def isFileGDB(path):
    '''Returns True if directory ending with ".gdb" '''
    return (os.path.isdir(path) and path[-4:] == '.gdb')

def isASCIIRaster(pathToFile):
    ''' Checks for ascii file extension, peeks at first two lines comparing
    to what is expected for an ASCII raster '''
    if fileExtensionMatch(GeoNISDataType.ASCIIRASTER, pathToFile):
        with open(pathToFile, 'r') as txtfile:
            line1 = txtfile.readline(64)
            line2 = txtfile.readline(64)
        return (len(line1) > 6 and line1[:5] == 'ncols' and len(line2) > 6 and line2[:5] == 'nrows')


