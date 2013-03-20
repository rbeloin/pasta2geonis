"""
Config data for pasta2geonis workflow

Created on Jan 28, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
"""
import os, re
import time, datetime
from copy import deepcopy
from lxml import etree
from logging import WARN
from geonis_helpers import siteFromId
from geonis_pyconfig import pathToStylesheets


unittest = True


def main():
    """used for testing """
##    tmp = parseAndPopulateEMLDicts(r"Z:\docs\local\geonis_testdata\pkgs\knb-lter-tjv.2.1\gi01001i.xml")
##    if tmp is None:
##        return
##    recoveredThing = eval(str(tmp))
##    for item in recoveredThing:
##        if item['name'] == 'spatialType':
##            print "%s !!" % (item['content'],)
##        if item['content'] is not None and 'xpath_metadata' in item:
##            print item['name'], ": ", item['content']
##    for item in recoveredThing:
##        if 'applies_to' in item:
##            print "check ", item['applies_to']
##    with open(r"Z:\docs\local\geonis_testdata\pkgs\knb-lter-tjv.2.1\temp_meta.data", 'w') as tmpdat:
##        tmpdat.write(str(tmp))
##    createSuppXML(tmp, r"Z:\docs\local\geonis_testdata\pkgs\knb-lter-tjv.2.1\supp_metadata.xml")
##    with open(r"Z:\docs\local\geonis_testdata\pkgs\knb-lter-rmb.1.1\temp_meta.data", 'r') as tmpdat:
##        emldat = eval(" ".join(tmpdat.readlines()))
##    print str(emldat)
##    print str(createInsertObj(emldat))
    #dat = {"entityName":"water","type":"raster","hello":["my","world"]}
    #writeWorkingDataToXML(r"Z:\docs\local\git\pasta2geonis_sg\emlSubset.xml",dat)
    #print str(readWorkingData(r"Z:\docs\local\git\pasta2geonis_sg\emlSubset.xml", None))
    #createEmlSubset(r"Z:\docs\local\git\pasta2geonis_sg",r"Z:\docs\local\geonis_testdata\downloaded_pkgs\gi01001.xml")
    #print(readFromEmlSubset(r"Z:\docs\local\git\pasta2geonis_sg","//physical/distribution/online/url"))
    createEmlSubsetWithNode(r"Z:\docs\local\geonis_testdata\tmp1",r"Z:\docs\local\geonis_testdata\tmp2",2)


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


##def parseAndPopulateEMLDicts(pathToEML, logger = None):
##    global emlnamespaces, unittest
##    try:
##        treeObj = etree.parse(pathToEML)
##    except etree.ParseError as e:
##        if logger:
##            logger.logMessage("Error parsing %s with message %s" % (pathToEML, e.message))
##        else:
##            print e.message
##        raise Exception("Parsing error.")
##    if not treeObj.getroot().tag == ( "{%s}eml" % (emlnamespaces['eml'],) ):
##        msg = "%s does not appear to be valid EML doc." % (pathToEML,)
##        if logger is not None:
##            logger.logMessage(msg)
##        raise Exception(msg)
##    if False:
##        results = treeObj.xpath('dataset/abstract/descendant::text()', namespaces = emlnamespaces)
##        if results is not None:
##            for kw in [s for s in results if re.search(r"[\S]",s) is not None]:
##                print str(kw)
##            #print ';'.join(results)
##        else:
##            print "no results"
##        return treeObj
##    temp = deepcopy(parseEMLdata)
##    try:
##        spatialNod = treeObj.xpath('//spatialVector')
##        stype = [item for item in temp if item["name"] == "spatialType"]
##        if spatialNod and etree.iselement(spatialNod[0]):
##            stype[0]["content"] = "vector"
##        else:
##            spatialNod = treeObj.xpath('//spatialRaster')
##            if spatialNod and etree.iselement(spatialNod[0]):
##                stype[0]["content"] = "raster"
##            else:
##                print "problem, no spatial node seen"
##        for item in [d for d in temp if 'xpath' in d]:
##            elementText = treeObj.xpath(item['xpath'], namespaces = emlnamespaces)
##            actualText = [t for t in elementText if re.search(r"[\S]",t)]
##            if len(actualText) == 1:
##                item['content'] = actualText[0]
##            elif len(actualText) > 1:
##                item['content'] = ';'.join(actualText)
##            else:
##                item['content'] = None
##            item['content'] = re.sub(r"\s+"," ", item['content'])
##    except etree.XPathError as x:
##        if logger is not None:
##            logger.logMessage("Error with xpath.  %s" % (x.message,))
##        else:
##            print x.message
##        raise Exception(x.message)
##    except Exception as e:
##        if logger:
##            logger.logMessage("EML error. %s" % ( e.message, ))
##        else:
##            print e.message
##        raise Exception(e.message)
##    return temp
##
##def addToXML(root, xpth, value = None, overwrite = False):
##    """given top node, and full xpath to destination node, create the path
##        if needed and insert value as text
##    """
##    node = root
##    nodes = xpth.strip(' /').split("/")
##    # loop over nodes, creating if needed
##    for nodeName in nodes[1:]:
##        if not nodeName in [n.tag for n in node]:
##            node = etree.SubElement(node, nodeName)
##        else:
##            node = [n for n in node if n.tag == nodeName][0]
##    if not overwrite and node.text is not None:
##        etree.SubElement(node.getparent(),nodes[-1]).text = value
##    else:
##        node.text = value

##def createSuppXML(emldata, outFilePath):
##    try:
##        suppX = etree.Element("supplemental")
##        #break emldata list into different lists for different processing
##        allMeta = [item for item in emldata if "xpath_metadata" in item]
##        #otherCitDet = [item for item in allMeta if item["xpath_metadata"].endswith("otherCitDet")]
##        keywds = [item for item in allMeta if item["xpath_metadata"].endswith("keyword")]
##        remains = [item for item in allMeta if item not in keywds]
####        if len(otherCitDet) > 0:
####            otherCitDetVal = ""
####            for item in otherCitDet:
####                #combine content and make one entry
####                otherCitDetVal = "%s %s: %s; " % (otherCitDetVal, item["name"], item["content"])
####            addToXML(suppX, otherCitDet[0]["xpath_metadata"], otherCitDetVal.strip("; "), overwrite = True)
##        if len(keywds) > 0:
##            # make entry for each keyword
##            keywords = keywds[0]["content"].split(";")
##            for kw in keywords:
##                addToXML(suppX, keywds[0]["xpath_metadata"], kw, overwrite = False)
##        for item in remains:
##            addToXML(suppX, item["xpath_metadata"], item["content"], overwrite = True)
##        #finally add a date
##        datepath = [item for item in allMeta if item["name"] == "loadDate"][0]["xpath_metadata"]
##        addToXML(suppX, datepath, time.strftime("%Y-%m-%dT%H:%M:%S"), overwrite = True)
##        with open(outFilePath,'w') as outfile:
##            outfile.write(etree.tostring(suppX, xml_declaration = True))
##    except Exception as err:
##        raise Exception("Error creating supplemental metadata XML in %s. %s" % (outFilePath, err.message))
##    #print (etree.tostring(suppX, pretty_print = True))

def createEmlSubset(workDir, pathToEML):
    """ Run XSL transformation on EML with emlSubset.xsl to generate emlSubset.xml.
        Also, make workingData object with packageId, spatial type,
        and push it into newly created XML. Returns a tubple with the packageId and the number of spatialType nodes found.
    """
    stylesheet = pathToStylesheets + os.sep + "emlSubset.xsl"
    outputXMLtree = runTransformation(xslPath = stylesheet, inputXMLPath = pathToEML)
    workingData = {"packageId": None, "spatialType" : None, "entityName" : None, "entityDesc" : None, "dataEntityNum" : 0 }
    top = outputXMLtree.getroot()
    pId = top.get("packageId")
    workingData["packageId"] = pId
    spTypeHit = outputXMLtree.xpath("//*[local-name()='spatialRaster' or local-name()='spatialVector']")
    workingData["dataEntityNum"] = len(spTypeHit)
##    if len(spTypeHit) == 1:
##        spType = spTypeHit[0].tag
##        workingData["spatialType"] = spType
##        entNameNode = outputXMLtree.xpath("//" + spType + "/entityName")[0]
##        workingData["entityName"] = entNameNode.text
##        entDescNode = outputXMLtree.xpath("//" + spType + "/entityDescription")[0]
##        workingData["entityDesc"] = entDescNode.text
    outputXMLtree.write(workDir + os.sep + "emlSubset.xml", xml_declaration = 'yes')
    writeWorkingDataToXML(workDir, workingData)
    return (workingData["packageId"], workingData["dataEntityNum"])

def createEmlSubsetWithNode(originalDir, newDirectory, whichSpatialNode, logger = None):
    """Duplicate the emlSubset file in originalDir into newDirectory, keeping
       only the spatial node indicated by the number whichSpatialNode.
       Then, fill some entity info into workingData """
    emlsub = originalDir + os.sep + "emlSubset.xml"
    emlsubNew = newDirectory + os.sep + "emlSubset.xml"
    workingData = readWorkingData(originalDir)
    expectedNumber = int(workingData["dataEntityNum"])
    tree = etree.parse(emlsub)
    count = len(tree.xpath("//node()[local-name()='spatialRaster' or local-name()='spatialVector']"))
    if whichSpatialNode > count or count != expectedNumber:
        if logger:
            logger.logMessage(WARN, "In %s: %d spatial nodes were found, expected %d" % (originalDir, count, expectedNumber))
    xpth = "//node()[(local-name()='spatialRaster' or local-name()='spatialVector')][position() != " + str(whichSpatialNode) + "]"
    spTypeHit = tree.xpath(xpth)
    for rnode in spTypeHit:
        rnode.getparent().remove(rnode)
    spTypeHit = tree.xpath("//node()[local-name()='spatialRaster' or local-name()='spatialVector']")
    if len(spTypeHit) == 1:
        snode = spTypeHit[0]
        spType = snode.tag
        workingData["spatialType"] = spType
        entNameNode = snode.xpath("//entityName")[0]
        workingData["entityName"] = entNameNode.text
        #save the first 16 characters of entityName after non-alphanumeric removed
        workingData["shortEntityName"] = stringToValidName(workingData["entityName"])
        entDescNode = snode.xpath("//entityDescription")[0]
        workingData["entityDesc"] = entDescNode.text
        tree.write(emlsubNew, xml_declaration = 'yes')
        writeWorkingDataToXML(newDirectory, workingData)
    else:
        if logger:
            logger.logMessage(WARN, "In %s: %d spatial nodes were left, expecting 1" % (originalDir, len(spTypeHit)))




def createSuppXML(workDir):
    """ Run XSL transformation on emlSubset.xml with emlSubsetToSupp.xsl to generate emlSupp.xml """
    stylesheet = pathToStylesheets + os.sep + "emlSubsetToSupp.xsl"
    inputXML = workDir + os.sep + "emlSubset.xml"
    outputXMLtree = runTransformation(xslPath = stylesheet, inputXMLPath = inputXML)
    #fill in today as date of pub within the new reference node
    outputXMLtree.xpath("//aggrInfo/aggrDSName/date/pubDate")[0].text = str(datetime.date.today())
    outputXMLtree.write(workDir + os.sep + "emlSupp.xml", xml_declaration = 'yes')
    del outputXMLtree


def runTransformation(xslPath = None, inputXMLPath = None):
    """ XSLT using lxml on the given parameters. Returns ElementTree instance. Traps lxml exceptions and throws Exception """
    if os.path.isfile(xslPath) and os.path.isfile(inputXMLPath):
        try:
            transformer = etree.XSLT(etree.parse(xslPath))
            emltree = etree.parse(inputXMLPath)
            return transformer(emltree)
        except etree.LxmlSyntaxError as syntaxErr:
            msg = syntaxErr.message
            raise Exception("Syntax/parse error transforming %s with %s. %s" % (inputXMLPath, xslPath, msg))
        except etree.XSLTerror as transformErr:
            msg = transformer.message
            raise Exception("XSLT error transforming %s with %s. %s" % (inputXMLPath, xslPath, msg))
        finally:
            del transformer
    else:
        raise Exception("%s or %s not found." % (xslPath, inputXMLPath))


def stringToValidName(inStr, spacesToUnderscore = False, max = 16):
    """Return alphanumeric + underscore chars up to max"""
    if spacesToUnderscore:
        return ''.join(re.findall('\w+',inStr.replace(' ','_')))[:max]
    else:
        return ''.join(re.findall('\w+',inStr))[:max]


##def createInsertObj(emldata):
##    retval = {}
##    pkgId = getContentFromEmldataByName(emldata,"packageId")
##    site, numId, rev = siteFromId(pkgId)
##    if site == "error":
##        retval["error"] = "bad package id"
##        return ("error",retval)
##    retval["packageid"] = pkgId
##    retval["site"] = site
##    retval["numericid"] = numId
##    retval["revision"] = rev
##    retval["title"] = getContentFromEmldataByName(emldata,"title")
##    retval["keywords"] = getContentFromEmldataByName(emldata,"keywords")
##    retval["entity"] = getContentFromEmldataByName(emldata,"entityName")
##    spatialType = getContentFromEmldataByName(emldata,"spatialType")
##    retval["raster"] = spatialType == "raster"
##    retval["featureclass"] = spatialType == "vector"
##    retval["added"] = datetime.datetime.now()
##    #this filled in when data loaded
##    retval["layerName"] = ""
##    #this recovered by query on map
##    retval["servId"] = None
##    return (getInsertStmt(),retval)

##def getContentFromEmldataByName(emldata, name):
##    try:
##        return [item for item in emldata if item["name"] == name][0]["content"]
##    except Exception:
##        return ""
##

def writeWorkingDataToXML(workDir, data, logger = None):
    try:
        pathToXML = workDir + os.sep + "emlSubset.xml"
        treeObj = etree.parse(pathToXML)
        root = treeObj.getroot()
    except etree.ParseError as e:
        if logger:
            logger.logMessage("Error parsing %s with message %s" % (pathToXML, e.message))
        else:
            print e.message
        raise Exception("Parsing error.")
    if not root.tag == "emlSubset":
        msg = "%s does not appear to be emlSubset doc." % (pathToXML,)
        if logger is not None:
            logger.logMessage(msg)
        raise Exception(msg)
    # get workingData node, clear it
    wdnode = root.xpath("workingData")[0]
    if len(wdnode):
        wdnode.clear()
    for item in data:
        child = etree.SubElement(wdnode,"item")
        child.set("name", item)
        if isinstance(data[item],list):
            child.set("separator",';')
            child.text = ';'.join(data[item])
        else:
            child.text = str(data[item])
    #print etree.tostring(treeObj)
    treeObj.write(pathToXML, xml_declaration = 'yes')



def readWorkingData(workDir, logger = None):
    try:
        pathToXML = workDir + os.sep + "emlSubset.xml"
        treeObj = etree.parse(pathToXML)
        root =  treeObj.getroot()
    except etree.ParseError as e:
        if logger:
            logger.logMessage("Error parsing %s with message %s" % (pathToXML, e.message))
        else:
            print e.message
        raise Exception("Parsing error.")
    if not root.tag == "emlSubset":
        msg = "%s does not appear to be emlSubset doc." % (pathToXML,)
        if logger is not None:
            logger.logMessage(msg)
        raise Exception(msg)
    # get workingData item nodes
    wdnodes = root.xpath("workingData/item")
    retval = {}
    for item in wdnodes:
        if item.get("name") is not None:
            if item.get("separator") is not None:
                retval[item.get("name")] = item.text.split(item.get("separator"))
            else:
                retval[item.get("name")] = item.text
    return retval


def readFromEmlSubset(workDir, xpath, logger = None):
    retval = ""
    try:
        pathToXML = workDir + os.sep + "emlSubset.xml"
        treeObj = etree.parse(pathToXML)
        root =  treeObj.getroot()
    except etree.ParseError as e:
        if logger:
            logger.logMessage("Error parsing %s with message %s" % (pathToXML, e.message))
        else:
            print e.message
        raise Exception("Parsing error.")
    if not root.tag == "emlSubset":
        msg = "%s does not appear to be emlSubset doc." % (pathToXML,)
        if logger is not None:
            logger.logMessage(msg)
        raise Exception(msg)
    # get nodes
    nodes = root.xpath(xpath)
    if nodes:
        retval = nodes[0].text
    del nodes, root, treeObj
    return retval




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
