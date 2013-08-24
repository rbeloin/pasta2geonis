'''
Created on Jan 15, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: Ron Beloin & Jack Peterson
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import sys, os
import arcpy
from arcpy import AddMessage as arcAddMsg, AddError as arcAddErr, AddWarning as arcAddWarn
from geonis_log import EvtLog
from logging import DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL
from arcpy import Parameter
from geonis_postgresql import getConfigValue
from geonis_pyconfig import defaultVerboseValue, tempMetadataFilename

class ArcpyTool(object):
    """
    Arcgis 10.1 allows creating toolboxes containing tools to be created
    completely in python. Each tool must follow a template, therefore this
    abstract class enforces the template so that subclasses will appear as
    properly written python tools, usable in the GUI or anywhere a toolbox
    tool can be used.
    """

    def __init__(self):
        self._description = ""
        self._label = ""
        self._alias = ""
        self.logger = None
        self._isRunningAsTool = True
        arcpy.LoadSettings(getConfigValue("pathtoenvsettings"))
        arcpy.env.scratchWorkspace = getConfigValue("scratchws")

    @property
    def isRunningAsTool(self):
        return self._isRunningAsTool

    @property
    def canRunInBackground(self):
        return False

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    # the following properties and methods must be implemented by the subclass
    @property
    def description(self):
        return self._description

    @property
    def label(self):
        return self._label

    @property
    def alias(self):
        return self._alias

    @property
    def spatialRef(self):
        return arcpy.SpatialReference(3857)

    def getParameterInfo(self):
        """Defines common parameter definitions"""
        commonparams = [Parameter(
                          displayName = 'Verbose',
                          name = 'send_msgs',
                          datatype = 'Boolean',
                          direction = 'Input',
                          parameterType = 'Optional'),
                        Parameter(
                          displayName = 'Log file or location',
                          name = 'logfilepath',
                          datatype = ['File', 'Folder'],
                          direction = 'Input',
                          parameterType = 'Optional')
                        ]
        commonparams[0].value = defaultVerboseValue
        return commonparams

    def getMultiDirInputParameter(self):
        return Parameter(
            displayName = "Input Directories",
            name = "in_dirlist",
            datatype = "Folder",
            direction = "Input",
            parameterType = "Optional",
            multiValue = True
            )

    def getMultiDirOutputParameter(self):
        return Parameter(
            displayName = "Output Directories",
            name = "out_dirlist",
            datatype = "Folder",
            direction = "Output",
            parameterType = "Derived",
            multiValue = True
            )


    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        pass

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        pass

    def getParamAsText(self, paramlist, numericIndex):
        if not paramlist or not paramlist[numericIndex]:
            return None
        if self.isRunningAsTool:
            return paramlist[numericIndex].valueAsText
        else:
            return str(paramlist[numericIndex].value)

##    def getEMLdata(self, workDir):
##        emldatafile = os.path.join(workDir,tempMetadataFilename)
##        if os.path.isfile(emldatafile):
##            try:
##                with open(emldatafile) as datafile:
##                    datastr = datafile.read()
##                return eval(datastr)
##            except Exception as err:
##                self.logger.logMessage(WARN, "EML data in %s could not be read or parsed. %s" % (emldatafile, err.message))
##                raise err
##        else:
##            raise Exception("EML data file %s not found." % (emldatafile,))


    def execute(self, parameters, messages):
        """Common tasks for excecuting the tool here"""
        logdest = None
        try:
            assert len(parameters) > 1
            logdest = self.getParamAsText(parameters,1)
            if logdest:
                testpath = str(logdest)
                if not os.path.isdir(testpath) and not os.path.isfile(testpath):
                    logdest = None
            self.logger = EvtLog.getLogger(fileorpath = logdest, showMessages = parameters[0].value)
            assert self.logger
            self.logger.logMessage(INFO,  self.__class__.__name__ + " started.")
            self.logger.logMessage(DEBUG, "As tool: " + str(self.isRunningAsTool))
            # if we have input dirs list, output dirs list parameters, make list instance
            for n in range(2,len(parameters)):
                if parameters[n].name == "in_dirlist":
                    indirlist = self.getParamAsText(parameters,n)
                    if indirlist is None or len(indirlist) == 0:
                        self.inputDirs = []
                    else:
                        self.inputDirs = [d for d in self.getParamAsText(parameters,n).split(';') if os.path.isdir(d)]
                        #self.inputDirs = [d for d in self.getParamAsText(parameters, n).split(';')]
                elif parameters[n].name == "out_dirlist":
                    self.outputDirs = [] # copied here as processing succeeds
        except AssertionError as asrtErr:
            #if these parameters are not here, tool has not been started correctly
            raise Exception("Unable to create log file. No parameters? " + asrtErr.message)


