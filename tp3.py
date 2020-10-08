from urllib import request
import nltk
from nltk import word_tokenize
from nltk.tree import Tree
import re

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

# TODO Rajouter How dans le regex
def getInterrogativeWord(phrase):
    if(type(phrase) == list):
        phrase = " ".join(phrase)
    match = re.search('([wW])(here|ho|hat|hich|hen)',phrase)
    return match.group()

# TODO Changer la facon de lire le fichier XML 
url = "file:///home/loubard/Documents/python/cabrio/IAetLangue/questions.xml"
reponse = request.urlopen(url).read().decode('utf8')
tokens = word_tokenize(reponse)
phrase1 = tokens[325:329]
phrase2 = tokens[593:601]
phrase3 = tokens[884:892]
tagged = nltk.pos_tag(phrase3)
entities = nltk.chunk.ne_chunk(tagged)
label, word = getNodes(entities)
intWord = getInterrogativeWord(phrase2)


    


