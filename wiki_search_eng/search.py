import sys
import json
import pickle
import re
import math
import Stemmer
import heapq

snow_stemmer = Stemmer.Stemmer('english')
f = open("./stopwords.pickle",'rb')
stop_words = pickle.load(f)
stop_words = set(stop_words)
f.close()

print(len(stop_words))

f = open("./progress_file.txt",'r')
number_docs = int(f.readline())
f.close()

term_keys = ['t','b','c','l','i','r']

weights_for_terms = {}
for i in term_keys:
    weights_for_terms[i] = 1

weights_for_terms['t'] = 5
weights_for_terms['i'] = 2
print(number_docs)
field_queries = {}

query = sys.argv[1]
query_split = query.split(':')
flag = 0

def get_ranked_heap(relevant_docs):
    ranked_docs = []
    final_docs = []
    
    i = 0
    for docID in relevant_docs:
        heapq.heappush(ranked_docs, (relevant_docs[docID],docID))
        i = i + 1
        if i > 10:
            x = heapq.heappop(ranked_docs)
    
    
    for i in range(10):
        final_docs.append(heapq.heappop(ranked_docs)[1])
        if len(ranked_docs) == 0:
            break
    
    final_docs = final_docs[::-1]
    return final_docs


if len(query_split)>1:
    flag = 1
    
    for i in range(len(query_split)-1):
        key = query_split[i][-1]
        if i == len(query_split) - 2:
            field_queries[key] = query_split[i+1].split(' ')

            continue
            
        field_queries[key] = query_split[i+1][:-1].split(' ')


if flag == 1:
    relevant_docs = {}
    for key in list(field_queries.keys()):
        temp_list = field_queries[key]
        for w in temp_list:
            if w == "":
                continue
            try:
                w = w.lower()
                if w in stop_words:
                    continue
                
                w = snow_stemmer.stemWord(w)
                if len(w) == 1:
                    f = open("inverted_index/" + str(w) + ".json")
                    index = json.load(f)
                    f.close()
                    
                    if w not in index:
                        continue

                    idf = math.log(number_docs/len(index[w][key]))
                    for docID in index[w][key]:
                        if docID not in relevant_docs:
                            relevant_docs[docID] = 0
                        relevant_docs[docID] = math.log(index[w][key][docID] + 1) * idf * weights_for_terms[key]
                    
                    continue
                
                first_char = w[0]
                second_char = w[1]

                two_char = first_char + second_char

                f = open("inverted_index/" + str(two_char) + ".json")
                index = json.load(f)
                f.close()

                if w not in index:
                    continue
                    
                idf = math.log(number_docs/len(index[w][key]))

                for docID in index[w][key]:
                    if docID not in relevant_docs:
                        relevant_docs[docID] = 0
                    relevant_docs[docID] = relevant_docs[docID] + math.log(index[w][key][docID] + 1) * idf * weights_for_terms[key]

            except:
                continue
    
    print(json.dumps(field_queries,indent=4))
    print(json.dumps(relevant_docs,indent=4))

    final_docs = get_ranked_heap(relevant_docs)
    for i in final_docs:
        file_num = (int(i) // 20000) + 1
        file_path = "inverted_index/t_d" + str(file_num) + ".txt"
        f = open(file_path,'r')
        t_dict = json.load(f)
        f.close()
        print(i,t_dict[str(i)])

else:
    query_words = query.split(' ')
    relevant_docs = {}
    for w in query_words:
        if w == "":
            continue
        
        w = w.lower()
        if w in stop_words:
            continue

        w = snow_stemmer.stemWord(w)
        try:
            if len(w) == 1:
                f = open("inverted_index/" + str(w) + ".json")
                index = json.load(f)
                f.close()
                
                if w not in index:
                    continue

                for key in list(index[w].keys()):
                    idf = math.log(number_docs/len(index[w][key]))
                    for docID in index[w][key]:
                        if docID not in relevant_docs:
                            relevant_docs[docID] = 0
                        relevant_docs[docID] = math.log(index[w][key][docID] + 1) * idf * weights_for_terms[key]
                
                continue

            first_char = w[0]
            second_char = w[1]

            two_char = first_char + second_char

            f = open("inverted_index/" + str(two_char) + ".json")
            index = json.load(f)
            f.close()

            if w not in index:
                continue
            
            for key in list(index[w].keys()):

                idf = math.log(number_docs/len(index[w][key]))
                for docID in index[w][key]:
                    if docID not in relevant_docs:
                        relevant_docs[docID] = 0
                    relevant_docs[docID] = relevant_docs[docID] + math.log(index[w][key][docID] + 1) * idf * weights_for_terms[key]
            
        except:
            continue
    
    print(json.dumps(relevant_docs,indent=4))

    final_docs = get_ranked_heap(relevant_docs)
    for i in final_docs:
        file_num = (int(i) // 20000) + 1
        file_path = "inverted_index/t_d" + str(file_num) + ".txt"
        f = open(file_path,'r')
        t_dict = json.load(f)
        f.close()
        print(i,t_dict[str(i)])