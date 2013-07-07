#!/usr/bin/env python
"""
Testing script for pasta2geonis that runs outside of ArcCatalog.

(c) Jack Peterson (jack@tinybike.net), 6/29/2013
"""
import os, sys
import arcpy
from arcpy import Parameter
import lno_geonis_wf
from geonis_pyconfig import envSettingsPath, scratchWS
import pdb
from pprint import pprint

# Command line parameters: staging server, scope, id, setup, model
# e.g. python p2g_model.py 1 knz 230 1 1
verbose = True
logfile = "C:\\TEMP\\geonis_wf.log"
testing_workflow = True
staging_server = True if len(sys.argv) > 1 and sys.argv[1] == 'pasta-s' else False
cleanup = True
Directory_of_Packages = "C:\\TEMP\\pasta_pkg_test"
valid_pkg_test = "C:\\TEMP\\valid_pkg_test"

# Setup
run_setup = 'Y' if len(sys.argv) > 4 and sys.argv[4] == 'run-setup' \
    else raw_input("Run Setup? [Y/n] ")
if run_setup.lower() != 'n':
    print "************"
    tool = lno_geonis_wf.Setup()
    tool._isRunningAsTool = False
    tool.setScopeIdManually = True
    tool.scope = sys.argv[2]
    tool.id = sys.argv[3]
    params = tool.getParameterInfo()
    params[0].value = verbose
    params[1].value = logfile
    params[2].value = testing_workflow
    params[3].value = staging_server
    params[4].value = [[tool.scope, tool.id]] # this doesn't work; set value manually instead
    params[5].value = cleanup
    tool.execute(params, [])

run_model = 'Y' if len(sys.argv) > 5 and sys.argv[5] == 'run-model' \
    else raw_input("Run model? [Y/n] ")
if run_model.lower() != 'n':

    # QueryPasta
    print "************"
    tool = lno_geonis_wf.QueryPasta()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = verbose
    params[1].value = logfile
    params[2].value = Directory_of_Packages
    tool.execute(params, [])

    # UnpackPackages
    print "************"
    tool = lno_geonis_wf.UnpackPackages()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = verbose
    params[1].value = logfile
    params[2].value = Directory_of_Packages
    params[3].value = valid_pkg_test
    tool.execute(params, [])

    # CheckSpatialData
    print "************"
    pkg_subdirs = os.listdir(valid_pkg_test)
    if len(pkg_subdirs) > 1:
        input_dirs = [valid_pkg_test + os.sep + d for d in os.listdir(valid_pkg_test)[1:]]
    else:
        input_dirs = [valid_pkg_test + os.sep + d for d in os.listdir(valid_pkg_test)]
    tool = lno_geonis_wf.CheckSpatialData()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = verbose
    params[1].value = logfile
    params[2].value = input_dirs
    tool.execute(params, [])

    # LoadVectorTypes
    print "************"
    tool = lno_geonis_wf.LoadVectorTypes()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = logfile
    params[2].value = input_dirs
    tool.execute(params, [])

    # LoadRasterTypes
    print "************"
    tool = lno_geonis_wf.LoadRasterTypes()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = logfile
    params[2].value = input_dirs
    tool.execute(params, [])

    # UpdateMXDs
    print "************"
    tool = lno_geonis_wf.UpdateMXDs()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = logfile
    params[2].value = input_dirs
    tool.execute(params, [])
        
    # RefreshMapService
    try:
        print "************"
        RMS = lno_geonis_wf.RefreshMapService()
        RMS._isRunningAsTool = False
        paramsRMS = RMS.getParameterInfo()
        paramsRMS[0].value = True
        paramsRMS[1].value = logfile
        if len(sys.argv) > 2 and sys.argv[2] != '*' and sys.argv[2] != 'all':
            RMS.calledFromScript = sys.argv[2]
        RMS.execute(paramsRMS, [])
    except:
        e = sys.exc_info()[0]
        self.logger.logMessage(WARN, "Map service refresh encountered an error: " + e)