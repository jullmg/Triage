import urllib.request, urllib.parse, re

url = 'https://api.themoviedb.org/3/search/multi?api_key=3282e21d33f2ff968619ab7ded55950d&language=en-US&query=jaws&page=1&include_adult=false'

data = urllib.request.urlopen(url)

data_binaire = data.read()

data_string = data_binaire.decode(encoding='UTF-8',errors='strict')

print(data_string)

if 'title' in  data_string:
    print('yahoo!')