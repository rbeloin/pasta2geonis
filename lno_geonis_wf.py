'''
Created on Jan 14, 2013

@author: ron beloin
'''
from abc import ABCMeta, abstractmethod, abstractproperty


class ArcpyTool:
    __metaclass__ = ABCMeta
    def __init__(self):
        self.canRunInBackground = False
    
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
    
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
        params = None
        return params

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        return (len(parameters), len(messages))
    
    
def main():
    mytest = testtool()
    print mytest.label
    print mytest.description
    print mytest.execute([], [])
    
if __name__ == '__main__':
    main()
    