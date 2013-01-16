import arcpy
import inspect
import lno_geonis_wf
from lno_geonis_wf import *


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GeoNIS Data Harvest"
        self.alias = "geonis"
        self.description = "toolbox description field"
        toollist = [obj for name, obj in inspect.getmembers(lno_geonis_wf) if inspect.isclass(obj) and "ArcpyTool" in str(obj.__bases__) and not inspect.isabstract(obj)]
        for toolcls in toollist:
            toolcls.runAsToolboxTool()
        self.tools = toollist
        

class Dummy(object):
    def __init__(self):
        """Arc seems to require at least one tool in this module,
        even if we don't include it in the toolbox."""
        self.label = "Dummy"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        return None

    def isLicensed(self):
        return False

    def updateParameters(self, parameters):
        pass

    def updateMessages(self, parameters):
        pass

    def execute(self, parameters, messages):
        pass



    
