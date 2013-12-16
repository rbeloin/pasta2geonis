#!/usr/bin/env python
"""
Script to run the pasta2geonis workflow outside of ArcCatalog.

(c) Jack Peterson (jack@tinybike.net), 6/29/2013
"""
import sys
from getopt import getopt, GetoptError
from urllib2 import urlopen
import lno_geonis_wf
from geonis_postgresql import getConfigValue

def parse_parameters(argv, parameters):
    usage = "Usage: pasta2geonis.py -p <pasta or pasta-s> -s <site> -i <id>"
    argv = [j for j in argv if not j.endswith('.py') and not j.endswith('.pyc')]
    try:
        opts, args = getopt(
            argv,
            'hp:s:i:SMROf:',
            ['run-setup', 'run-model', 'refresh-map-service', 'run-setup-only', 'flush=', 'test']
        )
    except GetoptError:
        print usage
        sys.exit(2)
    optlist = [j[0] for j in opts]
    if '-p' not in optlist:
        print "Warning: no pasta server specified, defaulting to pasta-s.lternet.edu"
        parameters['staging_server'] = True
    else:
        for opt, arg in opts:
            if opt == '-p':
                if arg.lower() == 'pasta':
                    parameters['staging_server'] = False
                    print "Fetching from live server (pasta.lternet.edu)"
                elif arg.lower() == 'pasta-s':
                    parameters['staging_server'] = True
                    print "Fetching from staging server (pasta-s.lternet.edu)"
                else:
                    print "Error: pasta server", arg, "not recognized."
                    print usage
                    sys.exit(2)
    parameters['testing_workflow'] = False
    for opt, arg in opts:
        if opt == '-h':
            print usage
            sys.exit()
        if opt in ('-f', '--flush'):
            parameters['flush'] = arg
            parameters['site'] = arg
            parameters['id'] = '*'
            return parameters
        if opt == 'test':
            print "Workflow: TESTING"
            parameters['testing_workflow'] = True
    if not parameters['testing_workflow']:
        print "Workflow: PRODUCTION"
    if '-s' not in optlist or '-i' not in optlist:
        print "Error: you must specify a site code (or * for all) and ID (or * for all)."
        print usage
        sys.exit(2)
    for key in ('run_setup_arg', 'run_model_arg', 'rfm_only_arg', 'rso_arg', 'flush'):
        parameters[key] = False
    for opt, arg in opts:
        if opt == '-s':
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
    return parameters


def refresh_map_service(parameters):
    print "************"
    tool = lno_geonis_wf.RefreshMapService()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = True
    params[1].value = parameters['logfile']
    if parameters['site'] not in ('*', 'all'):
        tool.calledFromScript = parameters['site']
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
    if parameters['site'] == 'standard-test':
        tool.scope = '*'
        tool.whitelist = set(('and', 'nwt', 'ntl', 'cap', 'bnz', 'knz', 'pie'))
    else:
        tool.scope = parameters['site']
    tool.id = parameters['id']
    tool.flush = parameters['flush']
    params = tool.getParameterInfo()
    params[0].value = parameters['verbose']
    params[1].value = parameters['logfile']
    params[2].value = parameters['testing_workflow']
    params[3].value = parameters['staging_server']
    params[4].value = None
    params[5].value = parameters['cleanup']
    tool.execute(params, [])
    if tool.flush is True:
        sys.exit("Flush complete.")
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
    parameters['package_directory'] = tool.packageDir
    return parameters


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
    parameters['input_dirs'] = tool.inputDirList
    return parameters


def check_spatial_data(parameters):
    print "************"
    tool = lno_geonis_wf.CheckSpatialData()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = parameters['verbose']
    params[1].value = parameters['logfile']
    params[2].value = parameters['input_dirs']
    tool.execute(params, [])
    parameters['input_dirs'] = tool.inputDirsParameter
    parameters['output_dirs'] = tool.outputDirsParameter
    return parameters


def load_vector_types(parameters):
    print "************"
    tool = lno_geonis_wf.LoadVectorTypes()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = parameters['verbose']
    params[1].value = parameters['logfile']
    params[2].value = parameters['input_dirs']
    params[3].value = parameters['output_dirs']
    tool.execute(params, [])


def load_raster_types(parameters):
    print "************"
    tool = lno_geonis_wf.LoadRasterTypes()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = parameters['verbose']
    params[1].value = parameters['logfile']
    params[2].value = parameters['input_dirs']
    tool.execute(params, [])


def update_mxds(parameters):
    print "************"
    tool = lno_geonis_wf.UpdateMXDs()
    tool._isRunningAsTool = False
    params = tool.getParameterInfo()
    params[0].value = parameters['verbose']
    params[1].value = parameters['logfile']
    params[2].value = parameters['input_dirs']
    tool.execute(params, [])


def main(argv):
    parameters = {
        'verbose': True,
        'logfile': "C:\\TEMP\\geonis_wf.log",
        'cleanup': True,
        'package_directory': "C:\\TEMP\\pasta_pkg",
        'valid_pkg_test': "C:\\TEMP\\valid_pkg",
    }

    # Parse command line parameters and add them to our dict
    parameters = parse_parameters(argv, parameters)

    # Are we doing a flush?
    if parameters['flush']:
        print "Flushing data for", parameters['flush']
        setup(parameters)
        sys.exit('Flush complete.')

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
        parameters = query_pasta(parameters)
        parameters = unpack_packages(parameters)
        parameters = check_spatial_data(parameters)
        load_vector_types(parameters)
        load_raster_types(parameters)
        update_mxds(parameters)
        refresh_map_service(parameters)
        

if __name__ == '__main__':
    main(sys.argv[1:])
