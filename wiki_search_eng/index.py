import time
import xml.etree.ElementTree as ET
import re
import pickle
import sys
import os
import Stemmer
import json

start_time = time.time()
f = open("./stopwords.pickle",'rb')
stop_words = pickle.load(f)
f.close()
stop_words = set(stop_words)


snow_stemmer = Stemmer.Stemmer('english')
token_reg = re.compile(r'[A-Za-z0-9]+')
css_reg = re.compile(r'{\|(.*?)\|}',re.DOTALL)
link_reg = re.compile(r'(https?://\S+)')
extension_set = set(['jpg','jpeg','png'])
# comment_sq = re.compile(r'(\[\[[^\[\]]*\]\])')
comment_sq = re.compile(r'({{[^{}]*?}})')
alnum_garbage = re.compile(r'[0-9]+[a-z]+[0-9a-z]*')
digit_list = ['0','1','2','3','4','5','6','7','8','9']
category_reg = re.compile(r'\[\[category:.*?\]\]')

all_dict = {}
title_dict = {}
title_dump_number = 1

def add_to_index(t,key):
    global all_dict
    global docID
    word_tokens = re.findall(token_reg,t)
    temp = {}
    for w in word_tokens:
        if (w in stop_words) or (w[-3:] in extension_set) or (len(w) > 15) or ((w[0] in digit_list) and len(w)>4):
            continue
        stemmed = snow_stemmer.stemWord(w)
        if stemmed not in temp:
            temp[stemmed] = 1
        else:
            temp[stemmed] = temp[stemmed] + 1
    
    for w in temp:

        if (len(w) == 1) or (len(w) == 2):
            if w not in all_dict:
                all_dict[w] = {}

            if w not in all_dict[w]:
                all_dict[w][w] = {}
            
            if docID not in all_dict[w][w]:
                all_dict[w][w][docID] = {}
            
            all_dict[w][w][docID][key] = temp[w]
            continue
        
        first_char = w[0]
        second_char = w[1]
        third_char = w[2]

        two_char = first_char + second_char + third_char

        if two_char not in all_dict:
            all_dict[two_char] = {}

        if w not in all_dict[two_char]:
            all_dict[two_char][w] = {}

        if docID not in all_dict[two_char][w]:
            all_dict[two_char][w][docID] = {}
            
        all_dict[two_char][w][docID][key] = temp[w]

# def write_to_file(saving_path):
#     global all_dict
#     if saving_path[-1] != "/":
#         saving_path = saving_path + "/"
    
#     for key in list(all_dict.keys()):
#         index = {}

#         temp_index_key = all_dict[key]
#         if not temp_index_key:
#             continue
#         file_path = saving_path + key + ".json"
#         if os.path.isfile(file_path):
#             f = open(file_path,'r')
#             index = json.load(f)
#             f.close()
        
#         for w in all_dict[key]:
#             if w not in index:
#                 index[w] = {}

#             for context_key in list(all_dict[key][w]):
#                 if context_key not in index[w]:
#                     index[w][context_key] = {}
                
#                 for stored_ids in list(all_dict[key][w][context_key]):
#                     index[w][context_key][stored_ids] = all_dict[key][w][context_key][stored_ids]
        
#         f = open(file_path,'w')
#         f.write(json.dumps(index, indent=0, separators=(",", ":")).replace("\n", ""))
#         f.close()

current_chunk_no = 0
def write_to_file_other():
    global all_dict
    global saving_path
    global current_chunk_no

    temp_list = []
    for file_key in all_dict.keys():
        for w in all_dict[file_key].keys():
            temp_string = str(w)
            for docID in all_dict[file_key][w].keys():
                temp_string = temp_string + " " + str(docID) + ":"
                if 'b' in all_dict[file_key][w][docID].keys():
                    temp_string = temp_string + str(all_dict[file_key][w][docID]['b']) + ","

                for key in all_dict[file_key][w][docID].keys():
                    if key == 'b':
                        continue                    
                    else:
                        if all_dict[file_key][w][docID][key] > 1:
                            temp_string = temp_string + str(key) + str(all_dict[file_key][w][docID][key])
                        else:
                            temp_string = temp_string + str(key)
            
            temp_string = temp_string
            temp_list.append(temp_string)
    
    f = open(saving_path + "index" + str(current_chunk_no),'w')
    f.writelines(temp_list)
    f.close()

    current_chunk_no = current_chunk_no + 1

def write_title_dict():
    global title_dict
    global title_dump_number
    global saving_path
    if saving_path[-1] != "/":
        saving_path = saving_path + "/"

    file_path = saving_path + "t_d" +str(title_dump_number) + ".txt"
    f = open(file_path,'w')
    # for i in title_dict:
    #     f.write(i.replace("\n","") + "\n")
    f.write(json.dumps(title_dict, indent=0, separators=(",", ":")).replace("\n", ""))
    f.close()
    title_dict = {}
    title_dump_number = title_dump_number + 1

docID = 0
step = 0

dump_path = sys.argv[1]
saving_path = sys.argv[2]

# make_dict()

for event,elem in iter(ET.iterparse(dump_path, events=("start", "end"))):
    
    if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page' and event == "start":
        docID = docID + 1

    if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}title' and event == "end":
        t = elem.text
        if not t:
            continue

        title_dict[docID] = t

        t = t.lower()
        
        t = re.sub(link_reg,' ',t)
        t = re.sub(css_reg,' ',t)
        t = re.sub(comment_sq, ' ', t)
        # t = re.sub(alnum_garbage, ' ', t)
        
        add_to_index(t, 't')

        if docID%20000 == 0:
            write_title_dict()

            
    elif elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}text' and event == "end":
        
        t = elem.text
        if not t:
            continue

        t = t.lower()

        t = re.sub(link_reg,' ',t)
        t = re.sub(css_reg,' ',t)
        t = re.sub(alnum_garbage, ' ', t)

        content_split = t.split("==references==")
        if len(content_split) > 1:
            references = content_split[1].split("\n\n")[0]
            t = t.replace(references, ' ')
            add_to_index(references, 'r')
            
        content_split = t.split("==external links==")
        if len(content_split) > 1:
            external_links = content_split[1].split("\n\n")[0]
            t = t.replace(external_links, ' ')
            add_to_index(external_links, 'l')

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

        content_split = re.findall(category_reg, t)
        temp = ""
        if len(content_split) > 0:
            for i in content_split:
                temp = temp + i + " "
                t = t.replace(i, " ")
            add_to_index(temp, 'c')
        
        t = re.sub(comment_sq, ' ', t)
        add_to_index(t, 'b')

        if docID%1000 == 0:
            print(docID)
            f = open("progress_file.txt",'w')
            f.write(str(docID))
            f.close()
        
        if docID%500 == 0:
            write_to_file_other()
            all_dict = {}
    
    if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page' and event == "end":
        elem.clear()

    

# with open(saving_path,'w+') as f:
#     f.write(json.dumps(index))
#     f.close()

write_to_file_other()
write_title_dict()

count = 0
for i in all_dict.keys():
    count = count + len(all_dict[i].keys())

print(count)
print("time taken = ", time.time()-start_time)

print(docID)
f = open("progress_file.txt",'w')
f.write(str(docID))
f.close()