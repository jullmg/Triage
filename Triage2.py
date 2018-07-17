'''Version : 2.1 '''

#Changelog

# 1.8 : Integre les expressions regulieres
# 2.0 : Integre les requetes API sur themoviedb.org
# 2.1 : Classe les films par genre

#a faire :

    # Faire un log decent
    # Download subtitles
    # Classification par genre
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

        self._prefixe, self._extension = os.path.splitext(self._nom_fichier)

        self._purgatoire = '{}\purgatoire\{}'.format(source, self._nom_fichier)

        self.indesirables = ['.txt', '.nfo', '.jpg', '.sfv', '.ini', '.png', '.ts', 'sample', 'Sample']
        # On remplace les points, tirets et les underscores par des espaces

    def classify(self):

        titre = None
        type = None
        movie_year = None
        season_episode = None
        genre = None

        # On detecte si c'est une serie televisee en detectant le pattern S01E02
        season_episode = re.search(r"[Ss]\d\d[Ee]\d\d", self._nom_fichier)

        # Si oui l'item sera DEFINITIVEMENT considere comme une serie
        if season_episode:

            type = 'Serie'

            index_debut, index_fin = season_episode.span()

            season_episode = season_episode.group()
            season_episode = season_episode.upper()

            titre = self._nom_fichier[:(index_debut - 1)]
            titre = self.purify(titre)
            titre = string.capwords(titre)
            if debug:
                print('Regex detecte', titre, type)

            # On contre-verifie sur TMDB
            titre_verifie = self.verify(titre)

            # S'il retourne positif on remplace les donnees par celles recoltees
            if titre_verifie:
                titre, type = titre_verifie

            self.move_file(titre, type, season_episode)

        # Si aucunes series detectees, on detecte un film en trouvant une annee entre 1920 et 2029
        if titre == None:
            movie_year = re.search(r"(19[2-9][0-9]|20[0-2][0-9])", self._nom_fichier)

        # S'il detecte une annee il pourra etre change pour une serie avec verification TMDB
        if movie_year:

            type = "Film"

            index_debut, index_fin = movie_year.span()

            movie_year = movie_year.group()

            titre = str(self._nom_fichier[:index_debut - 1])
            titre = self.purify(titre)
            titre = string.capwords(titre)

            if debug:
                print('Regex detecte', titre, type)

            titre_verifie = self.verify(titre)

            # S'il trouve sur TMDB on remplace
            if titre_verifie:
                titre, type, movie_year, genre = titre_verifie

            # Si ca ne fonctionne pas on essaie la recherche recursive
            else:
                recherche_recursive = self.recursive_verify(titre)
                # S'il trouve, on remplace
                if recherche_recursive:
                    titre, type = recherche_recursive


            titre = titre.replace(':', ' ')

            # On deplaces avec les valeurs finales
            self.move_file(titre, type, None, movie_year, genre)

        # Si les regex n'ont pas trouve de series ou film on fait une recherche recursive sur tmdb.org
        if titre == None:
            purified_name = self.purify(self._nom_fichier)
            self.recursive_verify(purified_name)

        # Si rien ne fonctionne on envoie au purgatoire
        if type == None and self._nom_fichier != os.path.basename(
                __file__) and self._extension not in self.indesirables:

            print('Type non-detecte, au purgatoire: ' + self._nom_fichier)

            if simulation == False:
                rename(self._path_complet, path.join(dossier_purgatoire, self._nom_fichier))

    def purify(self, titre):

        titre = titre.replace('.', ' ')
        titre = titre.replace('_', ' ')
        titre = titre.replace('-', ' ')

        return titre

    def verify(self, valeur_recherche):

        # L'index des genre_ids sur tmdb.org
        genre_ids = {28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime', 99: 'Documentary',
                     18: 'Drama', 14: 'Fantasy', 27: 'Horor', 36: 'History', 878: 'Science Fiction', 10752: 'War',
                     10749: 'Romance'}

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



                if debug:
                    print('themoviedb.org detecte {} {} '.format(serie_title, type_detecte))

                resultat_recherche_api = (serie_title, type_detecte)

                return resultat_recherche_api

            elif resultat_0['media_type'] == 'movie':

                type_detecte = 'Film'

                release_date = resultat_0['release_date']
                release_year = release_date[:4]
                movie_title = resultat_0['title']
                genre_id = resultat_0['genre_ids']
                genre_id = genre_id[0]
                genre = genre_ids[genre_id]

                if debug:
                    print('themoviedb.org detecte {} {} '.format(type_detecte, movie_title, release_year))

                resultat_recherche_api = (movie_title, type_detecte, release_year, genre)
                return resultat_recherche_api

            elif resultat_0['media_type'] == 'person':
                if debug:
                    print('Aucun resultat trouve sur themoviedb.org')
                return None

        else:
            if debug:
                print('Aucun resultat trouve sur themoviedb.org')
            return None

    def recursive_verify(self, valeur_recherche):

        resultat_regex_01 = re.search(r'[a-zA-Z]+\s', valeur_recherche)
        resultat_regex_02 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+', valeur_recherche)
        resultat_regex_03 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+', valeur_recherche)
        resultat_regex_04 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+', valeur_recherche)
        resultat_regex_05 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+', valeur_recherche)
        resultat_regex_06 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+',
                                      valeur_recherche)

        resultat_final = None

        while True:

            if resultat_regex_01:
                if debug:
                    print(resultat_regex_01.group())
                resultat_verify = self.verify(resultat_regex_01.group())

                if resultat_verify:
                    resultat_final = resultat_verify
                else:
                    break

            if resultat_regex_02:
                if debug:
                    print(resultat_regex_02.group())
                resultat_verify = self.verify(resultat_regex_02.group())

                if resultat_verify:
                    resultat_final = resultat_verify
                else:
                    break

            if resultat_regex_03:
                if debug:
                    print(resultat_regex_03.group())
                resultat_verify = self.verify(resultat_regex_03.group())

                if resultat_verify:
                    resultat_final = resultat_verify
                else:
                    break

            if resultat_regex_04:
                if debug:
                    print(resultat_regex_04.group())
                resultat_verify = self.verify(resultat_regex_04.group())

                if resultat_verify:
                    resultat_final = resultat_verify
                else:
                    break

            if resultat_regex_05:
                if debug:
                    print(resultat_regex_05.group())
                resultat_verify = self.verify(resultat_regex_05.group())
                if resultat_verify:
                    resultat_final = resultat_verify
                else:
                    break

            if resultat_regex_06:
                if debug:
                    print(resultat_regex_06.group())
                resultat_verify = self.verify(resultat_regex_06.group())
                if resultat_verify:
                    resultat_final = resultat_verify
            else:
                break

        if resultat_final:
            if debug:
                print('Recherche recursive retourne', resultat_final)
            return resultat_final


        else:
            if debug:
                print('Recherche recursive ne retourne rien')
            return None

    def move_file(self, titre, type, season_episode=None, movie_year=None, genre=None):

        if type == 'Serie':

            # nom final du fichier
            if season_episode:
                series_complete_title = '{} {}{}'.format(titre, season_episode, self._extension)
            else:
                episode_number = 1
                series_complete_title = '{} E01{}'.format(titre, self._extension)

            # sous dossier de saison
            if season_episode:
                seasons_folder = 'Season {}'.format(season_episode[1:3])
            else:
                seasons_folder = 'Season 01'

            # path complet de destination pour l'item
            series_pathto = os.path.join(dossier_series, titre, seasons_folder, series_complete_title)

            if os.path.isfile(series_pathto):
                while True:

                    episode_number += 1

                    if episode_number < 10:
                        episode_number_str = '0' + str(episode_number)
                    else:
                        episode_number_str = episode_number

                    series_complete_title = '{} {}{}'.format(titre, episode_number_str, self._extension)

                    series_pathto = os.path.join(dossier_series, titre, seasons_folder, series_complete_title)

                    if not os.path.isfile(series_pathto):
                        break



            # Si le dossier qui contient la saison n'existe pas, on le cree et finalement on deplace vers celui-ci
            path_dossier_season = os.path.join(dossier_series, titre, seasons_folder)
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

        if type == 'Film':

            # Nom final du fichier
            title_final = '{} {}{}'.format(titre, movie_year, self._extension)

            # dossier destination pour le films, dependant du genre
            if genre:
                path_final = '{}\{}'.format(dossier_films,genre)

            # Si aucun genre, on envoie dans Other
            else:
                path_final = '{}\Other'.format(dossier_films)

            #Creation du dossier de genre si inexistant
            if not os.path.isdir(path_final):
                print('Creation du dossier', path_final)

                if not simulation:
                    os.mkdir(path_final)

            movies_pathto = ('{}\{}'.format(path_final, title_final))

            # Deplacement du film vers le dossier film
            print(self._path_complet + ' --> ' + movies_pathto)

            if simulation == False:
                rename(self._path_complet, movies_pathto)

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

##################################################################################
debug = False

# Mode simulation = Aucunes manipulations sur les fichiers
simulation = False
##################################################################################

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

#Creation du dossier films s'il est manquant
if not os.path.isdir(dossier_films):

    print('Creation du dossier {}'.format(dossier_films))
    if simulation == False:

        os.makedirs(dossier_films)

#iteration recursive dans l'arborescence source
for racine, directories, fichiers in root:

    for fichier in fichiers:

        #On determine si le dossier racine contient du materiel deja classe dans les dossiers de base
        parse_dossier_racine = re.search(r"\\(Series|Films|Purgatoire)", racine)

        #Si le parse ne retourne rien on process l'item
        if  parse_dossier_racine == None:

            individu = Item_to_process(fichier, racine)

            # Purge des fichiers indesirables
            individu.purge()

            if (individu._extension not in individu.indesirables):
                if (individu._prefixe not in individu.indesirables):
                    individu.classify()

#On fait le menage des dossiers vides
for dossier in os.listdir(source):

    path_dossier = path.join(source, dossier)

    if dossier not in dossiers_base and os.path.isdir(path_dossier):

        print('Supression du dossier ' + (os.path.join(source, dossier)))

        if simulation == False:

            shutil.rmtree(os.path.join(source, dossier))









