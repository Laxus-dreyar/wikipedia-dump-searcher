import time
import xml.etree.ElementTree as ET
import re
import pickle
import sys
from nltk.corpus import stopwords
import Stemmer
import json

start_time = time.time()
stop_words = set(stopwords.words('english'))
snow_stemmer = Stemmer.Stemmer('english')
token_reg = re.compile(r'[A-Za-z0-9]+')
css_reg = re.compile(r'{\|(.*?)\|}',re.DOTALL)
link_reg = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
extension_set = set(['jpg','jpeg','png'])
comment_sq = re.compile(r'(\[\[[^\[\]]*\]\])')

def add_to_index(t,key):
    
    word_tokens = re.findall(token_reg,t)
    temp = {}
    for w in word_tokens:
        if (w in stop_words) or (w[-3:] in extension_set) or (len(w) > 15):
            continue
        stemmed = snow_stemmer.stemWord(w)
        if stemmed not in temp:
            temp[stemmed] = 1
        else:
            temp[stemmed] = temp[stemmed] + 1
    
    for w in temp:

        if w not in index:
            index[w] = {}

        if key not in index[w]:
            index[w][key] = []

        if temp[w] > 1:
            index[w][key].append(str(docID)+":"+str(temp[w]))
        else:
            index[w][key].append(str(docID))

index = {}
docID = 0
step = 0
unique_words = set()

dump_path = sys.argv[1]
saving_path = sys.argv[2] + "/index.txt"
stat_path = sys.argv[3]

for event,elem in iter(ET.iterparse(dump_path, events=("start", "end"))):
    
    if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}title' and event == "end":
        docID = docID + 1
        t = elem.text
        if not t:
            continue

        t = t.lower()

        toks = t.split(' ')
        
        for w in toks:
            unique_words.add(w)
        
        t = re.sub(link_reg,'',t)
        t = re.sub(css_reg,'',t)
        
        add_to_index(t, 't')

            
    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}text' and event == "end":
        
        t = elem.text
        if not t:
            continue

        t = t.lower()

        toks = t.split(' ')
        
        for w in toks:
            unique_words.add(w.lower())

        t = re.sub(link_reg,'',t)
        t = re.sub(css_reg,'',t)

        content_split = t.split("==references==")
        if len(content_split) > 1:
            references = content_split[1].split("\n\n")[0]
            t = t.replace(references, '')
            add_to_index(references, 'r')
            
        content_split = t.split("==external links==")
        if len(content_split) > 1:
            external_links = content_split[1].split("\n\n")[0]
            t = t.replace(external_links, '')
            add_to_index(external_links, 'e')

        content_split = t.split("{{infobox")
        if len(content_split) > 1:
            ibox = content_split[1]
            num_open = 1
            close_pointer = 0
            for bracket_iter in range(len(ibox)):
                if (bracket_iter+1<len(ibox)) and  (ibox[bracket_iter] == '}') and (ibox[bracket_iter+1] == '}'):
                    num_open = num_open - 1
                if (bracket_iter+1<len(ibox)) and  (ibox[bracket_iter] == '{') and (ibox[bracket_iter+1] == '{'):
                    num_open = num_open + 1
                if num_open == 0:
                    close_pointer = bracket_iter
                    break
            
            ibox = ibox[:close_pointer]
            t = t.replace(ibox, '')
            add_to_index(ibox, 'i')
        
        content_split = t.split("[[category")
        if len(content_split) > 1:
            temp = ""
            for i in range(len(content_split)):
                if i == 1:
                    continue
                cate = content_split[i]
                if (len(cate)>0) and (cate[0]!=':'):
                    break
                
                t = t.replace(cate, '')
                temp = temp + " " + cate
            add_to_index(temp, 'c')

        t = re.sub(comment_sq, ' ', t)
        add_to_index(t, 'b')
    
    step = step + 1
    if step%20000 == 0:
        print(step)


with open(saving_path,'w+') as f:
    f.write(json.dumps(index))
    f.close()

with open(stat_path,'w+') as f:
    f.write(str(len(unique_words)) + "\n" + str(len(index)))
    f.close()

print("unique tokens = ",len(unique_words))
print("time taken = ", time.time()-start_time)
print(len(index))