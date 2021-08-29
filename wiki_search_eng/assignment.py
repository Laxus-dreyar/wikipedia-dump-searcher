import time
import xml.etree.ElementTree as ET
from nltk.stem.snowball import SnowballStemmer
import json
from nltk.corpus import stopwords
import gensim
from gensim.parsing.preprocessing import remove_stopwords, STOPWORDS
from nltk.tokenize import word_tokenize


def remove_stop(sent):
    # stop_words = list(stopwords.words('english'))
    punt1 = set(['+','=','-','_',')','(','*','&','^','%','$','#','@','!','~','`','|','\\',']','}','[','{','\'','\"','\;','\:','/','?','.','>','<',','])
    # punct2 = ["he'd","let's","there's","she'd","we'll","can't","i'm","why's","i've","when's","who's","they'd","i'd","they're","could","cannot","that's","i'll","ought","would","they'll","he'll","he's","what's","here's","we'd","she'll","we've","we're","how's","where's","they've"]
    # stop_words.extend(punt1)
    # stop_words = set(stop_words)
    stop_words = STOPWORDS
    snow_stemmer = SnowballStemmer(language='english')
    sent1 = sent
    word_tokens = word_tokenize(sent1)
    temp = {}
    for w in word_tokens:
        if (w not in stop_words) and (w not in punt1):
            stemmed = snow_stemmer.stem(w)
            if stemmed not in temp:
                temp[stemmed] = 1
            else:
                temp[stemmed] = temp[stemmed] + 1
    
    return temp
    

start_time = time.time()
# tree = ET.parse('../dump.xml')
tree = ET.parse('./dump1.xml')
root = tree.getroot()
index = {}
docID = 0
step = 0


for elem in root.iter():

    if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}title':
        docID = docID + 1
        t = elem.text
        if not t:
            continue

        t = t.lower()
        temp = remove_stop(t)
        # temp = {}
        
        # for w in tokened:
        #     if w in temp:
        #         temp[w] = temp[w] + 1
        #     else:
        #         temp[w] = 1
        
        for w in temp:

            if w not in index:
                index[w] = {}
            
            if docID not in index[w]:
                index[w][docID] = []

            key = "t"
            index[w][docID].append(key + str(temp[w]))
            
    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}text':
        
        t = elem.text
        if not t:
            continue

        t = t.lower()
        temp = remove_stop(t)
        # temp = {}
        
        # for w in tokened:
        #     if w in temp:
        #         temp[w] = temp[w] + 1
        #     else:
        #         temp[w] = 1
        
        for w in temp:

            if w not in index:
                index[w] = {}
            
            if docID not in index[w]:
                index[w][docID] = []

            key = "b"
            index[w][docID].append(key + str(temp[w]))
                

        # external_links_split = bod.split("==External links==")
        # cur_links = []

        # if len(external_links_split)>1:
        #     temp = external_links_split[1].split('\n')
        #     for link in temp:
        #         if len(link) > 0 and link[0] == '*':
        #             cur_links.append(link)
        
        # print(len(cur_links))
    
    step = step + 1
    if step%20000 == 0:
        print(step)


print("time taken = ", time.time()-start_time)
with open('index.txt','w') as convert_file:
    convert_file.write(json.dumps(index))