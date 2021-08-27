import xml.sax

class IndexHandler( xml.sax.ContentHandler ):

    def __init__(self):

        self.curID = 1
        self.curTag = ""
        self.docID = ""
        self.title = ""
        self.infoBox = ""
        self.body = ""
        self.category = ""
        self.links = ""
        self.references = ""
    
    def startElement(self,name,attributes):
        self.curTag = name
        if name == 'page':
            self.docID = self.curID
            self.curID = self.curID + 1
    
    def endElement(self, name):
        if name == 'page':
            self.curTag = ''
            self.title = ''
            self.infoBox = ""
            self.body = ""
            self.category = ""
            self.links = ""
            self.references = ""
        
        if name == 'title':
            print(self.title)
    
    def characters(self, content):
        if self.curTag == 'title':
            self.title = content

        if self.curTag == 'iBox':
            self.infoBox = content.lower()
        
        if self.curTag == 'body':
            self.body == content.lower()
        
        if self.curTag == 'cate':
            self.category = content.lower()
        
        if self.curTag == 'links':
            self.links = content
        
        if self.curTag == 'ref':
            self.references =content
    


parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
indexer = IndexHandler()
parser.setContentHandler(indexer)
parser.parse('../wiki-dump.xml')