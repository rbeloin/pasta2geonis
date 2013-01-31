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
    tmp = parseAndPopulateEMLDicts(pathToEML = r"Z:\docs\local\geonis_testdata\pkgs\knb-lter-tjv-1\tv06101a.xml")
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
    experimental = False
    with open(pathToEML) as eml:
        treeObj = etree.parse(eml)
    if experimental:
        for n in treeObj.xpath('dataset/*/keyword', namespaces = emlnamespaces):
            nodename, content = (n.tag, n.text)
            print nodename, "contains ", content
        return parseEMLdata
    temp = deepcopy(parseEMLdata)
    spatialNod = treeObj.xpath('//spatialVector')
    if spatialNod and etree.iselement(spatialNod[0]):
        print "vector!!"
        temp.append({'name': 'spatialType','content':'vector'})
    else:
        spatialNod = treeObj.xpath('//spatialRaster')
        if spatialNod and etree.iselement(spatialNod[0]):
            print "raster!!"
            temp.append({'name': 'spatialType','content':'raster'})
        else:
            print "problem, no spatial node seen"
    for item in [d for d in temp if 'xpath' in d]:
        nodes = treeObj.xpath(item['xpath'], namespaces = emlnamespaces)
        if len(nodes) == 1:
            item['content'] = nodes[0].text
        elif len(nodes) > 1:
            item['content'] = ';'.join([n.text for n in nodes])
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
            {"name": "title",
            "xpath": "dataset/title",
            "content": None,
            "xpath_metadata": "/path/to/node",
            "overwrite": True},
            {"name": "keywords",
            "xpath": "dataset/*/keyword",
            "content": None,
            "xpath_metadata": "/path/to/node",
            "overwrite": True},
            {"name": "abstract",
            "xpath": "//abstract/para",
            "content": None,
            "xpath_metadata": "/path/to/node"},
            {"name": "purpose",
            "xpath": "dataset/purpose/para",
            "content": None,
            "xpath_metadata": "/path/to/node"},
            {"name": "url",
            "xpath": "//distribution/online/url",
            "content": None,
            "applies_to": ("vector","raster") },
            {"name": "entityName",
            "xpath": "dataset/*/entityName",
            "content": None,
            "applies_to": ("vector","raster") },
            {"name": "entityDescription",
            "xpath": "dataset/*/entityDescription",
            "content": None,
            "applies_to": ("vector","raster") },
            ]

if __name__ == '__main__':
    main()
