#!/usr/bin/env python

'''Version : 2.2 '''

#Changelog

# 1.8 : Integre les expressions regulieres
# 2.0 : Integre les requetes API sur themoviedb.org
# 2.1 : Classe les films par genre
# 2.2 : Transfert les items sur MediaCenter après traitement

#a faire :

    # Faire un log decent
    # Download subtitles
    # Classification par genre
    # Aller chercher le nom de l'episode si c'est une serie

#Troubles :

    #Recherche recursive inclue l'extension du fichier

# Standard Library
import os
from os import path
import re
import string
import subprocess

# 3rd party packages
import shutil
import urllib.request
import urllib.parse
import json
import bs4 as bs


class Item_to_process:

    def __init__(self,nom_fichier,location):

        self._nom_fichier = nom_fichier

        self._location = location

        self._path_complet = os.path.join(self._location, self._nom_fichier)

        self._prefixe, self._extension = os.path.splitext(self._nom_fichier)

        self._Purgatoire = '{}/Purgatoire/{}'.format(source, self._nom_fichier)

        self.indesirables = ['.txt', '.nfo', '.jpg', '.sfv', '.ini', '.png', '.ts', 'sample', 'Sample']
        # On remplace les points, tirets et les underscores par des espaces

    def classify(self):

        # Declaration des variables
        titre, self.type, movie_year, season_episode, genre = (None,None,None,None,None)

        # On detecte si c'est une serie televisee en detectant le pattern S01E02
        season_episode = re.search(r"[Ss]\d\d[Ee]\d\d", self._nom_fichier)


        # Si oui l'item sera DEFINITIVEMENT considere comme une serie
        if season_episode:

            self.type = 'Serie'

            index_debut, index_fin = season_episode.span()

            season_episode = season_episode.group()
            season_episode = season_episode.upper()
            print('Season_episode = ', season_episode)

            titre = self._nom_fichier[:(index_debut - 1)]
            titre = self.purify(titre)
            titre = string.capwords(titre)
            if debug:
                print('Regex detecte', titre, self.type)

            # On contre-verifie sur TMDB
            titre_verifie = self.verify(titre)

            if titre_verifie:
                print('titre verifie:', titre_verifie)

            # S'il retourne positif on remplace les donnees par celles recoltees
            if titre_verifie:
                titre, self.type, movie_year, genre = titre_verifie
                self.move_file(titre, self.type, season_episode)

            # Si TMDB ne retourne rien on essaie IMDB
            else:
                titre_imdb = self.search_imdb(titre)
                if titre_imdb:
                    titre = titre_imdb
                    self.move_file(titre, self.type, season_episode)

            if not titre_verifie:


                titre_verifie = self.recursive_verify(titre)


        # Si aucunes series detectees, on detecte un film en trouvant une annee entre 1920 et 2029
        if titre == None:
            movie_year = re.search(r"(19[2-9][0-9]|20[0-2][0-9])", self._nom_fichier)

        # S'il detecte une annee il pourra etre change pour une serie avec verification TMDB
        if movie_year:

            self.type = "Film"

            index_debut, index_fin = movie_year.span()

            movie_year = movie_year.group()

            titre = str(self._nom_fichier[:index_debut - 1])
            titre = self.purify(titre)
            titre = string.capwords(titre)

            if debug:
                print('Regex detecte', titre, self.type)

            titre_verifie = self.verify(titre)

            # S'il trouve sur TMDB on remplace
            if titre_verifie:
                titre, self.type, movie_year, genre = titre_verifie

            # Sinon on essaie la recherche recursive
            elif not titre_verifie:
                recherche_recursive = self.recursive_verify(titre)
                # S'il trouve, on remplace
                if recherche_recursive:
                    titre, self.type, movie_year, genre = recherche_recursive

            # Si la recherche recursive ne fonctionne pas on essaie sur IMDB
            elif not recherche_recursive:
                result_search_imdb = self.search_imdb(titre)
                if result_search_imdb:
                    titre = result_search_imdb

            # On deplaces avec les valeurs finales
            self.move_file(titre, self.type, None, movie_year, genre)

        # Si les regex n'ont pas trouve de series ou film on fait une recherche recursive sur tmdb.org
        if titre == None:

            if debug:
                print('Les REGEX n\'ont pas fonctionne pour', self._nom_fichier, 'On essaie une recherche recursive')
            purified_name = self.purify(self._nom_fichier)
            titre_verifie = self.recursive_verify(purified_name)

            # S'il trouve on remplace
            if titre_verifie:

                if titre_verifie[1] == 'Film':
                    titre, self.type, movie_year, genre = titre_verifie

                    # On deplaces avec les valeurs finales
                    self.move_file(titre, self.type, None, movie_year, genre)

        # Si rien ne fonctionne on envoie au Purgatoire
        if self.type == None and self._nom_fichier != os.path.basename(
                __file__) and self._extension not in self.indesirables:

            print('Type non-detecte, au Purgatoire: ' + self._nom_fichier)

            if not simulation and operation_mode == "local":
                os.rename(self._path_complet, path.join(dossier_Purgatoire, self._nom_fichier))

    def purify(self, titre):

        # On remplace les caractères suivants par des espaces
        titre = titre.replace('.', ' ')
        titre = titre.replace('_', ' ')
        titre = titre.replace('-', ' ')

        # On élimine tout ce qui est entre bracket
        titre = re.sub('\[.*\]', '', titre)

        if debug:
            print('Titre purifié:', titre)
        return titre

    def search_imdb(self, valeur_recherche):

        search_values_imdb = {'q': valeur_recherche}

        # Encode le dictionnaire (percent-encoded ASCII text string (ex: %20 au lieu des espace))
        search_data = urllib.parse.urlencode(search_values_imdb)

        # Encode UTF-8
        search_data = search_data.encode('utf-8')

        url = 'https://www.imdb.com/find?'

        #Spoof du header
        header = {}
        header['User-Agent'] = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'

        req = urllib.request
        req = req.Request(url, headers=header)

        resp = urllib.request.urlopen(req, search_data).read()

        soup = bs.BeautifulSoup(resp, 'lxml')

        result = soup.find_all(class_='findResult odd')

        if result:
            result = result[0].text

            year = re.search(r"(19[2-9][0-9]|20[0-2][0-9])", result)

            span_start, span_end = year.span()
            titre = result[5:span_start - 2]


            if debug:
                print('IMDB retourne',titre)

            return titre

        else:
            if debug:
                print('Aucun résultat trouvé sur IMDB')

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
        # search_data = search_data.encode('utf-8')

        if debug:
            print('valeur de recherche: ', valeur_recherche)
            print('url_multi_search', url_multi_search)
            print('search_data', search_data)

        # On fait la requete URL incluant les search_values a l'API de themoviedb.org
        data_binaire = urllib.request.urlopen(url_multi_search + search_data)
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
                self.type_detecte = 'Serie'
                serie_title = resultat_0['original_name']

                if debug:
                    print('themoviedb.org detecte {} {} '.format(serie_title, self.type_detecte))

                resultat_recherche_api = (serie_title, self.type_detecte, None, None)

                return resultat_recherche_api

            elif resultat_0['media_self.type'] == 'movie':
                movie_title, self.type_detecte, release_year, genre = None, None, None, None

                self.type_detecte = 'Film'

                release_date = resultat_0['release_date']
                release_year = release_date[:4]
                movie_title = resultat_0['title']
                print(movie_title)
                genre_id = resultat_0['genre_ids']

                if genre_id:
                    genre_id = genre_id[0]
                    genre = genre_ids[genre_id]

                if debug:
                    print('themoviedb.org detecte {} {} '.format(self.type_detecte, movie_title, release_year))

                resultat_recherche_api = (movie_title, self.type_detecte, release_year, genre)
                return resultat_recherche_api

            elif resultat_0['media_self.type'] == 'person':
                if debug:
                    print('Aucun resultat trouve sur themoviedb.org')
                return None

        else:
            if debug:
                print('Aucun resultat trouve sur themoviedb.org')
            return None

    def recursive_verify(self, valeur_recherche):

        if debug:
            print('----------------------------DEBUT RECHERCHE RECURSIVE----------------------------')
            print('Sujet: {}'.format(valeur_recherche))
        resultat_regex_01 = re.search(r'[\w]+\s', valeur_recherche)
        resultat_regex_02 = re.search(r'[\w]+\s[\w]+', valeur_recherche)
        resultat_regex_03 = re.search(r'[\w]+\s[\w]+\s[\w]+', valeur_recherche)
        resultat_regex_04 = re.search(r'[\w]+\s[\w]+\s[\w]+\s[\w]+', valeur_recherche)
        resultat_regex_05 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+', valeur_recherche)
        resultat_regex_06 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+',
                                      valeur_recherche)

        '''
        resultat_regex_01 = re.search(r'[a-zA-Z]+\s', valeur_recherche)
        resultat_regex_02 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+', valeur_recherche)
        resultat_regex_03 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+', valeur_recherche)
        resultat_regex_04 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+', valeur_recherche)
        resultat_regex_05 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+', valeur_recherche)
        resultat_regex_06 = re.search(r'[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+\s[a-zA-Z]+',
                                      valeur_recherche) '''

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
                    break
            else:
                break

        if resultat_final:
            if debug:
                print('Recherche recursive retourne', resultat_final)
                print('----------------------------FIN RECHERCHE RECURSIVE----------------------------')
            return resultat_final


        else:
            if debug:
                print('Recherche recursive ne retourne rien')
                print('----------------------------FIN RECHERCHE RECURSIVE----------------------------')
            return None

    def move_file(self, titre, type, season_episode=None, movie_year=None, genre=None):

        titre = titre.replace(':', '')

        if self.type == 'Serie':

            seasons_folder = None
            episode_number = 0

            # nom final du fichier
            if season_episode:
                series_complete_title = '{} {}{}'.format(titre, season_episode, self._extension)
            else:
                print("No Season or Episode info found. Sending to purgatory")

            # sous dossier de saison
            seasons_folder = 'Season {}'.format(season_episode[1:3])

            # path complet de destination pour l'item
            series_pathto = os.path.join(dossier_series, titre, seasons_folder, series_complete_title)

            series_pathto_folder = os.path.join("/media/julien/Videos/Series/", titre, seasons_folder)
            series_pathto_folder = series_pathto_folder.replace(" ", "\ ")

            series_pathto_scp = os.path.join("Series", titre, seasons_folder, series_complete_title)
            series_pathto_scp = mediacenter_destination + series_pathto_scp
            series_pathto_scp = series_pathto_scp.replace(" ", "\ ")

            if debug:
                print("SCP Path =  {}".format(series_pathto_scp))

            if os.path.isfile(series_pathto):
                while True:

                    episode_number += 1

                    if episode_number < 10:
                        episode_number_str = '0' + str(episode_number)
                    else:
                        episode_number_str = episode_number

                    series_complete_title = '{} {}{}'.format(titre, episode_number_str, self._extension)

                    series_pathto = os.path.join(dossier_series, titre, series_complete_title)

                    if not os.path.isfile(series_pathto):
                        break

            # Si le dossier qui contient la saison n'existe pas, on le cree et finalement on deplace vers celui-ci

            if seasons_folder:
                path_dossier_season = os.path.join(dossier_series, titre, seasons_folder)
                if os.path.isdir(path_dossier_season):
                    if operation_mode == 'local':
                        print(self._path_complet + '-->' + series_pathto)

                    if not simulation and operation_mode == "local":
                        os.rename(self._path_complet, series_pathto)

                else:
                    print('Creation du dossier local' + path_dossier_season)
                    if operation_mode == 'local':
                        print(self._path_complet + ' --> ' + series_pathto)
                    if not simulation and operation_mode == "local":
                        os.makedirs(path_dossier_season)
                        os.rename(self._path_complet, series_pathto)

            else:
                if operation_mode == 'local':
                    print(self._path_complet + '-->' + series_pathto)
                if not simulation and operation_mode == "local":
                    os.rename(self._path_complet, series_pathto)

            if not simulation and operation_mode == "mediacenter":
                self.scp_to_mediacenter(self._path_complet, series_pathto_scp, series_pathto_folder)

        if self.type == 'Film':

            # Nom final du fichier
            title_final = '{} ({}){}'.format(titre, movie_year, self._extension)

            # dossier destination pour le films, dependant du genre
            if genre:
                path_final = '{}/{}'.format(dossier_films,genre)

            # Si aucun genre, on envoie dans Other
            else:
                path_final = '{}/Other'.format(dossier_films)

            #Creation du dossier de genre si inexistant
            if not os.path.isdir(path_final):
                print('Creation du dossier', path_final)

                if not simulation and operation_mode == "local":
                    os.mkdir(path_final)

            movies_pathto = ('{}/{}'.format(path_final, title_final))

            movies_pathto_folder = "/media/julien/Videos/Films/" + genre if genre else "Other"

            movies_pathto_scp = os.path.join("Films", genre if genre else "Other", title_final)
            movies_pathto_scp = mediacenter_destination + movies_pathto_scp
            movies_pathto_scp = movies_pathto_scp.replace(" ", "\ ")
            movies_pathto_scp = movies_pathto_scp.replace("(", "\(")
            movies_pathto_scp = movies_pathto_scp.replace(")", "\)")

            if debug:
                print("Movies path to scp: {}".format(movies_pathto_scp))


            # Deplacement du film vers le dossier film
            if operation_mode == 'local':
                print(self._path_complet + ' --> ' + movies_pathto)

            if not simulation and operation_mode == "local" and operation_mode == "local":
                os.rename(self._path_complet, movies_pathto)

            if not simulation and operation_mode == "mediacenter":
                self.scp_to_mediacenter(self._path_complet, movies_pathto_scp, movies_pathto_folder)

    def scp_to_mediacenter(self, source, destination, destination_folder):
        scp_success = False
        try_count = 0

        while scp_success != True:
            print('Copie de {} par SSH vers MediaCenter'.format(source))

            # Verification de l'existance du dossier de destination
            message = subprocess.run(["ssh", "julien@192.168.0.100", "ls", destination_folder])

            # S`il n existe pas verification de l'existance du dossier superieur
            if message.returncode != 0:
                destination_folder_up = re.search(".*(?=\/.*$)", destination_folder)
                destination_folder_up = destination_folder_up.group()

                message = subprocess.run(["ssh", "julien@192.168.0.100", "ls", destination_folder_up])

                #S'il le dossier superieur n'existe pas on le crée
                if message.returncode != 0:
                     self.ssh_mkdir(destination_folder_up)

                # Finalement on crée le dossier de destination
                self.ssh_mkdir(destination_folder)

            # Si dossier existe on copie
            elif message.returncode == 0:
                message = subprocess.run(["scp", source, destination])

                if message.returncode == 0:
                    print("Item copié SCP avec succès vers Mediacentral")
                    scp_success = True

            try_count += 1

        if scp_success:
            try:
                print('Supression locale du fichier {}'.format(self._path_complet))
                os.remove(self._path_complet)
            except:
                print('Error deleting {}'.format(self._path_complet))

    def ssh_mkdir(self, path):
        message = subprocess.run(["ssh", "julien@192.168.0.100", "mkdir", path])

        if message.returncode == 0:
            print('Dossier {} créé avec succès'.format(path))
        else:
            print('Erreur lors de la création du dossier {}'.format(path))

    def purge(self):
        file_info = os.stat(path.join(self._location,self._nom_fichier))
        file_size = file_info.st_size / 1e6

        if debug:
            print("file_size = {}MB".format(file_size))

        if file_size < 100 and self._extension != '.srt':
            try:
                print('supression du fichier: {} car il est un trop petit ({}MB)\n\n'.format(fichier, file_size))
                if not simulation and operation_mode == "local":
                    os.remove(self._path_complet)
            except PermissionError:
                print('erreur de permission, deplacement au Purgatoire')

                if not simulation and operation_mode == "local":
                    os.rename(self._path_complet, self._Purgatoire)

            return True

        elif self._extension in self.indesirables and self._nom_fichier not in os.listdir('{}Purgatoire'.format(source)):
            try:
                print('supression du fichier: {} car il est un indésirable\n\n'.format(fichier))
                if not simulation and operation_mode == "local":
                    os.remove(self._path_complet)
            except PermissionError:

                print('erreur de permission, deplacement au Purgatoire')

                if not simulation and operation_mode == "local":
                    os.rename(self._path_complet, self._Purgatoire)

            return True

##################################################################################
debug = True

# mediacenter = Send to mediacenter, local = move file to local classification folders
operation_mode = "mediacenter"

# Mode simulation = Aucunes manipulations sur les fichiers
simulation = True

##################################################################################

if simulation:
    print('***Mode Simulation Actif***')
else:
    print('***Mode Simulation Non-Actif, des actions seront posées!!***')

source = '/home/julien/Downloads/Triage/'
mediacenter_destination = 'julien@192.168.0.100:/media/julien/Videos/'

dossier_films = path.join(source, 'Films')
dossier_series = path.join(source, 'Series')
dossier_Purgatoire  = path.join(source, 'Purgatoire')
dossiers_base = ['Purgatoire', 'Films', 'Series']

root = os.walk(source)

# Creation du dossier Purgatoire s'il est manquant
if not os.path.isdir(dossier_Purgatoire):
    print('Creation du dossier {}'.format(dossier_Purgatoire))
    if not simulation and operation_mode == "local":
        os.makedirs(dossier_Purgatoire)

# Creation du dossier films s'il est manquant
if not os.path.isdir(dossier_films):
    print('Creation du dossier {}'.format(dossier_films))
    if not simulation and operation_mode == "local":
        os.makedirs(dossier_films)

# Iteration recursive dans l'arborescence source
for racine, directories, fichiers in root:
    for fichier in fichiers:
        # On determine si le dossier racine contient du materiel deja classe dans les dossiers de base afin d'éviter
        # de traiter 2 fois le même objet.
        parse_dossier_racine = re.search(r"/(Series|Films|Purgatoire)", racine)

        # Si le parse ne retourne rien on process l'item
        if  not parse_dossier_racine:
            if debug:
                print('\n\nTraitement du fichier', fichier)
                print('------------------------------------------------------------------------------')

            individu = Item_to_process(fichier, racine)

            # Purge des fichiers indesirables
            purged = individu.purge()

            if not purged:
                individu.classify()
                print('\n\n')

#On fait le menage des dossiers vides
for dossier in os.listdir(source):

    path_dossier = path.join(source, dossier)

    if dossier not in dossiers_base and os.path.isdir(path_dossier):

        print('Supression du dossier ' + (os.path.join(source, dossier)))

        if not simulation:

            shutil.rmtree(os.path.join(source, dossier))









