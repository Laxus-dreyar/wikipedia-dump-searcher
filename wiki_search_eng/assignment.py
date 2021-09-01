import time
import xml.etree.ElementTree as ET
import re
import pickle
from nltk.stem.snowball import SnowballStemmer
import json


f = open('./stop.pickle','rb')
stop_words = pickle.load(f)
f.close()
snow_stemmer = SnowballStemmer(language='english')
tok_reg = re.compile(r'[A-Za-z0-9]+')


def remove_stop(sent):
    word_tokens = re.findall(tok_reg,sent)
    temp = {}
    for w in word_tokens:
        if w not in stop_words:
            stemmed = snow_stemmer.stem(w)
            if stemmed not in temp:
                temp[stemmed] = 1
            else:
                temp[stemmed] = temp[stemmed] + 1
    
    return temp
    

start_time = time.time()
index = {}
docID = 0
step = 0


for event,elem in iter(ET.iterparse('../dump.xml', events=("start", "end"))):

    if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}title' and event == "start":
        docID = docID + 1
        t = elem.text
        if not t:
            continue
        t = t.lower()
        temp = remove_stop(t)
        
        for w in temp:

            if w not in index:
                index[w] = {}
            
            if docID not in index[w]:
                index[w][docID] = []

            key = "t"
            index[w][docID].append(key + str(temp[w]))
            
    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}text' and event == "start":
        
        t = elem.text
        if not t:
            continue

        t = t.lower()
        temp = remove_stop(t)
        
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