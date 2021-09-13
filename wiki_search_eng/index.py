import time
import xml.etree.ElementTree as ET
import re
import pickle
import sys
import os
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
digit_list = ['0','1','2','3','4','5','6','7','8','9']
index_tokens_unique = set()

all_dict = {}


def make_dict():
    for i in range(36):
        first_char = chr(ord("a")+i)

        if i > 25:
            first_char = chr(ord("0")+ i - 26)
        
        all_dict[first_char] = {}

        for j in range(36):
            second_char = chr(ord("a")+j)
            if j > 25:
                second_char = chr(ord("0")+ j - 26)
            
            two_char = first_char + second_char
            all_dict[two_char] = {}

def add_to_index(t,key):
    
    word_tokens = re.findall(token_reg,t)
    temp = {}
    for w in word_tokens:
        if (w in stop_words) or (w[-3:] in extension_set) or (len(w) > 15) or (w.isnumeric()):
            continue
        stemmed = snow_stemmer.stemWord(w)
        if stemmed not in temp:
            temp[stemmed] = 1
        else:
            temp[stemmed] = temp[stemmed] + 1
    
    for w in temp:

        if len(w) == 1:
            index_tokens_unique.add(w)
            if w not in all_dict[w]:
                all_dict[w][w] = {}
            
            if key not in all_dict[w][w]:
                all_dict[w][w][key] = {}
            
            all_dict[w][w][key][docID] = temp[w]
            continue
        
        first_char = w[0]
        second_char = w[1]

        two_char = first_char + second_char

        if w not in all_dict[two_char]:
            all_dict[two_char][w] = {}

        if key not in all_dict[two_char][w]:
            all_dict[two_char][w][key] = {}
            
        all_dict[two_char][w][key][docID] = temp[w]

def write_to_file(saving_path):
    if saving_path[-1] != "/":
        saving_path = saving_path + "/"
    
    for key in list(all_dict.keys()):
        index = {}
        file_path = saving_path + key + ".json"
        if os.path.isfile(file_path):
            f = open(file_path,'r')
            index = json.load(f)
            f.close()
        
        for w in all_dict[key]:
            if w not in index:
                index[w] = {}

            for context_key in list(all_dict[key][w]):
                if context_key not in index[w]:
                    index[w][context_key] = {}
                
                try:
                    for stored_ids in list(all_dict[key][w][context_key]):
                        index[w][context_key][stored_ids] = all_dict[key][w][context_key][stored_ids]
                except:
                    print(w,context_key,docID)
        
        if len(list(all_dict[key].keys())) == 0:
            continue
        f = open(file_path,'w+')
        f.write(json.dumps(index))
        f.close()


docID = 0
step = 0
unique_words = set()

dump_path = sys.argv[1]
saving_path = sys.argv[2]

make_dict()

for event,elem in iter(ET.iterparse(dump_path, events=("start", "end"))):

    if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page' and event == "start":
        docID = docID + 1

        # if docID%500 == 0:
        #     write_to_file(saving_path)

        #     for key in all_dict:
        #         all_dict[key] = {}
        
        if docID%1000 == 0:
            print(docID)
    
    if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}title' and event == "end":
        # docID = docID + 1
        t = elem.text
        if not t:
            continue

        t = t.lower()

        toks = t.split(' ')
        
        for w in toks:
            unique_words.add(w)
        
        t = re.sub(link_reg,' ',t)
        t = re.sub(css_reg,' ',t)
        t = re.sub(comment_sq, ' ', t)
        
        add_to_index(t, 't')

            
    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}text' and event == "end":
        
        t = elem.text
        if not t:
            continue

        t = t.lower()

        toks = t.split(' ')
        
        for w in toks:
            unique_words.add(w.lower())

        t = re.sub(link_reg,' ',t)
        t = re.sub(css_reg,' ',t)

        content_split = t.split("==references==")
        if len(content_split) > 1:
            references = content_split[1].split("\n\n")[0]
            t = t.replace(references, ' ')
            add_to_index(references, 'r')
            
        content_split = t.split("==external links==")
        if len(content_split) > 1:
            external_links = content_split[1].split("\n\n")[0]
            t = t.replace(external_links, ' ')
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
            t = t.replace(ibox, ' ')
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
                
                t = t.replace(cate, ' ')
                temp = temp + " " + cate
            add_to_index(temp, 'c')

        t = re.sub(comment_sq, ' ', t)
        add_to_index(t, 'b')


# with open(saving_path,'w+') as f:
#     f.write(json.dumps(index))
#     f.close()

write_to_file(saving_path)

print("unique tokens = ",len(unique_words))
print("time taken = ", time.time()-start_time)
print(len(index_tokens_unique))