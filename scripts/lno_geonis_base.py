'''
Created on Jan 15, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import sys, os
import arcpy
from arcpy import AddMessage as arcAddMsg, AddError as arcAddErr, AddWarning as arcAddWarn
from geonis_log import EvtLog
from logging import DEBUG, INFO, WARN, WARNING, ERROR, CRITICAL

from arcpy import Parameter

 #set the default value for the verbose switch for each tool. Verbose forces DEBUG logging
defaultVerboseValue = True


class ArcpyTool(object):
    """
    Arcgis 10.1 allows creating toolboxes containing tools to be created
    completely in python. Each tool must follow a template, therefore this
    abstract class enforces the template so that subclasses will appear as
    properly written python tools, usable in the GUI or anywhere a toolbox
    tool can be used.
    """
    def __init__(self):
        self.isRunningAsTool = False
        self._description = ""
        self._label = ""
        self._alias = ""
        self.logger = None
        self.showMsgs = defaultVerboseValue

    def runAsToolboxTool(self):
        self.isRunningAsTool = True

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

    def execute(self, parameters, messages):
        """Common tasks for excecuting the tool here"""
        self.showMsgs = parameters[0].value
        logdest = None
        if self.isRunningAsTool and parameters[1] and parameters[1].valueAsText:
            logdest = parameters[1].valueAsText
        arcAddMsg("log dest: " + str(logdest))
        arcAddMsg("__db " + str(__debug__))
        self.logger = EvtLog.getLogger(fileorpath = logdest)
        self.logger.logMessage(DEBUG, True, "param is " + str(type(parameters[1])))
        return


