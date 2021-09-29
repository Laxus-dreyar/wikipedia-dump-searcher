import sys
import json
import pickle
import re
import math
import Stemmer
import heapq
import time

snow_stemmer = Stemmer.Stemmer('english')
f = open("./stopwords.pickle",'rb')
stop_words = pickle.load(f)
stop_words = set(stop_words)
f.close()

f = open("times_split.txt",'r')
times_split = json.load(f)
f.close()

f = open("first_word.txt",'r')
start_words = json.load(f)
f.close()

f = open("./progress_file.txt",'r')
number_docs = int(f.readline())
f.close()

index_path = sys.argv[1]
if index_path[-1] != "/":
    index_path = index_path + "/"

token_reg = re.compile(r'[A-Za-z0-9]+')
term_keys = ['t','b','c','l','i','r']

weights_for_terms = {}
for i in term_keys:
    weights_for_terms[i] = 1

weights_for_terms['t'] = 20
weights_for_terms['i'] = 7
field_queries = {}


def parse_query(query):
    field_queries = {}
    split_query = query.split(':')
    if len(split_query) == 1:
        field_queries['n'] = []
        query1 = str(query)
        query1 = query1.lower()
        query2 = query1.split(' ')
        for i in query2:
            if (i in stop_words) or (i == ""):
                continue
            w = snow_stemmer.stemWord(i)
            field_queries['n'].append(w)
    
    else:
        for i in range(len(split_query)-1):
            key = split_query[i][-1]
            if key not in field_queries:
                field_queries[key] = []

            if i == len(split_query) - 2:
                temp_list = split_query[i+1].split(' ')
                for w in temp_list:
                    w = w.lower()
                    if (w in stop_words) or (w == ""):
                        continue
                    w1 = snow_stemmer.stemWord(w)
                    field_queries[key].append(w1)
                continue
                
            temp_list = split_query[i+1][:-1].split(' ')
            for w in temp_list:
                w = w.lower()
                if (w in stop_words) or (w == ""):
                    continue
                w1 = snow_stemmer.stemWord(w)
                field_queries[key].append(w1)
        
    return field_queries

def get_ranked_heap(relevant_docs,n):
    ranked_docs = []
    final_docs = []
    
    i = 0
    for docID in relevant_docs:
        heapq.heappush(ranked_docs, (relevant_docs[docID],docID))
        i = i + 1
        if i > n:
            x = heapq.heappop(ranked_docs)
    
    # print(len(ranked_docs))
    for i in range(n):
        final_docs.append(heapq.heappop(ranked_docs)[1])
        if len(ranked_docs) == 0:
            break
    
    final_docs = final_docs[::-1]
    return final_docs


def get_results(query):
    field_queries = parse_query(query)
    if 'n' not in field_queries:
        relevant_docs = {}
        times_repeated = {}
        for key in list(field_queries.keys()):
            temp_list = field_queries[key]
            for w in temp_list:
                try:
                    if (len(w) == 1) or (len(w) == 2):
                        f = open(index_path + str(w),'r')
                        index = json.load(f)
                        f.close()
                        
                        if w not in index:
                            continue

                        idf = math.log(number_docs/len(index[w][key]))
                        for docID in index[w][key]:
                            if docID not in relevant_docs:
                                relevant_docs[docID] = 0
                            if docID not in times_repeated:
                                times_repeated[docID] = 0
                            times_repeated[docID] = times_repeated[docID] + 1
                            relevant_docs[docID] = math.log(index[w][key][docID] + 1) * idf * weights_for_terms[key]
                        
                        continue
                    
                    first_char = w[0]
                    second_char = w[1]
                    third_char = w[2]


                    two_char = first_char + second_char + third_char
                    index = {}
                    if str(times_split[two_char]) == str(-1):
                        f = open(index_path + str(two_char),'r')
                        index = json.load(f)
                        f.close()

                    else:
                        number_times_split = int(times_split[two_char])
                        for possible_idno in range(number_times_split):
                            possible_file_name = two_char + "_" + str(possible_idno)
                            possible_start_word = str(start_words[possible_file_name])
                            if w < possible_start_word or possible_idno == int(times_split[two_char]) -1 :
                                f = open(index_path + possible_file_name,'r')
                                index = json.load(f)
                                f.close()
                                break
                    
                    if w not in index:
                        continue
                        
                    idf = math.log(number_docs/len(index[w][key]))

                    for docID in index[w][key]:
                        if docID not in relevant_docs:
                            relevant_docs[docID] = 0
                        if docID not in times_repeated:
                            times_repeated[docID] = 0
                        times_repeated[docID] = times_repeated[docID] + 1
                        relevant_docs[docID] = relevant_docs[docID] + math.log(index[w][key][docID] + 1) * idf * weights_for_terms[key]
                except:
                    continue
        for docIDs in relevant_docs:
            relevant_docs[docIDs] = relevant_docs[docIDs] * (times_repeated[docIDs] + 1) * (times_repeated[docIDs] + 1)

        final_docs = get_ranked_heap(relevant_docs,10)
        final_return_list = []
        for i in final_docs:
            file_num = (int(i) // 60000) + 1
            file_path = index_path +"t_d" + str(file_num) + ".txt"
            f = open(file_path,'r')
            t_dict = json.load(f)
            f.close()
            final_return_list.append(str(i)+',' + " " + t_dict[str(i)])
        return final_return_list
    
    else:
        temp_list = field_queries['n']
        relevant_docs = {}
        times_repeated = {}

        for w in temp_list:

            if (len(w) == 1) or (len(w) == 2):
                f = open(index_path + str(w),'r')
                index = json.load(f)
                f.close()
                
                if w not in index:
                    continue
                
                for key in index[w].keys():
                    try:
                        idf = math.log(number_docs/len(index[w][key]))
                        for docID in index[w][key]:
                            if docID not in relevant_docs:
                                relevant_docs[docID] = 0
                            if docID not in times_repeated:
                                times_repeated[docID] = 0
                            times_repeated[docID] = times_repeated[docID] + 1
                            relevant_docs[docID] = math.log(index[w][key][docID] + 1) * idf * weights_for_terms[key]
                    except:
                        continue
                
                continue
            
            first_char = w[0]
            second_char = w[1]
            third_char = w[2]


            two_char = first_char + second_char + third_char
            index = {}
            if str(times_split[two_char]) == str(-1):
                f = open(index_path + str(two_char),'r')
                index = json.load(f)
                f.close()

            else:
                number_times_split = int(times_split[two_char])
                for possible_idno in range(number_times_split):
                    possible_file_name = two_char + "_" + str(possible_idno)
                    possible_start_word = str(start_words[possible_file_name])
                    if w < possible_start_word or possible_idno == int(times_split[two_char]) -1 :
                        f = open(index_path + possible_file_name,'r')
                        index = json.load(f)
                        f.close()
                        break
            
            if w not in index:
                continue
            
            for key in index[w].keys():
                try:
                    idf = math.log(number_docs/len(index[w][key]))

                    for docID in index[w][key]:
                        if docID not in relevant_docs:
                            relevant_docs[docID] = 0
                        if docID not in times_repeated:
                            times_repeated[docID] = 0
                        times_repeated[docID] = times_repeated[docID] + 1
                        relevant_docs[docID] = relevant_docs[docID] + math.log(index[w][key][docID] + 1) * idf * weights_for_terms[key]
                except:
                    continue
    
        for docIDs in relevant_docs:
            relevant_docs[docIDs] = relevant_docs[docIDs] * (times_repeated[docIDs] + 1) * (times_repeated[docIDs] + 1)

        final_docs = get_ranked_heap(relevant_docs,10)
        final_return_list = []
        for i in final_docs:
            file_num = (int(i) // 60000) + 1
            file_path = index_path + "t_d" + str(file_num) + ".txt"
            f = open(file_path,'r')
            t_dict = json.load(f)
            f.close()
            final_return_list.append(str(i)+',' + " " + t_dict[str(i)])
            # print(i,t_dict[str(i)])
        return final_return_list

queries_path = sys.argv[2]

f = open(queries_path)
queries_list = f.readlines()
f.close()

f = open('queries_op.txt','w')
f.close()

for i in queries_list:
    i = i.replace('\n',' ')
    start_time = time.time()
    final_results = get_results(i)
    final_time = time.time() - start_time

    f = open('queries_op.txt','a')
    for list_items in final_results:
        f.write(list_items + "\n")
    
    f.write(str(final_time) + "\n\n")
    f.close()



    # print("time = ", time.time() - start_time , "\n\n")
