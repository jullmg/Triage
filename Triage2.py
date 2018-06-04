'''Version : 1.2 '''

#a faire :

#utiliser les expressions regulières
# Synchronisation sur base de donnee sur le web? Pour chercher posters et sous-titres et nom episodes


import os, re, shutil, stat

from os import rename, path

from string import capwords



class Item_to_process:

    def __init__(self,nom_fichier,location):

        self._nom_fichier = nom_fichier

        self._location = location

        self._path_complet = os.path.join(self._location, self._nom_fichier)

        self._prefixe, self._extension = os.path.splitext(self._path_complet)

        self._purgatoire = '{}\purgatoire\{}'.format(source, self._nom_fichier)

        self.indesirables = ['.txt', '.nfo', '.jpg', '.sfv', '.ini']


    def classify(self):

        #item_name, item_extention

        range_1_a_10 = str(list(range(0, 10)))

        type_detecte = None

        if self._extension not in self.indesirables:

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

                    if self._nom_fichier[i] in ['1', '2'] and self._nom_fichier[i + 1] in range_1_a_10 \
                            and self._nom_fichier[i + 2] in range_1_a_10 and self._nom_fichier[i + 3] in range_1_a_10 \
                            and (self._nom_fichier[i - 1]) in ['.', '(', '[', '-', ' ']:

                        type_detecte = "Film"

                        movie_title = ''

                        #On change les points par des espaces
                        for lettre in self._nom_fichier[0:i - 1]:

                            if lettre == '.':

                                movie_title = movie_title + ' '

                            else:

                                movie_title = movie_title + lettre


                        movie_year = ''.join(self._nom_fichier[i:i + 4])

                        # dossier destination pourn les films
                        movies_pathto = ('{}\{} ({}){}'.format(dossier_films, movie_title, movie_year, self._extension))

                        # Deplacement du film vers le dossier film
                        print(self._path_complet + ' --> ' + movies_pathto)
                        if simulation == False:
                            rename(self._path_complet, movies_pathto)

                except:

                    pass

        if type_detecte == None and self._nom_fichier != os.path.basename(__file__) and self._extension not in self.indesirables:

            print('Type non-detecte, au purgatoire: ' + self._nom_fichier)


            if simulation == False:

                rename(self._path_complet, path.join(dossier_purgatoire, self._nom_fichier))

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

simulation = False

#source = 'd:\\downloads\\triage'

source = os.getcwd()

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

for racine, directories, fichiers in root:

    for fichier in fichiers:


        if racine != dossier_series and racine != dossier_films \
                and racine !=  dossier_purgatoire:

            individu = Item_to_process(fichier, racine)

            individu.purge()

            individu.classify()

#On fait le menage des dossiers vides
for dossier in os.listdir(source):

    if dossier not in dossiers_base and dossier != os.path.basename(__file__) and os.path.isdir(dossier) :

        print('Supression du dossier ' + (os.path.join(source, dossier)))

        if simulation == False:

            shutil.rmtree(os.path.join(source, dossier))
