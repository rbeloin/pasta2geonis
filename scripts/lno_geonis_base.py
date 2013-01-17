'''
Created on Jan 15, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico 
@see https://nis.lternet.edu/NIS/
'''

from abc import ABCMeta, abstractmethod, abstractproperty
from arcpy import Parameter


class ArcpyTool:
    """
    Arcgis 10.1 allows creating toolboxes containing tools to be created
    completely in python. Each tool must follow a template, therefore this
    abstract class enforces the template so that subclasses will appear as
    properly written python tools, usable in the GUI or anywhere a toolbox
    tool can be used.
    """
    __metaclass__ = ABCMeta
    
    #class level var
    isRunningAsTool = False
    
    @classmethod
    def runAsToolboxTool(cls):
        cls.isRunningAsTool = True
        
    @classmethod
    def isArcpyTool():
        return True
    
    @property
    def canRunInBackground(self):
        return False
    
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
    # the following properties and methods must be implemented by the subclass
    @abstractproperty
    def description(self):
        pass
    
    @abstractproperty
    def label(self):
        pass
    
    @abstractproperty
    def alias(self):
        pass
    
    @abstractmethod
    def getParameterInfo(self):
        """Define parameter definitions"""
        pass
    
    @abstractmethod
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        pass

    @abstractmethod
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        pass

    @abstractmethod
    def execute(self, parameters, messages):
        """The source code of the tool."""
        return
    
def getListofCommonInputs():
    commonparams = [Parameter(
                      displayName = 'Verbose',
                      name = 'msgs_on',
                      datatype = 'Boolean',
                      direction = 'Input',
                      parameterType = 'Optional'),
                    Parameter(
                      displayName = 'Log file location',
                      name = 'logfilepath',
                      datatype = 'Folder',
                      direction = 'Input',
                      parameterType = 'Optional')]
    commonparams[1].value = r"C:\temp\geonislogs";
    return commonparams
    
def updateParametersCommon(parameters):
    """ set a default log file path """
    logpath = [p for p in parameters if p.name == 'logfilepath']
    if len(logpath) == 1:
        pass
    return


    
