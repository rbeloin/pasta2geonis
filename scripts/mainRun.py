'''
Created on Jan 15, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import os, sys
import arcpy
from arcpy import Parameter
import lno_geonis_wf


def testUnpack():
    unpack = lno_geonis_wf.UnpackPackages()
    tool._isRunningAsTool = False
    params = unpack.getParameterInfo()
    params[0].value = True
    params[1].value = None #r"C:\Users\ron\Documents\geonis_tests\wf.log"
    params[2].value = r"C:\Users\ron\Documents\geonis_tests\newpackages"
    params[3].value = None
    unpack.execute(params,[])
    print params[3].value

def testUnpackAsTool():
    mytoolspath = arcpy.gp.getMyToolboxesPath()
    toolname = r"GeoNIS PASTA Processing.pyt"
    toolbox = os.path.join(mytoolspath, toolname )
    arcpy.ImportToolbox(toolbox)

    send_msgs = True
    logfilepath = None # r"C:\Users\ron\Documents\geonis_tests\wf.log"
    in_dir = r"C:\Users\ron\Documents\geonis_tests\newpackages"

    try:
        result = arcpy.UnpackPackages_geonis (send_msgs, logfilepath, in_dir)
        print result
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.message


def testCheckData():
    tool = lno_geonis_wf.CheckSpatialData()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = None #r"C:\Users\ron\Documents\geonis_tests\wf.log"
    params[2].value = r"C:\Users\ron\Documents\geonis_tests\workflow_dirs\pkg_0;C:\Users\ron\Documents\geonis_tests\workflow_dirs\pkg_1;C:\Users\ron\Documents\geonis_tests\workflow_dirs\pkg_2"
    params[3].value = None
    tool.execute(params,[])
    print params[3].value

def testMetadata():
    tool = lno_geonis_wf.CreateMetadata()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = None #r"C:\Users\ron\Documents\geonis_tests\wf.log"
    params[2].value = r"C:\Users\ron\Documents\geonis_tests\workflow_dirs\pkg_0;C:\Users\ron\Documents\geonis_tests\workflow_dirs\pkg_1;C:\Users\ron\Documents\geonis_tests\workflow_dirs\pkg_2"
    params[3].value = None
    tool.execute(params,[])
    print params[3].value


if __name__ == '__main__':
    #testUnpack()
   # testCheckData()
    #testMetadata()
    testUnpackAsTool()
