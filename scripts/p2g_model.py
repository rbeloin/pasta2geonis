#!/usr/bin/env python
"""
Testing script for pasta2geonis that runs outside of ArcCatalog.

(c) Jack Peterson (jack@tinybike.net), 6/29/2013
"""

# Import arcpy module
import os, sys
import arcpy
from arcpy import Parameter
import lno_geonis_wf
from geonis_pyconfig import envSettingsPath, scratchWS
import pdb

# Local variables:
valid_pkg_test = "C:\\TEMP\\valid_pkg_test"
logfile = "C:\\TEMP\\geonis_wf.log"
#logfile = None
verbose = True
Directory_of_Packages = "C:\\TEMP\\pasta_pkg_test"

print "************"

tool = lno_geonis_wf.Setup()
tool._isRunningAsTool = False
params = tool.getParameterInfo()
params[0].value = verbose # verbose
params[1].value = logfile # logfile
params[2].value = True # testing workflow (workflow_d schema)
params[3].value = False # staging server (pasta-s)
params[4].value = [[u'knz', u'230']] # this doesn't work; set value manually instead
params[5].value = True # cleanup
tool.execute(params, [])

print "************"

tool = lno_geonis_wf.QueryPasta()
tool._isRunningAsTool = False
params = tool.getParameterInfo()
params[0].value = verbose
params[1].value = logfile
params[2].value = Directory_of_Packages
tool.execute(params, [])

print "************"

tool = lno_geonis_wf.UnpackPackages()
tool._isRunningAsTool = False
params = tool.getParameterInfo()
params[0].value = verbose
params[1].value = logfile
params[2].value = Directory_of_Packages
params[3].value = valid_pkg_test
tool.execute(params, [])

print "************"

input_dirs = [valid_pkg_test + os.sep + d for d in os.listdir(valid_pkg_test)[1:]]
tool = lno_geonis_wf.CheckSpatialData()
tool._isRunningAsTool = False
params = tool.getParameterInfo()
params[0].value = verbose
params[1].value = logfile
params[2].value = input_dirs
tool.execute(params, [])

print "************"

tool = lno_geonis_wf.LoadVectorTypes()
tool._isRunningAsTool = False
params = tool.getParameterInfo()
params[0].value = True
params[1].value = logfile
params[2].value = input_dirs
tool.execute(params, [])

print "************"

tool = lno_geonis_wf.LoadRasterTypes()
tool._isRunningAsTool = False
params = tool.getParameterInfo()
params[0].value = True
params[1].value = logfile
params[2].value = ""
tool.execute(params, [])

print "************"

tool = lno_geonis_wf.UpdateMXDs()
tool._isRunningAsTool = False
params = tool.getParameterInfo()
params[0].value = True
params[1].value = logfile
params[2].value = ""
tool.execute(params, [])
