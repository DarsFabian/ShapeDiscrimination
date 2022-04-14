# -------------------------------------------------------------------------------
# Name:         forme-counter
# Purpose:      A fonctions repository for Exclusion des formes.py
#
# Author:       LEROY Gaétan
#
# Created:      09/03/2022
# -------------------------------------------------------------------------------

import numpy
from numpy import array, rot90, flipud, fliplr, zeros, shape, hsplit, max, roll, argwhere, ones
from math import ceil, factorial
from os import path, makedirs
from pandas import DataFrame, read_excel
from multiprocessing import Process, Value, Manager
from time import time, sleep


def forme_to_formes(forme):
    f = [
        array(forme).tolist(),
        rot90(forme, 1).tolist(),
        rot90(forme, 2).tolist(),
        rot90(forme, 3).tolist(),
        flipud(forme).tolist(),
        flipud(rot90(forme, 1)).tolist(),
        flipud(rot90(forme, 2)).tolist(),
        flipud(rot90(forme, 3)).tolist(),
        fliplr(forme).tolist(),
        fliplr(rot90(forme, 1)).tolist(),
        fliplr(rot90(forme, 2)).tolist(),
        fliplr(rot90(forme, 3)).tolist()]

    doublon = set()
    for i, j in enumerate(f):
        for a in range(i + 1, len(f)):
            if j == f[a]:
                doublon.add(i)

    for i, j in enumerate(doublon):
        f.pop(j - i)
    return f


def get_sum(f, ligne, colonne):
    s = zeros((ligne, colonne), dtype=int)
    for a in f:
        for b in range(ligne - shape(a)[0] + 1):
            for c in range(colonne - shape(a)[1] + 1):
                s[b:b + shape(a)[0], c:c + shape(a)[1]] += a
    return s


def interval(ligne, colonne, forme):
    coin = get_sum(forme_to_formes(forme), 5, 5)[0:3, 0:3]
    a = ((ligne - 4) * (colonne - 4) * coin[2, 2] + 4 * coin[1, 1] + (ligne + colonne - 8) * 2 * (
            coin[0, 2] + coin[1, 2]) + 8 *
         coin[0, 1] + 4 * coin[0, 0]) // sum([sum(a) for a in forme])
    b = ceil(a / coin[2, 2])
    c = ceil(a / coin[0, 0])
    return a, b, c


def verifier(mat, formes):  # verifies si la forme rentre dans la matrice
    for Test in formes:
        comparaison = Test * mat == Test
        if comparaison.all():
            return False
    return True


def exporter(mat):
    file = DataFrame(mat)
    file.to_excel("Matrice.xlsx", header=None, index=None)


def importer(filename):
    mat = read_excel(filename + ".xlsx", header=None, index_col=None).to_numpy()
    return mat


def matrice(ligne, colonne, minimum, last_pos):  # génère une matrice aléatoire (passe1) ou non (passe 2)
    if last_pos[0] == ligne * colonne - minimum:
        print("Now looking for min =", minimum + 1)
        return [], list(range(minimum + 1)), True
    pos = [last_pos, last_pos.copy()]
    pos[1][-1] += 1
    for b in range(1, minimum):
        if b == minimum - 1 and pos[1][1] >= ligne * colonne - minimum + 2:
            pos[1][0] += 1
            for c in range(1, minimum):
                pos[1][c] = pos[1][c - 1] + 1

        elif pos[1][-b] >= ligne * colonne - b + 1:
            pos[1][-b - 1] += 1
            for c in range(minimum - b, minimum):
                pos[1][c] = pos[1][c - 1] + 1

        if pos[1][-b] >= ligne * colonne - b + 1:
            pos[1][-b] = ligne * colonne - b

    mat = ones((ligne * colonne,), dtype=int)
    for a in pos[1]:
        mat[a] = 0

    return array(mat).reshape((ligne, colonne)), pos[1], False


def search(ligne, colonne, minimum, forme, last_pos, last_pos_fin, stop, procnum, return_test,
           tests):  # Fonction principal
    print("Initializing core", procnum)
    test = 0
    formes = get_formes(ligne, colonne, forme)
    while last_pos != last_pos_fin:
        if stop.value == 1:
            print("core", procnum, "was stopped")
            tests.value += test
            return
        mat, last_pos, fin = matrice(ligne, colonne, minimum, last_pos)
        if fin:
            print("core", procnum, "finished his work")
            tests.value += test
            return
        else:
            x = verifier(mat, formes)
            if x:
                print("core", procnum, "found an array that fit in")
                stop.value = 1
                tests.value += test
                return_test[procnum] = mat
                return
            test += 1
    print("core", procnum, "finished his work")
    tests.value += test
    return


def get_formes(ligne, colonne, forme):
    formes = []
    forme2 = forme.copy()
    for TestM in range(2):
        if TestM != 0:
            forme2 = flipud(forme).copy()
        for TestR in range(4):
            forme3 = rot90(forme2, TestR).copy()
            zero = zeros((ligne, colonne), dtype=int)
            zero[:shape(forme3)[0], :shape(forme3)[1]] = forme3.copy()
            forme3 = zero.copy()
            [uns_v, uns_h] = hsplit(argwhere(forme3 == 1), 2).copy()
            for TestV in range(ligne - max(uns_v)):
                forme4 = roll(forme3, TestV, axis=0).copy()
                for TestH in range(colonne - max(uns_h)):
                    formes.append(roll(forme4, TestH, axis=1))
    doublon = set()
    for i, j in enumerate(formes):
        for a in range(i + 1, len(formes)):
            if j.tolist() == formes[a].tolist():
                doublon.add(i)
    for i, j in enumerate(doublon):
        formes.pop(j - i)
    return formes


def interface():
    # inputs
    ligne_n = int(input("l = "))
    colonne_n = int(input("c = "))
    forme_n = int(input("Forme n° = "))
    first_min = int(input("Commencer à balayer à partir de min = "))

    # créer des dossiers ou pas
    if path.exists(
            path.dirname(path.realpath(__file__)) + "/Exclusion des formes/Formes/Forme " + str(forme_n) + ".xlsx"):

        forme = importer(path.dirname(path.realpath(__file__)) + "/Exclusion des formes/Formes/Forme " + str(forme_n))
        print("Loading Formes...")
        get_formes(ligne_n, colonne_n, forme)
        print("Done\nGetting Interval...")
        if first_min == 0:
            mini = interval(ligne_n, colonne_n, forme)[1]
        else:
            mini = first_min
        print("Done\nRunning...")
        return run(ligne_n, colonne_n, mini, forme)

    else:
        makedirs(path.dirname(path.realpath(__file__)) + "/Exclusion des formes/Formes/", exist_ok=True)
        print("""Veuillez d'abord créer un fichier nommé "forme """ + str(
            forme_n) + """" dans le dossier: /Exclusion des formes/Formes/""")


def run(ligne, colonne, minimum, forme):
    fin = False
    tests = Value("d", 0, lock=True)
    while not fin:
        print("\nSearching for minimum =", minimum, "...")
        mat, fin = multiprocess_search(ligne, colonne, minimum, forme, list(range(minimum)), tests)
        minimum += 1
        print("Done")
    return int(tests.value), minimum - 1, mat


def get_n_forme(size, minimum):
    return factorial(size) // (factorial(minimum) * factorial(size - minimum))


def get_steps(min, max, n_core):
    if n_core == 1:
        step0 = list(range(0, min))
        step1 = list(range(max - min, max))

        return [step0, step1]

    if n_core == 4:
        step0 = list(range(0, min))
        step1 = [0, (max - min + 1) // 2]
        step1.extend(list(range(max - min + 2, max)))
        step2 = [0]
        step2.extend(list(range(max - min + 1, max)))
        step3 = list(range(2, min + 2))
        step4 = list(range(max - min, max))

        return [step0, step1, step2, step3, step4]

    elif n_core == 8:
        step0 = list(range(0, min))
        step1 = [0, (max - min + 1) // 3]
        step1.extend(list(range(max - min + 2, max)))
        step2 = [0, 2 * (max - min + 1) // 3]
        step2.extend(list(range(max - min + 2, max)))
        step3 = [0]
        step3.extend(list(range(max - min + 1, max)))
        step4 = list(range(1, min + 1))
        step5 = list(range(2, min + 2))
        step6 = [(max - min) // 4]
        step6.extend(list(range(max - min + 1, max)))
        step7 = [(max - min) // 2 + 1]
        step7.extend(list(range(max - min + 1, max)))
        step8 = list(range(max - min, max))

        return [step0, step1, step2, step3, step4, step5, step6, step7, step8]


def multiprocess_search(ligne, colonne, minimum, forme, last_pos, tests):
    n_core = 8
    stop = Value("b", 0)
    return_test = Manager().list([[] for _ in range(n_core)])

    step = get_steps(minimum, ligne * colonne, n_core)
    jobs = []

    for i in range(n_core):
        p = Process(target=search,
                    args=(ligne, colonne, minimum, forme, step[i], step[i + 1], stop, i, return_test, tests))
        p.start()
        jobs.append(p)

    for i in jobs:
        i.join()

    mat = []
    fin = False
    for i in return_test:
        if type(i) == numpy.ndarray:
            fin = True
            mat = i

    return mat, fin


if __name__ == '__main__':
    t0 = time()
    tests, minimum, mat = interface()
    t = time() - t0
    exporter(mat)
    print("\nA minimum was found with", '{:,}'.format(tests).replace(',', ' '), "tests, in", int(t), "s, at min =", minimum, "with array :")
    for a in mat:
        print(a)
    sleep(10)
