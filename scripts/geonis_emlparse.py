"""
Config data for pasta2geonis workflow

Created on Jan 28, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
"""
import os, re
import time
from copy import deepcopy
from lxml import etree


unittest = True


def main():
    """used for testing """
    tmp = parseAndPopulateEMLDicts(r"Z:\docs\local\geonis_testdata\pkgs\knb-lter-tjv.2.1\gi01001i.xml")
    if tmp is None:
        return
##    recoveredThing = eval(str(tmp))
##    for item in recoveredThing:
##        if item['name'] == 'spatialType':
##            print "%s !!" % (item['content'],)
##        if item['content'] is not None and 'xpath_metadata' in item:
##            print item['name'], ": ", item['content']
##    for item in recoveredThing:
##        if 'applies_to' in item:
##            print "check ", item['applies_to']
    with open(r"Z:\docs\local\geonis_testdata\pkgs\knb-lter-tjv.2.1\temp_meta.data", 'w') as tmpdat:
        tmpdat.write(str(tmp))
    createSuppXML(tmp, r"Z:\docs\local\geonis_testdata\pkgs\knb-lter-tjv.2.1\supp_metadata.xml")

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


def parseAndPopulateEMLDicts(pathToEML, logger = None):
    global emlnamespaces, unittest
    try:
        treeObj = etree.parse(pathToEML)
    except etree.ParseError as e:
        if logger:
            logger.logMessage("Error parsing %s with message %s" % (pathToEML, e.message))
        else:
            print e.message
        raise Exception("Parsing error.")
    if not treeObj.getroot().tag == ( "{%s}eml" % (emlnamespaces['eml'],) ):
        msg = "%s does not appear to be valid EML doc." % (pathToEML,)
        if logger is not None:
            logger.logMessage(msg)
        raise Exception(msg)
    if False:
        results = treeObj.xpath('dataset/abstract/descendant::text()', namespaces = emlnamespaces)
        if results is not None:
            for kw in [s for s in results if re.search(r"[\S]",s) is not None]:
                print str(kw)
            #print ';'.join(results)
        else:
            print "no results"
        return treeObj
    temp = deepcopy(parseEMLdata)
    try:
        spatialNod = treeObj.xpath('//spatialVector')
        stype = [item for item in temp if item["name"] == "spatialType"]
        if spatialNod and etree.iselement(spatialNod[0]):
            stype[0]["content"] = "vector"
        else:
            spatialNod = treeObj.xpath('//spatialRaster')
            if spatialNod and etree.iselement(spatialNod[0]):
                stype[0]["content"] = "raster"
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
            item['content'] = re.sub(r"\s+"," ", item['content'])
    except etree.XPathError as x:
        if logger is not None:
            logger.logMessage("Error with xpath.  %s" % (x.message,))
        else:
            print x.message
        raise Exception(x.message)
    except Exception as e:
        if logger:
            logger.logMessage("EML error. %s" % ( e.message, ))
        else:
            print e.message
        raise Exception(e.message)
    return temp

def addToXML(root, xpth, value = None, overwrite = False):
    """given top node, and full xpath to destination node, create the path
        if needed and insert value as text
    """
    node = root
    nodes = xpth.strip(' /').split("/")
    # loop over nodes, creating if needed
    for nodeName in nodes[1:]:
        if not nodeName in [n.tag for n in node]:
            node = etree.SubElement(node, nodeName)
        else:
            node = [n for n in node if n.tag == nodeName][0]
    if not overwrite and node.text is not None:
        etree.SubElement(node.getparent(),nodes[-1]).text = value
    else:
        node.text = value

def createSuppXML(emldata, outFilePath):
    try:
        suppX = etree.Element("supplemental")
        #break emldata list into different lists for different processing
        allMeta = [item for item in emldata if "xpath_metadata" in item]
        #otherCitDet = [item for item in allMeta if item["xpath_metadata"].endswith("otherCitDet")]
        keywds = [item for item in allMeta if item["xpath_metadata"].endswith("keyword")]
        remains = [item for item in allMeta if item not in keywds]
##        if len(otherCitDet) > 0:
##            otherCitDetVal = ""
##            for item in otherCitDet:
##                #combine content and make one entry
##                otherCitDetVal = "%s %s: %s; " % (otherCitDetVal, item["name"], item["content"])
##            addToXML(suppX, otherCitDet[0]["xpath_metadata"], otherCitDetVal.strip("; "), overwrite = True)
        if len(keywds) > 0:
            # make entry for each keyword
            keywords = keywds[0]["content"].split(";")
            for kw in keywords:
                addToXML(suppX, keywds[0]["xpath_metadata"], kw, overwrite = False)
        for item in remains:
            addToXML(suppX, item["xpath_metadata"], item["content"], overwrite = True)
        #finally add a date
        datepath = [item for item in allMeta if item["name"] == "loadDate"][0]["xpath_metadata"]
        addToXML(suppX, datepath, time.strftime("%Y-%m-%dT%H:%M:%S"), overwrite = True)
        with open(outFilePath,'w') as outfile:
            outfile.write(etree.tostring(suppX, xml_declaration = True))
    except Exception as err:
        raise Exception("Error creating supplemental metadata XML in %s. %s" % (outFilePath, err.message))
    #print (etree.tostring(suppX, pretty_print = True))



"""
    List contains objects that describe what and where to pull information from the EML file
    for primarily two purposes: data checking and merging of metadata from here with Arc metadata
    file created when loading or storing the data. A function in this module iterates over
    this list to capture the text from the EML. Items that have 'xpath_metadata' are for
    merging with other metadata.  Items with 'applies_to'
    key are for checks against the data. An item may be used for both purposes.
"""
parseEMLdata = [
            {"name": "spatialType",
            "content": ""},
            {"name": "packageId",
            "xpath": "/eml:eml/@packageId",
            "content": "",
            "xpath_metadata": "/supplemental/dataIdInfo/aggrInfo/aggrDSName/citId/identCode"},
            {"name": "messages",
            "content": []},
            {"name": "title",
            "xpath": "dataset/title/text()",
            "content": None,
            "xpath_metadata": "/supplemental/dataIdInfo/idCitation/resTitle"},
            {"name": "keywords",
            "xpath": "//keyword/text()",
            "content": None,
            "xpath_metadata": "/supplemental/dataIdInfo/searchKeys/keyword"},
            {"name": "abstract",
            "xpath": "//abstract/descendant::text()",
            "content": None,
            "xpath_metadata": "/supplemental/dataIdInfo/idAbs"},
            {"name": "purpose",
            "xpath": "dataset/purpose/descendant::text()",
            "content": None,
            "xpath_metadata": "/supplemental/dataIdInfo/idPurp"},
            {"name": "url",
            "xpath": "//physical/descendant::url/text()",
            "content": None,
            "applies_to": ("vector","raster"),
            "xpath_metadata": "/supplemental/dataIdInfo/aggrInfo/aggrDSName/citOnlineRes/linkage" },
            {"name": "entityName",
            "xpath": "dataset/*/entityName/text()",
            "content": None,
            "applies_to": ("vector","raster") },
            {"name": "entityDescription",
            "xpath": "dataset/*/entityDescription/text()",
            "content": None,
            "applies_to": ("vector","raster") },
            {"name": "loadDate",
            "content": None,
            "xpath_metadata": "/supplemental/dataIdInfo/aggrInfo/aggrDSName/date/pubDate" },            ]

if __name__ == '__main__':
    unittest = True
    main()
