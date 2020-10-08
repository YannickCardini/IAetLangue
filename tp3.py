from urllib import request
import nltk
from nltk import word_tokenize
from nltk.tree import Tree
import re
import xml.etree.ElementTree as ET

def getNodes(parent):
    for node in parent:
        if type(node) is nltk.Tree:
            if node.label() != 'ROOT':
                label = node.label()
                word = node.leaves()[0][0]
                print ("Label:", label)
                print ("Word:", word)
                return (label,word)
            getNodes(node)
    return None,None

def getInterrogativeWord(phrase):
    if(type(phrase) == list):
        phrase = " ".join(phrase)
    match = re.search('(([wW])(here|ho|hat|hich|hen))|([hH]ow)',phrase)
    if (match != None):
        return match.group()
    else:
        return None

url = "/home/loubard/Documents/python/cabrio/IAetLangue/questions.xml"
tree = ET.parse(url)
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
            print(question.text)
            intWord = getInterrogativeWord(question.text)


    


