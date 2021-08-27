import xml.sax
import time
import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class IndexHandler( xml.sax.ContentHandler ):

    def __init__(self):
        self.curID = 1
        self.curTag = ''
        self.docID = ''
        self.title = ''
        self.infoBox = ''
        self.body = ''
        self.category = ''
        self.links = ''
        self.references = ''
        self.text = ''
        self.un_list = []
        self.time = 0

    def startDocument(self):
        self.time = time.time()

    def startElement(self,name,attributes):
        self.curTag = name
        if name not in self.un_list:
            self.un_list.append(name)
        
        if name == 'page':
            self.docID = self.curID
            self.curID = self.curID + 1
    
    def endElement(self, name):
        if name == 'page':
            self.curTag = ''
            self.title = ''
            self.infoBox = ''
            self.body = ''
            self.category = ''
            self.links = ''
            self.references = ''
            
        
        if name == 'text':
            self.text = ''
        
        if name == 'title':
            self.title = ''
            # print(self.curID)
        
        # if name == 'body':
        #     x = self.remove_stop(self.body)
        
        # if name == 'title':
        #     print(self.title)
    
    def characters(self, content):
        if self.curTag == 'title':
            self.title += content
        else:
            self.text += content
    
    def endDocument(self):
        print(time.time()-self.time)
    
    def remove_stop(self,str):
        stop_words = list(stopwords.words('english'))
        stop_words.append(".")
        out = [w for w in word_list if not w in stop_words]
        return out
    


parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
indexer = IndexHandler()
parser.setContentHandler(indexer)
parser.parse('../dump.xml')


# tree = ET.parse('../wiki-dump.xml')
# root = tree.getroot()
# un = []
# for elem in root.iter():
#     if elem.tag not in un:
#         un.append(elem.tag)

# for i in un:
#     print(i)