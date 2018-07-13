'''Version : 2.0 '''

#Changelog

# 1.8 : Integre les expressions regulieres
# 2.0 : Integre les requetes API sur themoviedb.org pour valider les informations de l'item.

#a faire :

    # Faire un log decent
    # Download subtitles
    # Synchronisation sur base de donnee sur le web? Pour confirmer le type de media (serie ou film) et downloader les sous-titres
    # Faire un GUI?

#Troubles :

    #Parfois un espace a la fin de la variable movie_title


import os, re, shutil, string, urllib.request, urllib.parse, json

from os import rename, path

class Item_to_process:

    def __init__(self,nom_fichier,location):

        self._nom_fichier = nom_fichier

        self._location = location

        self._path_complet = os.path.join(self._location, self._nom_fichier)

        self._prefixe, self._extension = os.path.splitext(self._path_complet)

        self._purgatoire = '{}\purgatoire\{}'.format(source, self._nom_fichier)

        self.indesirables = ['.txt', '.nfo', '.jpg', '.sfv', '.ini', '.png', '.ts']



    def classify(self):

        type_detecte = None

        try:

            # On detecte si c'est une serie televisee en detectant le pattern S01E02
            resultat_serie = re.search(r"\W[Ss]\d\d[Ee]\d\d", self._nom_fichier)

            # Si le re.search retourne un resultat on extrapole le titre
            if resultat_serie:

                type_detecte = 'Serie'

                #On determine l'index du resultat
                index_debut, index_fin = resultat_serie.span()

                series_episode = self._nom_fichier[(index_debut + 1):index_fin]

                series_episode = series_episode.upper()

                series_title = str(self._nom_fichier[:index_debut])

                # On remplace les points par des espaces
                series_title = series_title.replace('.', ' ')

                # Lettre majuscule au debut de chaque mot
                series_title = string.capwords(series_title)

                print('Les Regex retournent le type Serie et le titre ' + series_title)

                # On contre-verifie le resultat par l'API de themoviedb.org
                series_title = self.verify(series_title)

                series_complete_title = '{} {}{}'.format(series_title, series_episode, self._extension)

                seasons_folder = 'Season {}'.format(series_episode[1:3])

                #On determine le path de destination pour l'item
                series_pathto = os.path.join(dossier_series, series_title, seasons_folder, series_complete_title)

                # Si le dossier qui contient la saison n'existe pas, on le cree et finalement on deplace vers celui-ci
                path_dossier_season = os.path.join(dossier_series, series_title, seasons_folder)

                if os.path.isdir(path_dossier_season):

                    print(self._path_complet + '-->' + series_pathto)
                    if simulation == False:
                        rename(self._path_complet, series_pathto)

                else:

                    print('Creation du dossier ' + path_dossier_season)
                    print(self._path_complet + ' --> ' + series_pathto)
                    if simulation == False:
                        os.makedirs(path_dossier_season)
                        rename(self._path_complet, series_pathto)

            # Si aucunes series detectees, on detecte un film en trouvant une annee entre 1920 et 2029
            if type_detecte == None:

                resultat_film = re.search(r"\W(19[2-9][0-9]|20[0-2][0-9])", self._nom_fichier)

                #Si le re.search retourne un resultat on extrapole l'annee et le titre du film
                if resultat_film:

                    type_detecte = "Film"

                    index_debut, index_fin = resultat_film.span()

                    movie_year = self._nom_fichier[(index_debut+1):index_fin]

                    movie_title = str(self._nom_fichier[:index_debut])

                    #On remplace les points par des espaces
                    movie_title = movie_title.replace('.', ' ')

                    print('Les Regex retournent le type Film et le titre ' + movie_title)

                    # On contre-verifie le resultat par l'API de themoviedb.org
                    movie_title = self.verify(movie_title)

                    # dossier destination pour les films
                    movies_pathto = ('{}\{} ({}){}'.format(dossier_films, movie_title, movie_year, self._extension))

                    # Deplacement du film vers le dossier film
                    print(self._path_complet + ' --> ' + movies_pathto)

                    if simulation == False:

                        rename(self._path_complet, movies_pathto)

            if type_detecte == None and self._nom_fichier != os.path.basename(__file__) and self._extension not in self.indesirables:

                print('Type non-detecte, au purgatoire: ' + self._nom_fichier)

                if simulation == False:

                    rename(self._path_complet, path.join(dossier_purgatoire, self._nom_fichier))

        except Exception as erreur:

            print('Erreur lors de l\'analyse de ' + self._nom_fichier)
            print(erreur)
            pass

    def verify(self, valeur_recherche):

        # URL de base pour recherche multiple incluant films et series
        url_multi_search = 'https://api.themoviedb.org/3/search/multi?'

        search_values = {'api_key': '3282e21d33f2ff968619ab7ded55950d'}

        # On determine la recherche qui sera faite sur themoviedb.org
        search_values['query'] = valeur_recherche
        
        # Encode le dictionnaire en str (percent-encoded ASCII text string)
        search_data = urllib.parse.urlencode(search_values)

        # Encode ce string en UTF-8 (binaire)
        search_data = search_data.encode('utf-8')

        # On fait la requete URL incluant les search_values a l'API de themoviedb.org
        data_binaire = urllib.request.urlopen(url_multi_search, search_data)
        data_binaire = data_binaire.read()

        # On decode l'information encodee UTF-8
        data_string = data_binaire.decode(encoding='UTF-8', errors='strict')

        # On transforme la string JSON en dictionnaire Python
        json_data = json.loads(data_string)
        
        #On va chercher l'information si il ya des resultats
        if json_data['total_results'] > 0:

            #Cette clee du dictionnaire contient tous les resultats dans une liste
            resultats = json_data['results']

            #Le premier item de la liste est le resultat le plus 'revelant'
            resultat_0 = resultats[0]


            if resultat_0['media_type'] == 'tv':

                type_detecte = 'Serie'

                serie_title = resultat_0['original_name']

                print('themoviedb.org retourne le type {} et le titre {} '.format(type_detecte, serie_title))
                return serie_title

            elif resultat_0['media_type'] == 'movie':

                type_detecte = 'Film'

                release_date = resultat_0['release_date']
                release_year = release_date[:4]
                movie_title = resultat_0['title']

                print('themoviedb.org retourne le type {} et le titre {} '.format(type_detecte, movie_title))
                return movie_title
        else:

            return valeur_recherche
            print('Aucun resultat trouve sur themoviedb.org')
        


    def purge(self):

        if self._extension in self.indesirables and self._nom_fichier not in os.listdir('{}\purgatoire'.format(source)):

            try:

                print('supression du fichier: ' + self._nom_fichier)

                if simulation == False:
                    os.remove(self._path_complet)


            except PermissionError:

                print('erreur de permission, deplacement au purgatoire')

                if simulation == False:
                    os.rename(self._path_complet, self._purgatoire)

# Mode simulation = Aucunes manipulations sur les fichiers
simulation = True

if simulation == True:
    print('***Mode Simulation Actif***')

else:
    print('***Mode Simulation Non-Actif, des actions seront posées!!***')

source = 'd:\\downloads\\triage'

#source = os.getcwd()

dossier_films = path.join(source, 'Films')

dossier_series = path.join(source, 'Series')

dossier_purgatoire  = path.join(source, 'Purgatoire')

dossiers_base = ['Purgatoire','Films','Series']

root = os.walk(source)

#Creation du dossier purgatoire s'il est manquant
if not os.path.isdir(dossier_purgatoire):

    print('Creation du dossier {}'.format(dossier_purgatoire))
    if simulation == False:

        os.makedirs(dossier_purgatoire)

#iteration recursive dans l'arborescence source
for racine, directories, fichiers in root:

    for fichier in fichiers:

        #On determine si le dossier racine contient du materiel deja classe dans les dossiers de base
        parse_dossier_racine = re.search(r"\\(Series|Films|Purgatoire)", racine)

        #Si le parse ne retourne rien on process l'item
        if  parse_dossier_racine == None:

            individu = Item_to_process(fichier, racine)

            individu.purge()

            individu.classify()

#On fait le menage des dossiers vides
for dossier in os.listdir(source):

    path_dossier = path.join(source, dossier)

    if dossier not in dossiers_base and os.path.isdir(path_dossier):

        print('Supression du dossier ' + (os.path.join(source, dossier)))

        if simulation == False:

            shutil.rmtree(os.path.join(source, dossier))









