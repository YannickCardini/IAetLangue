from urllib import request
import nltk
from nltk import word_tokenize
from nltk.tree import Tree


url = "file:///home/loubard/Documents/cabrio/tp3/questions.xml"
reponse = request.urlopen(url).read().decode('utf8')
tokens = word_tokenize(reponse)
tagged = nltk.pos_tag(tokens[322:326])
entities = nltk.chunk.ne_chunk(tagged)
print(entities)
for i in entities:
    if type(i) == Tree:
        print(i)


