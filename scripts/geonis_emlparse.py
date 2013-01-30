'''
Config data for pasta2geonis workflow

Created on Jan 28, 2013

@change: https://github.com/rbeloin/pasta2geonis

@author: ron beloin
@copyright: 2013 LTER Network Office, University of New Mexico
@see https://nis.lternet.edu/NIS/
'''
"""
class EMLItem:
    ''' Parent class of items to be stored in a list after parsing the EML.
        Some items are for the checking of spatial data, other items for
        inclusion into the metadata upon loading of the data.
    '''
    def __init__(self):
        self.name = ""
        self.xpath = ""
        self.value = ""
        self.atts = dict()
    def compareToContent(content):
        return self.value.strip() == content.strip()


class EMLSourceItem(EMLItem):
    def __init__(self, name="", xpath="", emlcontent = ""):
        EMLItem.__init__(self)
        self.name = name
        self.xpath = xpath
        self.value = emlcontent
        self.protocol = 'ftp://'
        self.downloaded = False


class EMLValidationItem(EMLItem):
    def __init__(self, name="", xpath="", emlcontent = ""):
        EMLItem.__init__(self)
        self.name = name
        self.xpath = xpath
        self.value = emlcontent
        #list of GeoNISDataType to apply this check to, or e.g. GeoNISDataType.SPATIALVECTOR
        self.appliesTo = []
        self.comparisonFunc = None
    def compareToContent(content):
        if super(EMLValidationItem,self).compareToContent(content):
            return True
        elif comparer is not None:
            # other checks specific to type
            return comparisonFunc(self.value, content)
        else:
            return False


class EMLMetadataItem(EMLItem):
    def __init__(self, name="", xpath="", content = "", overwrite=False, xpath_metadata="" ):
        EMLItem.__init__(self)
        self.name = name
        self.xpath = xpath
        self.value = content
        self.overwrite = overwrite
        self.metaXpath = xpath_metadata

parsedEMLdata = []

parsedEMLdata.append(EMLMetadataItem(name="item1",
                    xpath="/spatialraster/node",
                    content="item1 content",
                    overwrite=True,
                    xpath_metadata="/desc/item"))

parsedEMLdata.append(EMLMetadataItem(name="item2",
                    xpath="/spatialraster/node",
                    content="item2 content",
                    overwrite=True,
                    xpath_metadata="/desc/item"))
"""

parseEMLdata = [
            {"name": "item1",
            "xpath": "/path/to/thing",
            "content": "",
            "metadata": True,
            "overwrite": True},
            {"name": "item2",
            "xpath": "/path/to/thing",
            "content": "",
            "metadata": True,
            "overwrite": True},
            {"name": "item3",
            "xpath": "/path/to/thing",
            "content": "",
            "metadata": False},
            ]

