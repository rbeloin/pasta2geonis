import arcpy
from lno_geonis_wf import toolclasses as tools
for tool in tools:
    exec "from lno_geonis_wf import " + tool.__name__

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GeoNIS Data Harvest"
        self.alias = "geonis"
        self.description = "this is the toolbox description field"
        self.tools = tools
        

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



    
