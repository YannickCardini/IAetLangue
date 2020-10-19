from urllib import request
import nltk
from nltk import word_tokenize
from nltk.tree import Tree
import re
import xml.etree.ElementTree as ET
import requests
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def getNodes(parent):
    for node in parent:
        print(node)
        if type(node) is nltk.Tree:
            if node.label() != 'ROOT' and node[0][1] == "NNP" and node[0][0] != "Which":
                label = node.label()
                words = ""
                for word in node.leaves():
                    words += word[0] + " "
                return (label,words)
            getNodes(node)
        else:
            if(node[1] == "NNP"):
                return (None,node[0])
    return None,None

def getInterrogativeWord(phrase):
    if(type(phrase) == list):
        phrase = " ".join(phrase)
    match = re.search('(([wW])(here|ho|hat|hich|hen))|([hH]ow)',phrase)
    if (match != None):
        return match.group()
    else:
        return None

def query(q, f='application/json'):
    try:
        params = {'query': q}
        resp = requests.get("http://dbpedia.org/sparql", params=params, headers={'Accept': f})
        return resp.text
    except Exception as e:
        print(e)
        raise

def getKeyword(queryString):
    if(queryString == None):
        return None
    resp = requests.get("https://lookup.dbpedia.org/api/search/PrefixSearch?&MaxHits=1&QueryString=" + queryString, headers={'Accept': 'application/json'})
    tree = ET.fromstring(resp.content)
    for child in tree:
        for element in child:
            if(element.tag == "URI"):
                return element.text.split("/")[-1]

url = "/home/loubard/Documents/python/cabrio/IAetLangue/"
# tree = ET.parse(url + "questions.xml")
# root = tree.getroot()
# questions = []
# for child in root:
#     for question in child:
#         if(question.tag == 'string' and question.attrib['lang'] == 'en'):
#             questions.append(question.text)
#             tokens = word_tokenize(question.text)
#             tagged = nltk.pos_tag(tokens)
#             entities = nltk.chunk.ne_chunk(tagged)
#             label, word = getNodes(entities)
#             print(question.text)
#             print("Label: ",label)
#             print("Word(s): ", getKeyword(word))
#             intWord = getInterrogativeWord(question.text)



# q1 = "PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:Goofy dbo:creator ?uri .}"   
# print(query(q1))
dbo = []
dbp = []
fs = open(url + "relations.txt",'r')  
for line in fs.readlines():
    db, relation = line.split(":")
    if(db == "dbo"):
        dbo.append(re.sub("\n", "", relation))
    else:
        dbp.append(re.sub("\n", "", relation))

for db in dbo:
    similarity = similar("cross",db)
    if( similarity > 0.5):
        print(db,similarity)