import arcpy
from arcpy import Parameter


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "TBalias"
        self.description = "toolbox description field"

        # List of tool classes associated with this toolbox
        self.tools = [Test1]


class Test1(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Test1"
        self.description = "here is description"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions """
        param0 = Parameter(
            displayName="give me name",
            name="istr",
            datatype="String",
            parameterType="Required",
            direction="Input")

        param1 = Parameter(
            displayName="greeting",
            name="ostr",
            datatype="String",
            parameterType="Derived",
            direction="Output")
        params = [param0,param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        parameters[1].value = "hello " + parameters[0].value
        messages.addMessage("result: " + parameters[1].valueAsText)
        return
