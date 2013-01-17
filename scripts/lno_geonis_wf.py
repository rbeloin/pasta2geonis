'''

Created on Jan 14, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico 
@see https://nis.lternet.edu/NIS/
'''
import sys, os
import arcpy

from lno_geonis_base import ArcpyTool
from lno_geonis_base import getListofCommonInputs, updateParametersCommon


class testtool(ArcpyTool):
    def __init__(self):
        pass    
        
    @property
    def label(self):
        return "testtool"
    
    @property
    def alias(self):
        return "testtool alias"
    
    @property
    def description(self):
        return "test description property of testtool, the original"
    
    def getParameterInfo(self):
        params = getListofCommonInputs()
        return params

    def updateParameters(self, parameters):
        updateParametersCommon(parameters)
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        if(self.isRunningAsTool):
            messages.AddMessage("this message brought to you via message object pass in")
        else:
            arcpy.AddMessage("this message brought to you via arcpy")            
        return

    
class test2tool(ArcpyTool):
    def __init__(self):
        pass
        
    @property
    def label(self):
        return "test2tool"
    
    @property
    def alias(self):
        return "test2tool alias"
    
    @property
    def description(self):
        return "this is test 2 tool with changes"
    
    def getParameterInfo(self):
        params = getListofCommonInputs()
        return params

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        if(self.isRunningAsTool):
            messages.AddMessage("this message brought to you via message object pass in")
        else:
            arcpy.AddMessage("this message brought to you via arcpy")            
        return
 

def quicktest():
    #testtool.runAsToolboxTool()
    mytest = testtool()
    print mytest.isRunningAsTool
    print mytest.canRunInBackground
    print mytest.isLicensed()
    print mytest.label
    print mytest.description
    print mytest.getParameterInfo()
    print mytest.execute([], [])
    
if __name__ == '__main__':
    quicktest()
    