'''

Created on Jan 14, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico 
@see https://nis.lternet.edu/NIS/
'''
from lno_geonis_base import ArcpyTool


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
        return "test description property or testtool, the original"
    
    def getParameterInfo(self):
        params = []
        return params

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        print("params: " + str(len(parameters)) + ", messages: " + str(len(messages)))
        #messages.addMessage("test 1 done");
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
        params = []
        return params

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        print("params: " + str(len(parameters)) + ", messages: " + str(len(messages)))
        #messages.addMessage("test 2 done");
        return
        
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
    