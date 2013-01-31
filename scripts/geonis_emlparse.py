"""
Config data for pasta2geonis workflow

Created on Jan 28, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
"""
import os
from copy import deepcopy
from lxml import etree
import re

istest = False
##
##class EMLItem:
##    """ Parent class of items to be stored in a list after parsing the EML.
##        Some items are for the checking of spatial data, other items for
##        inclusion into the metadata upon loading of the data.
##    """
##    def __init__(self):
##        self.name = ""
##        self.xpath = ""
##        self.value = ""
##        self.atts = dict()
##    def compareToContent(content):
##        return self.value.strip() == content.strip()
##
##
##class EMLSourceItem(EMLItem):
##    def __init__(self, name="", xpath="", emlcontent = ""):
##        EMLItem.__init__(self)
##        self.name = name
##        self.xpath = xpath
##        self.value = emlcontent
##        self.protocol = 'ftp://'
##        self.downloaded = False
##
##
##class EMLValidationItem(EMLItem):
##    def __init__(self, name="", xpath="", emlcontent = ""):
##        EMLItem.__init__(self)
##        self.name = name
##        self.xpath = xpath
##        self.value = emlcontent
##        #list of GeoNISDataType to apply this check to, or e.g. GeoNISDataType.SPATIALVECTOR
##        self.appliesTo = []
##        self.comparisonFunc = None
##    def compareToContent(content):
##        if super(EMLValidationItem,self).compareToContent(content):
##            return True
##        elif comparer is not None:
##            # other checks specific to type
##            return comparisonFunc(self.value, content)
##        else:
##            return False
##
##
##class EMLMetadataItem(EMLItem):
##    def __init__(self, name="", xpath="", content = "", overwrite=False, xpath_metadata="" ):
##        EMLItem.__init__(self)
##        self.name = name
##        self.xpath = xpath
##        self.value = content
##        self.overwrite = overwrite
##        self.metaXpath = xpath_metadata
##
##parsedEMLdata = []
##
##parsedEMLdata.append(EMLMetadataItem(name="item1",
##                    xpath="/spatialraster/node",
##                    content="item1 content",
##                    overwrite=True,
##                    xpath_metadata="/desc/item"))
##
##parsedEMLdata.append(EMLMetadataItem(name="item2",
##                    xpath="/spatialraster/node",
##                    content="item2 content",
##                    overwrite=True,
##                    xpath_metadata="/desc/item"))

def main():
    tmp = parseAndPopulateEMLDicts(pathToEML = r"Z:\docs\local\geonis_testdata\downloaded_pkgs\gi01001i.xml")
    if tmp is None:
        return
    recoveredThing = eval(str(tmp))
    for item in recoveredThing:
        if item['name'] == 'spatialType':
            print "%s !!" % (item['content'],)
        if item['content'] is not None and 'xpath_metadata' in item:
            print item['name'], ": ", item['content']
    for item in recoveredThing:
        if 'applies_to' in item:
            print "check ", item['applies_to']


emlnamespaces = {'eml':'eml://ecoinformatics.org/eml-2.1.0',
                'stmml':"http://www.xml-cml.org/schema/stmml",
                'sw':"eml://ecoinformatics.org/software-2.1.0",
                'cit':"eml://ecoinformatics.org/literature-2.1.0",
                'ds':"eml://ecoinformatics.org/dataset-2.1.0" ,
                'prot':"eml://ecoinformatics.org/protocol-2.1.0" ,
                'doc':"eml://ecoinformatics.org/documentation-2.1.0" ,
                'res':"eml://ecoinformatics.org/resource-2.1.0",
                'xs':"http://www.w3.org/2001/XMLSchema",
                'xsi':"http://www.w3.org/2001/XMLSchema-instance"}


def parseAndPopulateEMLDicts(pathToEML = "", logger = None):
    global emlnamespaces
    global istest
    treeObj = etree.parse(pathToEML)
    if istest:
        results = treeObj.xpath('dataset/abstract/descendant::text()', namespaces = emlnamespaces)
        if results is not None:
            for kw in [s for s in results if re.search(r"[\S]",s) is not None]:
                print str(kw)
            #print ';'.join(results)
        else:
            print "no results"
        return None
    temp = deepcopy(parseEMLdata)
    spatialNod = treeObj.xpath('//spatialVector')
    stype = [item for item in temp if item["name"] == "spatialType"]
    if spatialNod and etree.iselement(spatialNod[0]):
        stype[0]["content"] = "vector"
    else:
        spatialNod = treeObj.xpath('//spatialRaster')
        if spatialNod and etree.iselement(spatialNod[0]):
            stype[0]["content"] = "rastor"
        else:
            print "problem, no spatial node seen"
    for item in [d for d in temp if 'xpath' in d]:
        elementText = treeObj.xpath(item['xpath'], namespaces = emlnamespaces)
        actualText = [t for t in elementText if re.search(r"[\S]",t)]
        if len(actualText) == 1:
            item['content'] = actualText[0]
        elif len(actualText) > 1:
            item['content'] = ';'.join(actualText)
        else:
            item['content'] = None
    return temp


"""
    List contains objects that describe what and where to pull information from the EML file
    for primarily two purposes: data checking and merging of metadata from here with Arc metadata
    file created when loading or storing the data. A function in this module iterates over
    this list to capture the text from the EML. Items that have 'xpath_metadata' are for
    merging with other metadata. They should have an 'overwrite' flag. Items with 'applies_to'
    key are for checks against the data. An item may be used for both purposes.
"""
parseEMLdata = [
            {"name": "spatialType",
            "content": ""},
            {"name": "packageId",
            "xpath": "/eml:eml/@packageId",
            "content": "",
            "xpath_metadata": ""},
            {"name": "messages",
            "content": []},
            {"name": "title",
            "xpath": "dataset/title/text()",
            "content": None,
            "xpath_metadata": "/path/to/node",
            "overwrite": True},
            {"name": "keywords",
            "xpath": "//keyword/text()",
            "content": None,
            "xpath_metadata": "/path/to/node",
            "overwrite": True},
            {"name": "abstract",
            "xpath": "//abstract/descendant::text()",
            "content": None,
            "xpath_metadata": "/path/to/node"},
            {"name": "purpose",
            "xpath": "dataset/purpose/descendant::text()",
            "content": None,
            "xpath_metadata": "/path/to/node"},
            {"name": "url",
            "xpath": "//distribution/online/url/text()",
            "content": None,
            "applies_to": ("vector","raster") },
            {"name": "entityName",
            "xpath": "dataset/*/entityName/text()",
            "content": None,
            "applies_to": ("vector","raster") },
            {"name": "entityDescription",
            "xpath": "dataset/*/entityDescription/text()",
            "content": None,
            "applies_to": ("vector","raster") },
            ]

if __name__ == '__main__':
    global istest
    #istest = True
    main()
