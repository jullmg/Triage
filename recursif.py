import os

root = os.walk('d:\\downloads')

for racine, directories, fichiers in root:

    #print(racine)
    #print(directories)
    #print(fichiers)
    for i in fichiers:
        print(os.path.join(racine, i))
