from collections import Counter




my_answers = ['http://dbpedia.org/resource/Sam_Adams_Award', 'http://dbpedia.org/resource/Index_on_Censorship', 'http://dbpedia.org/resource/Amnesty_International_UK_Media_Awards', '*'] 
gold_answers = ['http://dbpedia.org/resource/Index_on_Censorship', 'http://dbpedia.org/resource/Amnesty_International_UK_Media_Awards', 'http://dbpedia.org/resource/Sam_Adams_Award']
c = Counter(my_answers)
total_count = sum(c[x] for x in gold_answers)
print(total_count)