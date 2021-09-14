import sys
import json
import pickle
import re
import Stemmer

index_path = sys.argv[1] + "/index.txt"
snow_stemmer = Stemmer.Stemmer('english')
f = open("./stopwords.pickle")



tok_reg = re.compile(r'[A-Za-z0-9]+')


query = sys.argv[2]
query = re.sub('.:','',query)
query1 = query.lower()
word_tokens = re.findall(tok_reg,query1)

dict1 = {}


for w in word_tokens:
    w1 = snow_stemmer.stem(w)
    dict1[w] = {}

    if w1 not in index:
        dict1[w]["title"] = []
        dict1[w]["body"] = []
        continue
    
    if "t" not in index[w1]:
        dict1[w]["title"] = []
    else:
        dict1[w]["title"] = list(index[w1]["b"].keys())
    
    if "b" not in index[w1]:
        dict1[w]["body"] = []
    else:
        dict1[w]["body"] = list(index[w1]["b"].keys())
    

    # print(dict1[w]["title"])


print(json.dumps(dict1))