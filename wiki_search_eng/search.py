import sys
import json
import pickle
import re
from nltk.stem.snowball import SnowballStemmer

index_path = sys.argv[1]
snow_stemmer = SnowballStemmer(language='english')
f = open(index_path,'rb')
index = json.load(f)
f.close()

tok_reg = re.compile(r'[A-Za-z0-9]+')


query = sys.argv[2]
query = re.sub('.:','',query)
query1 = query.lower()
word_tokens = re.findall(tok_reg,query1)

dict1 = {}


for w in word_tokens:
    w1 = snow_stemmer.stem(w)
    dict1[w] = {}
    dict1[w]["title"] = list(index[w1]["t"].keys())
    dict1[w]["body"] = list(index[w1]["b"].keys())

    # print(dict1[w]["title"])


print(json.dumps(dict1))