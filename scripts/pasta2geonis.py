#!/usr/bin/env python
"""
Testing script for pasta2geonis that runs outside of ArcCatalog.

(c) Jack Peterson (jack@tinybike.net), 6/29/2013
"""
import os
import sys
import getopt
import lno_geonis_wf

# Command line parameters: staging server, scope, id, setup, model
# e.g. python pasta2geonis.py pasta knz 230 run-setup run-model
verbose = True
logfile = "C:\\TEMP\\geonis_wf.log"
testing_workflow = True
staging_server = True
cleanup = True
Directory_of_Packages = "C:\\TEMP\\pasta_pkg_test"
valid_pkg_test = "C:\\TEMP\\valid_pkg_test"

try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        'hp:s:i:SMRO',
        ['run-setup', 'run-model', 'refresh-map-service', 'run-setup-only']
    )
except getopt.GetoptError:
    print "pasta2geonis.py -p <pasta or pasta-s> -s <site> -i <id>"
    sys.exit(2)

print opts
if '-p' not in opts or '-s' not in opts or '-i' not in opts:
    print ("Error: you must specify a pasta server name, "
           "site code (or * for all), and ID (or * for all).")
    print "pasta2geonis.py -p <pasta or pasta-s> -s <site> -i <id>"
    sys.exit(2)

run_setup_arg, run_model_arg, rfm_only_arg, rso_arg = False, False, False, False
for opt, arg in opts:
    if opt == '-h':
        print "pasta2geonis.py -p <pasta or pasta-s> -s <site> -i <id>"
        sys.exit()
    elif opt == '-p':
        if arg.lower() == 'pasta':
            staging_server = False
        elif arg.lower() == 'pasta-s':
            staging_server = True
        else:
            print "Error: pasta server", arg, "not recognized."
            print "pasta2geonis.py -p <pasta or pasta-s> -s <site> -i <id>"
            sys.exit(2)
    elif opt == '-s':
        site_code = arg
    elif opt == '-i':
        data_id = arg
    elif opt in ('-S', '--run-setup'):
        run_setup_arg = True
    elif opt in ('-M', '--run-model'):
        run_model_arg = True
    elif opt in ('-R', '--refresh-map-service'):
        rfm_only_arg = True
    elif opt in ('-O', '--run-setup-only'):
        rso_arg = True
    else:
        print "Error: command line parameter", opt, "not recognized."
        print "pasta2geonis.py -p <pasta or pasta-s> -s <site> -i <id>"
        sys.exit(2)

# Refresh map service only
if rfm_only_arg:
    print "Refreshing map services only"
    RMS = lno_geonis_wf.RefreshMapService()
    RMS._isRunningAsTool = False
    paramsRMS = RMS.getParameterInfo()
    paramsRMS[0].value = True
    paramsRMS[1].value = logfile
    if site_code != '*' and data_id != 'all':
        RMS.calledFromScript = site_code
    #RMS.sendReport = True
    RMS.execute(paramsRMS, [])
    sys.exit("Refreshed map services, exiting.")

# Setup
run_setup = 'Y' if run_setup_arg else raw_input("Run Setup? [Y/n] ")
if run_setup.lower() != 'n':
    print "************"
    tool = lno_geonis_wf.Setup()
    tool._isRunningAsTool = False
    tool.setScopeIdManually = True
    tool.scope = site_code
    tool.id = data_id
    params = tool.getParameterInfo()
    params[0].value = verbose
    params[1].value = logfile
    params[2].value = testing_workflow
    params[3].value = staging_server
    params[4].value = [[tool.scope, tool.id]]  # this doesn't work; set value manually instead
    params[5].value = cleanup
    tool.execute(params, [])
    print "Setup complete."
    if rso_arg:
        sys.exit()

run_model = 'Y' if run_model_arg else raw_input("Run model? [Y/n] ")
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
    print "************"
    RMS = lno_geonis_wf.RefreshMapService()
    RMS._isRunningAsTool = False
    paramsRMS = RMS.getParameterInfo()
    paramsRMS[0].value = True
    paramsRMS[1].value = logfile
    if site_code != '*' and data_id != 'all':
        RMS.calledFromScript = site_code
    #RMS.sendReport = True
    RMS.execute(paramsRMS, [])
