'''
Created on Jan 15, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
import os, sys
from arcpy import Parameter
import lno_geonis_wf


def quicktest():
    #testtool.runAsToolboxTool()
    unpack = lno_geonis_wf.UnpackPackages()
    params = [Parameter(
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
    params[0].value = True
    params.append(Parameter(displayName = "Directory of Packages",
                        name = "in_dir",
                        datatype = "Folder",
                        parameterType = "Required",
                        direction = "Input"))
    params.append(Parameter(
    displayName = "Output Directories",
            name = "out_dirlist",
            datatype = "Folder",
            direction = "Output",
            parameterType = "Derived",
            multiValue = True))

    #params = unpack.getParameterInfo()
    params[0].value = True
    params[1].value = None
    params[2].value = r"C:\Users\ron\Documents\geonis_tests\newpackages"
    params[3].value = None
    unpack.execute(params,[])
    print params[3].value




if __name__ == '__main__':
    quicktest()
