#!/usr/bin/env python
"""
Testing script for pasta2geonis that runs outside of ArcCatalog.

(c) Jack Peterson (jack@tinybike.net), 6/29/2013
"""
import os
import sys
from getopt import getopt, GetoptError
from urllib2 import urlopen
import lno_geonis_wf
from geonis_postgresql import getConfigValue
# Is RFM picking up specified service, or not b/c in vw_stalemapservices?


def parse_parameters(argv, parameters):
    usage = "Usage: pasta2geonis.py -p <pasta or pasta-s> -s <site> -i <id>"
    argv = [j for j in argv if not j.endswith('.py') and not j.endswith('.pyc')]
    try:
        opts, args = getopt(
            argv,
            'hp:s:i:SMRO',
            ['run-setup', 'run-model', 'refresh-map-service', 'run-setup-only']
        )
    except GetoptError:
        print usage
        sys.exit(2)
    optlist = [j[0] for j in opts]
    if '-s' not in optlist or '-i' not in optlist:
        print "Error: you must specify a site code (or * for all) and ID (or * for all)."
        print usage
        sys.exit(2)
    if '-p' not in optlist:
        print "Warning: no pasta server specified, defaulting to pasta-s.lternet.edu"
        parameters['staging_server'] = True
    for key in ('run_setup_arg', 'run_model_arg', 'rfm_only_arg', 'rso_arg'):
        parameters[key] = False
    for opt, arg in opts:
        if opt == '-h':
            print "pasta2geonis.py -p <pasta or pasta-s> -s <site> -i <id>"
            sys.exit()
        elif opt == '-p':
            if arg.lower() == 'pasta':
                parameters['staging_server'] = False
            elif arg.lower() == 'pasta-s':
                parameters['staging_server'] = True
            else:
                print "Error: pasta server", arg, "not recognized."
                print usage
                sys.exit(2)
        elif opt == '-s':
            parameters['site'] = arg
        elif opt == '-i':
            parameters['id'] = arg
        elif opt in ('-S', '--run-setup'):
            parameters['run_setup_arg'] = True
        elif opt in ('-M', '--run-model'):
            parameters['run_model_arg'] = True
        elif opt in ('-R', '--refresh-map-service'):
            parameters['rfm_only_arg'] = True
        elif opt in ('-O', '--run-setup-only'):
            parameters['rso_arg'] = True
        else:
            print "Error: command line parameter", opt, "not recognized."
            print usage
            sys.exit(2)
    return parameters


def refresh_map_service(parameters):
    print "************"
    tool = lno_geonis_wf.RefreshMapService()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = parameters['logfile']
    if parameters['site'] not in ('*', 'all'):
        tool.calledFromScript = [parameters['site']]
    elif parameters['site'] in ('*', 'all'):
        tool.calledFromScript = [
            s.split('-')[-1] for s in urlopen(
                getConfigValue('pastaurl') + '/package/eml'
            ).read().split('\n') if s.startswith('knb-lter-')
        ]
    #tool.sendReport = True
    tool.execute(params, [])


def setup(parameters):
    print "************"
    tool = lno_geonis_wf.Setup()
    tool._isRunningAsTool = False
    tool.setScopeIdManually = True
    tool.scope = parameters['site']
    tool.id = parameters['id']
    params = tool.getParameterInfo()
    params[0].value = parameters['verbose']
    params[1].value = parameters['logfile']
    params[2].value = parameters['testing_workflow']
    params[3].value = parameters['staging_server']
    params[4].value = None
    params[5].value = parameters['cleanup']
    tool.execute(params, [])
    print "Setup complete."


def query_pasta(parameters):
    print "************"
    tool = lno_geonis_wf.QueryPasta()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = parameters['verbose']
    params[1].value = parameters['logfile']
    params[2].value = parameters['package_directory']
    tool.execute(params, [])


def unpack_packages(parameters):
    print "************"
    tool = lno_geonis_wf.UnpackPackages()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = parameters['verbose']
    params[1].value = parameters['logfile']
    params[2].value = parameters['package_directory']
    params[3].value = parameters['valid_pkg_test']
    tool.execute(params, [])


def check_spatial_data(parameters):
    print "************"
    pkg_subdirs = os.listdir(parameters['valid_pkg_test'])
    if len(pkg_subdirs) > 1:
        parameters['input_dirs'] = [parameters['valid_pkg_test'] + os.sep + d for d in os.listdir(parameters['valid_pkg_test'])[1:]]
    else:
        parameters['input_dirs'] = [parameters['valid_pkg_test'] + os.sep + d for d in os.listdir(parameters['valid_pkg_test'])]
    tool = lno_geonis_wf.CheckSpatialData()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = parameters['verbose']
    params[1].value = parameters['logfile']
    params[2].value = parameters['input_dirs']
    tool.execute(params, [])
    return parameters


def load_vector_types(parameters):
    print "************"
    tool = lno_geonis_wf.LoadVectorTypes()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = parameters['logfile']
    params[2].value = parameters['input_dirs']
    tool.execute(params, [])


def load_raster_types(parameters):
    print "************"
    tool = lno_geonis_wf.LoadRasterTypes()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = parameters['logfile']
    params[2].value = parameters['input_dirs']
    tool.execute(params, [])


def update_mxds(parameters):
    print "************"
    tool = lno_geonis_wf.UpdateMXDs()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = parameters['logfile']
    params[2].value = parameters['input_dirs']
    tool.execute(params, [])


def main(argv):
    parameters = {
        'verbose': True,
        'logfile': "C:\\TEMP\\geonis_wf.log",
        'testing_workflow': True,
        'cleanup': True,
        'package_directory': "C:\\TEMP\\pasta_pkg_test",
        'valid_pkg_test': "C:\\TEMP\\valid_pkg_test",
    }

    # Parse command line parameters and add them to our dict
    parameters = parse_parameters(argv, parameters)

    # Refresh map service only
    if parameters['rfm_only_arg']:
        print "Refreshing map services only"
        refresh_map_service(parameters)
        sys.exit("Refreshed map services, exiting.")

    # Run the setup tool (if requested)
    run_setup = 'Y' if parameters['run_setup_arg'] else raw_input("Run Setup? [Y/n] ")
    if run_setup.lower() != 'n':
        setup(parameters)
        if parameters['rso_arg']:
            sys.exit()

    # Run the model (if requested)
    run_model = 'Y' if parameters['run_model_arg'] else raw_input("Run model? [Y/n] ")
    if run_model.lower() != 'n':
        unpack_packages(parameters)
        parameters = check_spatial_data(parameters)
        load_vector_types(parameters)
        load_raster_types(parameters)
        update_mxds(parameters)
        refresh_map_service(parameters)

if __name__ == '__main__':
    main(sys.argv[1:])
