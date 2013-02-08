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

def testChain():
    mytoolspath = arcpy.gp.getMyToolboxesPath()
    toolname = r"GeoNIS PASTA Processing.pyt"
    toolbox = os.path.join(mytoolspath, toolname )
    arcpy.ImportToolbox(toolbox)

    send_msgs = True
    logfilepath = None # r"C:\Users\ron\Documents\geonis_tests\wf.log"
    in_dir = r"C:\Users\ron\Documents\geonis_tests\newpackages"

    try:
        # ideally we shouldn't hit most exceptions because they are handled in the code
        # but fatal exceptions will be caught here
        result = arcpy.UnpackPackages_geonis (send_msgs, logfilepath, in_dir)
        result2 = arcpy.CheckSpatialData_geonis(send_msgs, logfilepath, result)
        #result3 = arcpy.GatherMetadata_geonis(send_msgs, logfilepath, result2)
        print result2.getOutput(0)
        print result2.getOutput(1)
    except arcpy.ExecuteError:
        print arcpy.GetMessages(2)
    except Exception as e:
        print e.message


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
    except Exception as e:
        print e.message


    """
    Tools as standalone classes can be run, but output will not be set
    and there may be other subtle differences when running as a tool.
    However, the code can be stepped through, so this is useful.
    """

def testUnpack():
    unpack = lno_geonis_wf.UnpackPackages()
    unpack._isRunningAsTool = False
    params = unpack.getParameterInfo()
    params[0].value = True
    params[1].value = None #r"C:\Users\ron\Documents\geonis_tests\wf.log"
    params[2].value = r"Z:\docs\local\geonis_testdata\downloaded_pkgs"
    params[3].value = r"Z:\docs\local\geonis_testdata\pkgs"
    params[4].value = None
    unpack.execute(params,[])
    print params[4].value

def testCheckData():
    tool = lno_geonis_wf.CheckSpatialData()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = None #r"C:\Users\ron\Documents\geonis_tests\wf.log"
    params[2].value = r"Z:\docs\local\geonis_testdata\pkgs\knb-lter-rmb.1.1"
    params[3].value = None
    tool.execute(params,[])
    print params[3].value
    print params[4].value

def testLoadVector():
    tool = lno_geonis_wf.LoadVectorTypes()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = None #r"C:\Users\ron\Documents\geonis_tests\wf.log"
    params[2].value = r"Z:\docs\local\geonis_testdata\pkgs\knb-lter-rmb.1.1;Z:\docs\local\geonis_testdata\pkgs\knb-lter-tjv.2.1"
    params[3].value = None
    tool.execute(params,[])
    print params[3].value



if __name__ == '__main__':
    #testUnpack()
    #testCheckData()
    testLoadVector()
    #testUnpackAsTool()
    #testChain()
