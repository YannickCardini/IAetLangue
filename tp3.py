from urllib import request
import nltk
from nltk import word_tokenize
from nltk.tree import Tree
import re
import xml.etree.ElementTree as ET
import requests
from difflib import SequenceMatcher
import os
from pathlib import Path
from nltk.corpus import wordnet as wn

url = Path(os.getcwd())

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def getNodes(parent):
    for node in parent:
        if type(node) is nltk.Tree:
            if node.label() != 'ROOT' and (node[0][1] == "NNP" or node[0][1] == "NNPS") and node[0][0] != "Which":
                label = node.label()
                words = ""
                for word in node.leaves():
                    words += word[0] + " "
                return (label,words)
            getNodes(node)
        else:
            if(node[1] == "NNP" or node[1] == "NNPS"):
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
    
def getRelations():
    dbo = []
    dbp = []
    fs = open(url / "relations.txt",'r')  
    for line in fs.readlines():
        db, relation = line.split(":")
        if(db == "dbo"):
            dbo.append(re.sub("\n", "", relation))
        else:
            dbp.append(re.sub("\n", "", relation))
    return (dbo,dbp)

def getBestSimilarity(token):
    if(token == None):
        return None
    dbo, dbp = getRelations()
    for db in dbo + dbp:
        similarity = similar(token,db)
        if( similarity > 0.6):
            return db,similarity
    return None

def getPathSimilarity(token):
    if(token == None):
        return None
    tokenSyn = wn.synsets(token)
    if(len(tokenSyn) == 0):
        return None
    similarity = [] 
    dbo, dbp = getRelations()
    for db in dbo + dbp:
        dbSyn = wn.synsets(db)
        if(len(dbSyn) > 0):
            simTuple = (db,tokenSyn[0].path_similarity(dbSyn[0]))
            if(simTuple[1] != None):
                similarity.append(simTuple)
    dbo = max(similarity,key=lambda item:item[1])
    return dbo


def getdbo(tokens):
    dbo = None
    dbos = []
    for token in tokens:
        dbos.append(getBestSimilarity(token))
    dbos = [i for i in dbos if i]#Remove None
    if len(dbos) == 0:
        for token in tokens:
            dbos.append(getPathSimilarity(token))
        dbos = [i for i in dbos if i]#Remove None
        print(dbos)
    if len(dbos) > 1:
        dbo = max(dbos,key=lambda item:item[1])[0]
    else:
        dbo = dbos[0][0]        
    return dbo

questionXML = url / "questions.xml"
tree = ET.parse(os.path.join(questionXML))
root = tree.getroot()
questions = []

for child in root:
    for question in child:
        if(question.tag == 'string' and question.attrib['lang'] == 'en'):
            questions.append(question.text)
            tokens = word_tokenize(question.text)
            tagged = nltk.pos_tag(tokens)
            entities = nltk.chunk.ne_chunk(tagged)
            label, word = getNodes(entities)
            dbo = getdbo(tokens)
            print(question.text)
            print("dbo:",dbo)
            # print("Label: ",label)
            # print("Word(s): ", getKeyword(word))
            # intWord = getInterrogativeWord(question.text)
            q1 = "PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:" + word + " dbo:" + dbo + " ?uri .}"   
            print(query(q1))





# for db in dbo:
#     similarity = similar("cross",db)
#     if( similarity > 0.5):
#         print(db,similarity)