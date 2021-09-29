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
all_dict_keys = []
title_dict = {}
title_dump_number = 1

def make_dict():
    global all_dict
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

            for k in range(36):
                third_char = chr(ord("a")+k)
                if k > 25:
                    third_char = chr(ord("0")+ k - 26)
                
                three_char = first_char + second_char + third_char
                all_dict[three_char] = {}
    
    for i in all_dict.keys():
        all_dict_keys.append(i)

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
        w = str(w)
        if (len(w) == 1) or (len(w) == 2):
            
            if w not in all_dict[w]:
                all_dict[w][w] = {}
            
            if key not in all_dict[w][w]:
                all_dict[w][w][key] = {}
            
            all_dict[w][w][key][docID] = temp[w]
            continue
        
        two_char = w[0] + w[1] + w[2]

        if w not in all_dict[two_char]:
            all_dict[two_char][w] = {}

        if key not in all_dict[two_char][w]:
            all_dict[two_char][w][key] = {}
            
        all_dict[two_char][w][key][docID] = temp[w]

def write_to_file(saving_path):
    global all_dict
    if saving_path[-1] != "/":
        saving_path = saving_path + "/"
    
    for key in all_dict_keys:
        if not all_dict[key]:
            continue

        file_key_path = saving_path + key
        if os.path.isfile(file_key_path):
            f = open(file_key_path,'r')
            stored_index = json.load(f)
            f.close()

            for w in all_dict[key].keys():
                if w not in stored_index:
                    stored_index[w] = all_dict[key][w]
                    continue
                for field_key in all_dict[key][w].keys():
                    if field_key not in stored_index[w]:
                        stored_index[w][field_key] = all_dict[key][w][field_key]
                        continue
                    for stored_docIDs in all_dict[key][w][field_key]:
                        stored_index[w][field_key][stored_docIDs] = all_dict[key][w][field_key][stored_docIDs]
            
            f = open(file_key_path,'w')
            f.write(json.dumps(stored_index, indent=0, separators=(",", ":")).replace("\n", ""))
            f.close()
        
        else:
            f = open(file_key_path,'w')
            f.write(json.dumps(all_dict[key], indent=0, separators=(",", ":")).replace("\n", ""))
            f.close()


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
if saving_path[-1] != "/":
    saving_path = saving_path + "/"

make_dict()

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

        if docID%60000 == 0:
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
        
        if docID%50000 == 0:
            write_to_file(saving_path)
            all_dict = {}
            for keys_all in all_dict_keys:
                all_dict[keys_all] = {}
    
    if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page' and event == "end":
        elem.clear()


write_to_file(saving_path)
write_title_dict()

print("time taken = ", time.time()-start_time)

print(docID)
f = open("progress_file.txt",'w')
f.write(str(docID))
f.close()

list_of_file_names = os.listdir(saving_path)

list_of_file_names.sort()

times_split = {}
start_word = {}
total_size = 0
benchmark = int(30*1000*1000)
count = 0

for file_name in list_of_file_names:

    this_file_name = saving_path + file_name
    if (len(file_name) > 2) and (file_name[0] == 't') and (file_name[1] == '_'):
        continue

    if (len(file_name) == 1) or ((len(file_name) == 2)): 
        continue
    size = int(os.path.getsize(this_file_name))
    total_size = total_size + size

    number_splits_req = -1
    if size > benchmark:
        count = count + 1
        number_splits_req = 2 * size // benchmark + 1
        
        f = open(this_file_name,'r')
        word_index = json.load(f)
        f.close()

        word_list = list(word_index.keys())
        word_list.sort()

        number_words_in_each_split = len(word_list) // number_splits_req
        left_over = len(word_list) % number_splits_req

        for i in range(number_splits_req):
            new_dict = {}
            for j in range(number_words_in_each_split):
                cur_index = number_words_in_each_split*i + j
                cur_word = word_list[cur_index]
                new_dict[cur_word] = word_index[cur_word]
            
            new_saving_path = saving_path + file_name + "_" + str(i)
            f = open(new_saving_path,'w')
            f.write(json.dumps(new_dict, indent=0, separators=(",", ":")).replace("\n", ""))
            f.close()

            try:
                new_dict_keys = list(new_dict.keys())
                new_dict_keys.sort()
                start_word[file_name + "_" + str(i)] = new_dict_keys[0]
            except:
                print(len(new_dict_keys),new_saving_path,file_name,size)
        
        os.remove(this_file_name)

    times_split[file_name] = str(number_splits_req)

print(total_size,count)
f = open("./" + "times_split.txt",'w')
f.write(json.dumps(times_split, indent=0, separators=(",", ":")).replace("\n", ""))
f.close()

f = open("./" + "first_word.txt",'w')
f.write(json.dumps(start_word, indent=0, separators=(",", ":")).replace("\n", ""))
f.close()