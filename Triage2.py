'''Version : 1.1 '''

#a faire :
# lire plus qu'un dossier de profondeur
#Synchronisation sur base de donnee sur le web?


import os
from os import rename, path
import stat
from string import capwords

class Item_to_process:

    def __init__(self,nom_fichier,location):

        self._nom_fichier = nom_fichier

        self._location = location

        self._path_complet = os.path.join(self._location, self._nom_fichier)

        self._prefixe, self._extension = os.path.splitext(self._path_complet)

        print('on process: ' + self._nom_fichier)

    def classify(self):

        #item_name, item_extention

        range_1_a_10 = str(list(range(0, 10)))
        
        season_episode = None

        for i, n in enumerate(self._nom_fichier):

            # On detecte si c'est une serie televisee en detectant le pattern S0102
            try:

                if (self._nom_fichier[i] in ['s', 'S']) and (self._nom_fichier[(i + 1)] in range_1_a_10) and (self._nom_fichier[(i - 1)] in ['.', ' ']):

                    series_episode = ''.join(self._nom_fichier[i:(i + 6)])

                    series_episode = series_episode.upper()

                    print('series_episode: ' + series_episode)

                    series_title = ''.join(self._nom_fichier[0:(i-1)])

                    print('series_title: ' + series_title)

                    series_title_clean = ''

                    # On determine la nomenclature pour le dossier qui contiendra cette serie
                    for n in series_title:

                        if n != '.':

                            series_title_clean = series_title_clean + n

                        else:

                            series_title_clean = series_title_clean + ' '

                    series_title_clean = capwords(series_title_clean)



                    seasons_folder = 'Season {}'.format(series_episode[1:3])

                    #On determine le path de destination pour l'item
                    series_pathto = ('{}\{}\{}\{} {}{}'.format(dossier_series,series_title_clean, seasons_folder, series_title_clean, series_episode, self._extension))

                    # Si le dossier qui contient la saison n'existe pas, on le cree et finalement on deplace vers celui-ci
                    if os.path.isdir('{}\{}\{}'.format(dossier_series, series_title_clean, seasons_folder)):

                        rename(self._path_complet, series_pathto)

                    else:

                        os.makedirs('{}\{}\{}'.format(dossier_series, series_title_clean, seasons_folder))
                        rename(self._path_complet, series_pathto)

                    print('{} |detecte| {} {} (.seasonid3)'.format(''.join(self._nom_fichier), series_title, series_episode))

            except IndexError:
                pass


            # On detecte un film en trouvant une annee

            try:
                if self._nom_fichier[i] in ['1', '2'] and self._nom_fichier[i + 1] in str(list(range(0, 10))) \
                        and self._nom_fichier[i + 2] in range_1_a_10 and self._nom_fichier[i + 3] in range_1_a_10 \
                        and (self._nom_fichier[i - 1]) in ['.', '(', '[', '-', ' ']:

                    movie_title = ''

                    for lettre in self._nom_fichier[0:i - 1]:

                        if lettre == '.':

                            movie_title = movie_title + ' '

                        else:

                            movie_title = movie_title + lettre



                    print(movie_title)

                    movie_year = ''.join(self._nom_fichier[i:i + 4])

                    # dossier destination pourn les films
                    movies_pathto = ('{}\{} ({}){}'.format(dossier_films, movie_title, movie_year, self._extension))

                    print('{} |detecte| {} {} (.seasonid3)'.format(''.join(self._nom_fichier), movie_title, movie_year))

                    # Deplacement du film vers le dossier film
                    rename(self._path_complet, movies_pathto)

            except:

                pass

    def purge(self):

        indesirables = ['.txt', '.nfo', '.jpg', '.sfv']

        purgatoire = '{}\purgatoire\{}'.format(source, self._nom_fichier)

        if self._extension in indesirables and self._nom_fichier not in os.listdir('{}\purgatoire'.format(source)):

            try:

                os.remove(self._path_complet)
                print('supression du fichier: ' + self._nom_fichier)

            except PermissionError:

                print('erreur de permission, deplacement au purgatoire')
                os.rename(self._path_complet, purgatoire)

source = os.getcwd()

dossier_films = '{}\Films'.format(source)

dossier_series = '{}\Series'.format(source)

dossiers_base = ['purgatoire','Films','Series']



dossiers = os.listdir(source)

root = os.walk(source)

for racine, directories, fichiers in root:

    #print(racine)
    #print(directories)
    #print(fichiers)
    for i in fichiers:
        print(os.path.join(racine, i))

#Creation des fichiers de base si necessaire
for i in dossiers_base:

    if i not in dossiers:

        os.makedirs('{}\{}'.format(source, i))






quit()
for items in dossiers :

    #path de l'item itere
    path_sous_dossier = path.join(source, items)

    # mode = fichier ou dossier
    mode = os.stat(path_sous_dossier).st_mode

    # Est-ce que c'est un dossier?
    if stat.S_ISDIR(mode) and items not in dossiers_base :

        #oui alors on liste son contenu
        fichiers = os.listdir(path_sous_dossier)

        #on itere et process les items contenus
        for elements in fichiers:
            print(elements)
            individu = Item_to_process(elements, path_sous_dossier)
            individu.purge()

            individu.classify()

        #On elimine le dossier vide qui reste
        os.removedirs(path_sous_dossier)

    # Est-ce que c'est un fichier?
    if stat.S_ISREG(mode) and items != os.path.basename(__file__):

        #oui alors on le process

        individu = Item_to_process(items,source)
        individu.purge()
        individu.classify()


