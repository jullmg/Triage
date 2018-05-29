'''Version : 1.1 '''

#a faire :
# lire plus qu'un dossier de profondeur
# mode simulation
# Synchronisation sur base de donnee sur le web?


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


    def classify(self):

        #item_name, item_extention

        range_1_a_10 = str(list(range(0, 10)))
        
        type_detecte = None

        for i, n in enumerate(self._nom_fichier):

            # On detecte si c'est une serie televisee en detectant le pattern S0102
            try:

                if (self._nom_fichier[i] in ['s', 'S', 'E', 'e']) and (self._nom_fichier[(i + 1)] in range_1_a_10) and (self._nom_fichier[(i - 1)] in ['.', ' ']):

                    type_detecte = 'Serie'

                    if self._nom_fichier[i] in ['E', 'e']:

                        series_episode = ('S01' + self._nom_fichier[i:(i + 3)])

                    else:

                        series_episode = ''.join(self._nom_fichier[i:(i + 6)])

                    series_episode = series_episode.upper()

                    series_title = ''.join(self._nom_fichier[0:(i-1)])

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

                        print(self._path_complet + '-->' + series_pathto)
                        if simulation == False:
                            rename(self._path_complet, series_pathto)

                    else:

                        os.makedirs('{}\{}\{}'.format(dossier_series, series_title_clean, seasons_folder))

                        print(self._path_complet + ' --> ' + series_pathto)
                        if simulation == False:
                            rename(self._path_complet, series_pathto)



            except IndexError:
                pass

            # On detecte un film en trouvant une annee

            try:
                if self._nom_fichier[i] in ['1', '2'] and self._nom_fichier[i + 1] in str(list(range(0, 10))) \
                        and self._nom_fichier[i + 2] in range_1_a_10 and self._nom_fichier[i + 3] in range_1_a_10 \
                        and (self._nom_fichier[i - 1]) in ['.', '(', '[', '-', ' ']:

                    type_detecte = "Film"

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

                    # Deplacement du film vers le dossier film
                    print(self._path_complet + ' --> ' + movies_pathto)
                    if simulation == False:
                        rename(self._path_complet, movies_pathto)

            except:

                pass

        if type_detecte == None:

            print('Au purgatoire: ' + self._nom_fichier)

            if simulation == False:
                os.rename(self._path_complet, purgatoire)

    def purge(self):

        indesirables = ['.txt', '.nfo', '.jpg', '.sfv']

        purgatoire = '{}\purgatoire\{}'.format(source, self._nom_fichier)

        if self._extension in indesirables and self._nom_fichier not in os.listdir('{}\purgatoire'.format(source)):

            try:

                print('supression du fichier: ' + self._nom_fichier)

                if simulation == False:
                    os.remove(self._path_complet)


            except PermissionError:

                print('erreur de permission, deplacement au purgatoire')

                if simulation == False:
                    os.rename(self._path_complet, purgatoire)

simulation = True

source = 'd:\\downloads\\triage'

dossier_films = '{}\Films'.format(source)

dossier_series = '{}\Series'.format(source)

dossiers_base = ['purgatoire','Films','Series']



dossiers = os.listdir(source)

root = os.walk(source)

for racine, directories, fichiers in root:

    for fichier in fichiers:

        if racine[0:(len(source)+7)] != os.path.join(source,'Series') and racine[0:(len(source)+6)] != os.path.join(source,'Films'):

            individu = Item_to_process(fichier, racine)
            individu.purge()
            individu.classify()

#On fait le menage des dossiers vides
for dossier in os.listdir(source):

    if dossier not in dossiers_base:

        print('Supression du dossier ' + (os.path.join(source, dossier)))

        if simulation == False:
            os.removedirs(os.path.join(source, dossier))


quit()

#Creation des fichiers de base si necessaire
for i in dossiers_base:

    if i not in dossiers:

        os.makedirs('{}\{}'.format(source, i))

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


