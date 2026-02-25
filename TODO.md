
Fix automatic release https://batsov.com/articles/2025/02/27/automate-the-creation-of-github-releases/


- Filter using >, <, etc 
- List of typical ignore files
- Map to apply post-processing
- Reduce, eg to create a count of ID
- How can I only filter the directory that have this pattern? "PCP-19-20-AA-BB"
- Split - and get part with cap and other part with no cap
- General patterns of first LETTER
- ORDERED
- YEAR
- Conditionnal if ext is md then add line_count, or count_by_ext cumulative based on file id
- Add headers for stats (eg rules, etc) so it returns a dictionnary then {} with the entries as `entries` key which is an array; add stats in the dictionnary such as the generation time, query used, time to execute, number of entries, etc. generate this once the --with-headers is provided 
- Add a --nested option so it uses a nested JSON like https://github.com/centralelyon/aquanote/blob/main/courses_demo/flat.json to return the results matching the hierarchy instead of a flat list
- file number plugin that results from a counter from 1 to N files
- Associer les résultats du match à des variables afin de pouvoir par exemple convertir l'année en champs, etc
- Combiner avec ntt afin d'avoir des modules avancés de traitement vidéos -> plugins?
- Compter le nombre de fichiers dans un dossier, éventuellement grouper par extension/un autre field

- X Sort
- X Add tests for plugins
- X Full path
- X Parent

https://pypi.org/project/flatdir/


Voir https://github.com/centralelyon/flat/
Egalement flatdir2 et flatdir3



Parse and put into the JSON information that is stored within

Ordered

00_
01_
02_

Here we talk about academic year

23-24-ABC
24-25-DEF

23-24-ABC
24-25-DEF

Extra padding with 3 zeros

000_..
001_..
002_..



Index

Parse pattern year_start, year_end
Decomposer nom/prénom avec nom en majuscule

Mettre qu'un dossier possède un fichier en particulier (has txt) donc faire remonter à la hierarchie

Par

git tag v0.0.3 && git push --tags && python -m build

