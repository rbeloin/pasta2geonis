'''

Created on Jan 14, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico 
@see https://nis.lternet.edu/NIS/
'''
from abc import ABCMeta, abstractmethod, abstractproperty


class ArcpyTool:
    """
    Arcgis 10.1 allows creating toolboxes containing tools to be created
    completely in python. Each tool must follow a template, therefore this
    abstract class enforces the template so that subclasses will appear as
    properly written python tools, usable in the GUI or anywhere a toolbox
    tool can be used.
    """
    __metaclass__ = ABCMeta
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
    
    
class testtool(ArcpyTool):
    def __init__(self):
        pass
        
    @property
    def label(self):
        return "test"
    
    @property
    def alias(self):
        return "test alias"
    
    @property
    def description(self):
        return "test description property"
    
    def getParameterInfo(self):
        params = []
        return params

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        return (len(parameters), len(messages))
    
    
def quicktest():
    mytest = testtool()
    print mytest.canRunInBackground
    print mytest.isLicensed()
    print mytest.label
    print mytest.description
    print mytest.getParameterInfo()
    print mytest.execute([], [])
    
if __name__ == '__main__':
    quicktest()
    