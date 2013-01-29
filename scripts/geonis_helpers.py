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

isShapefile = partial(fileExtensionMatch, GeoNISDataType.SHAPEFILE)
isKML = partial(fileExtensionMatch, GeoNISDataType.KML)
isTif = partial(fileExtensionMatch, GeoNISDataType.TIF)

