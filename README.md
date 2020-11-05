# IAetLangue
Conception et implémentation d’un système de questions réponses en langue naturelle sur des données structurées

# Executer

```bash
python3 tp3.py
```

# Comment ca marche

Les grandes étapes:
- Récupérer les questions du fichier *question.xml*
- Séparer chaque mots en un token
- Tagger ces tokens
- En extraire des d'entités nommées
- Récupérer le [QQOQCCP](https://fr.wikipedia.org/wiki/QQOQCCP) 
- Recupérer l'entité dans la base DBpedia à l'aide du QQOQCCP et des entités nommées
- Récupérer le dbo ou dbp dans le fichier *relations.txt* en selectionnant celui qui a le plus de similarité avec n'importe quel token de la question
- Requeter DBpedia avec notre entité et notre dbo/dbp
- Analyse de la réponse 
> :warning: Dépendant des états de service des api de dbpedia