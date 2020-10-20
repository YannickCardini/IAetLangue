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
import json

url = Path(os.getcwd())

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def getBestWords(nodes,intWord):
    res = None
    if len([x for x in nodes if x[0] is None]) == len(nodes):
        return( "_".join([i[1] for i in nodes]))
    else:
        if intWord == "who" or intWord == "Who":
            res = [y for x,y in nodes if x == "PERSON" ]
            if len(res) == 0:
                return nodes[0][1]
            return res[0]
        elif intWord == "when" or intWord == "When":
            res = [y for x,y in nodes if x == "DATE" ]
            if len(res) == 0:
                return nodes[0][1]
            return res[0]


def getNodes(parent,intWord):
    lbwd = []
    for node in parent:
        if type(node) is nltk.Tree:
            if (node[0][1] == "NNP" or node[0][1] == "NNPS") and node[0][0] != "Which":
                label = node.label()
                words = ""
                for word in node.leaves():
                    words += word[0] + " "
                lbwd.append((label,words))
            getNodes(node,intWord)
        else:
            if(node[1] == "NNP" or node[1] == "NNPS"):
                lbwd.append((None,node[0]))
    if len(lbwd) > 1:
        return getBestWords(lbwd,intWord)
    elif len(lbwd) == 1:
        return lbwd[0][1]
    else:
        return None

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
        return ""
    resp = requests.get("https://lookup.dbpedia.org/api/search/PrefixSearch?&MaxHits=1&QueryString=" + queryString, headers={'Accept': 'application/json'})
    tree = ET.fromstring(resp.content)
    for child in tree:
        for element in child:
            if(element.tag == "URI"):
                return element.text.split("/")[-1]
    return ""
    
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
        if( similarity > 0.7):
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
    if(len(similarity) == 0):
        return None
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
    if len(dbos) > 1:
        dbo = max(dbos,key=lambda item:item[1])[0]
    else:
        dbo = dbos[0][0]        
    return dbo

def getResp(q1):
    res = []
    try:
        json_dictionary = json.loads(q1)
    except:
        print('\033[91m',"Echec de la requête:\n",q1,'\033[0m')
        return []
    bindings = json_dictionary["results"]["bindings"]
    for uri in bindings:
        res.append(uri["uri"]["value"])
    return res

questionXML = url / "questions.xml"
tree = ET.parse(os.path.join(questionXML))
root = tree.getroot()
questions = []

for child in root:
    for question in child:
        gold_standard_answers = []
        if(question.tag == 'string' and question.attrib['lang'] == 'en'):
            questions.append(question.text)
            tokens = word_tokenize(question.text)
            tagged = nltk.pos_tag(tokens)
            entities = nltk.chunk.ne_chunk(tagged)
            intWord = getInterrogativeWord(question.text)
            word = getNodes(entities,intWord)
            dbo = getdbo(tokens)
            q1 = "PREFIX dbo: <http://dbpedia.org/ontology/> PREFIX res: <http://dbpedia.org/resource/> SELECT DISTINCT ?uri WHERE { res:" + getKeyword(word) + " dbo:" + dbo + " ?uri .}"   
            resp = getResp(query(q1))
        if(question.tag == 'answers'):
            for answer in question:
                for uri in answer:
                    gold_standard_answers.append(uri.text)
    print(questions[-1])
    print("dbo:",dbo)
    print("Word(s): ", getKeyword(word))
    print("Reponse: ",resp)
    nb_bonne_reponse = [(x == y) for x, y in zip(resp, gold_standard_answers)].count(True)
    print("Nombre de bonnes réponses: ",nb_bonne_reponse,"\n")     