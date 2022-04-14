#Fabian#9101

from pandas import DataFrame, read_excel
from numpy import flipud, rot90, ones, zeros, shape, hsplit, min, max, roll, argwhere, random, all, array
from keyboard import is_pressed
from time import sleep
from os import remove, path, makedirs, rename, system
from sys import exit
from math import factorial
from tqdm import tqdm

def run(l, c, forme):   #Fonction principal
    global f
    print("\n-----Passe 1-----\n")
    passe = 1
    test = 0
    count = 0
    minimum = l * c
    LastMin = 0
    while True:
        if is_pressed('q'):
            return test, minimum
        elif is_pressed('t'):
            print("Nombre de tests : " + str(test) + ", Minimum : " + str(minimum))
            sleep(0.5)
        else:
            if test == 5000:
                passe = 2
                print("\n-----Passe 2-----")
                count = 0
                LastMin = 0
                sleep(1)
            (m, fin, lenth) = GenMatrice(l, c, minimum, LastMin, count, passe)
            if LastMin != minimum and passe ==2:
                print("\nTest en cours...")
                pbar = tqdm(total = lenth, unit = "mat", unit_scale = True)
            LastMin = minimum
            if fin == True:
                pbar.close()
                return test, minimum
            x = verifier(m)
            if passe == 2:
                pbar.update(1)
            if len(trouve(m, 0)) < minimum and x == True:
                    if passe == 2:
                        pbar.close()
                    count = 0
                    minimum = len(trouve(m, 0))
                    exporter(m)
                    print(minimum)
                    print(m)
                    f.write("\n" + str(minimum) + "\n" + str(m))
                    sleep(1)
            test +=1
            count += 1

def verifier(m): # verifie si la forme rentre dans la matrice
    global formes
    x = True
    try:
        for Test in range(len(formes)):
            comparaison = formes[Test] * m == formes[Test]
            if comparaison.all() == True:
                x = 0 / 0
    except:
        x = False

    return x

def exporter(matrice):
    file = DataFrame(matrice)
    file.to_excel("Matrice.xlsx", header = None, index = None)

def importer(filename):
    matrice = read_excel(filename + ".xlsx", header = None, index_col = None)
    matrice = matrice.to_numpy()
    return matrice

def trouve(matrice, objet): #Renvoie les positions de l'objet dans la matrice
    couples = argwhere(matrice == objet)
    return couples

def GenMatrice(l, c, minimum, LastMin, count, passe):   #génère une matrice aléatoire (passe1) ou non (passe 2)
    global mat
    fin = False
    if passe == 1:
        mat = random.randint(2, size = (l, c), dtype = int)
        return mat, False, 0
    if passe == 2:
        if LastMin != minimum:
            m = list(ones((1, l * c - minimum + 1), dtype = int).flatten())
            m2 = list(zeros((1, minimum - 1), dtype = int).flatten())
            m.extend(m2)
            result = SeekPos(m, minimum - 1)
            mat = MakeArray(result, l, c)
        if count == len(mat):
            return mat[0], True, 0
        return mat[count], False, len(mat)

def SeekPos(m, minimum):    #Renvoie les positions des 1 dans toutes les permutations de la matrice
    pos = [list(range(minimum))]
    n = int(factorial(len(m)) / (factorial(minimum) * factorial(len(m) - minimum)))
    print("\nGénération en cours (min = " + str(minimum) + ")...")
    pbar = tqdm(total = n - 1, unit = "mat", unit_scale = True)
    for a in range(1, n):
        pos.append(pos[-1].copy())
        pos[a][-1] += 1
        for b in range(1, len(pos[0])):
            if b == len(pos[0]) - 1 and pos[a][1] >= len(m) - len(pos[0]) + 2:
                pos[a][0] += 1
                for c in range(1, len(pos[0])):
                    pos[a][c] = pos[a][c - 1] + 1

            elif pos[a][-b] >= len(m) - b + 1:
                pos[a][-b - 1] += 1
                for c in range(len(pos[0]) - b, len(pos[0])):
                    pos[a][c] = pos[a][c - 1] + 1

            if pos[a][-b] >= len(m) - b + 1:
                pos[a][-b] = len(m) - b
        pbar.update(1)
    pbar.close()
    return pos

def MakeArray(pos, l, c):   #Transforme les positions en matrices 2 dimensions
    matrices = []
    print("\nConvertion en cours...")
    pbar = tqdm(total = len(pos), unit = "mat", unit_scale = True)
    for a in range(len(pos)):
        m = list(ones((1, l * c), dtype = int).flatten())
        for b in range(len(pos[0])):
            test=pos[a][b]
            m[pos[a][b]] = 0
        matrices.append(array(m).reshape((l, c)))
        pbar.update(1)
    pbar.close()
    return matrices

#---------------------------------------------------------------------------------------------------------------------------------------------------#

# inputs
lignes = int(input("l = "))
colonnes = int(input("c = "))
Forme = int(input("Forme n° = "))

# def chemins des fichiers
chemin = path.dirname(path.realpath(__file__)) + "/Exclusion des formes/Résultats/Forme " +  str(Forme) + "/"
file_name = chemin + "(L = " + str(lignes) + ", C = " + str(colonnes) + ", Min = En cours...).txt"

# créer des dossier ou pas
if path.exists(path.dirname(path.realpath(__file__)) + "/Exclusion des formes/Formes/Forme " + str(Forme) + ".xlsx") == True:
    forme = importer(path.dirname(path.realpath(__file__)) + "/Exclusion des formes/Formes/Forme " + str(Forme))
else:
    makedirs(path.dirname(path.realpath(__file__)) + "/Exclusion des formes/Formes/", exist_ok = True)
    print("""Veuillez d'abord créer un fichier nommé "forme """ + str(Forme) + """" dans le dossier: /Exclusion des formes/Formes/""")
    exit(1)

formes = []
forme2 = forme.copy()
for TestM in range(2):
    if TestM != 0:
        forme2 = flipud(forme).copy()
    for TestR in range(4):
        forme3 = rot90(forme2, TestR).copy()
        zero = zeros((lignes, colonnes), dtype = int)
        zero[:shape(forme3)[0],:shape(forme3)[1]] = forme3.copy()
        forme3 = zero.copy()
        UnInForme3 = trouve(forme3, 1)
        [UnV,UnH] = hsplit(UnInForme3, 2).copy()
        for TestV in range(lignes-max(UnV)):
            forme4 = roll(forme3, TestV, axis=0).copy()
            for TestH in range(colonnes-max(UnH)):
                formes.append(roll(forme4, TestH, axis=1))

makedirs(chemin, exist_ok = True)
f = open(file_name, "a")
(tests, minimum) = run(lignes, colonnes, forme) # lance le programme
f.close()

# Sauvegarde des minima
if minimum != lignes * colonnes:
    new_name = chemin + "(L = " + str(lignes) + ", C = " + str(colonnes) + ", Min = " + str(minimum) + ", Tests = " + str(tests) + ").txt"
    if path.exists(new_name) == False:
        rename(file_name, new_name)
    print("\nRésultats sauvegardés sous : " + new_name)
else:
    remove(file_name)
    print("\nAucun résultats trouvé...")

system('pause')
