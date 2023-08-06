""" This module contains all methods related to database splitting.

Most of these functions take two data set as parameters (datax, datay). The
first is the database containing all examples, and the second their respective
labels.

Authors :
* BIZZOZZERO Nicolas
* ADOUM Robert
"""

import numpy as np


def split_train_test(datax, datay, pourcentage_train=0.8, shuffle=True):
    """ Sépare les bases de données en deux (une pour l'entrainement, une pour
    le test), en donnant `pourcentage train`% de données dans la première
    base, et  1 - `pourcentage_train`% de données dans la deuxième.
    """
    if shuffle:
        datax, datay = _shuffle_data(datax, datay)

    # On slice les données en deux
    index = int(len(datax) * pourcentage_train)
    datax_train, datax_test = datax[:index], datax[index:]
    datay_train, datay_test = datay[:index], datay[index:]

    # On les retourne en convertissant en np.array pour + de performance
    return np.array(datax_train), np.array(datay_train),\
        np.array(datax_test), np.array(datay_test)


def chunk(datax, datay, pieces=10, shuffle=True):
    """ Eclate les données passées en `pieces` d'approximativement la
    même taille.
    """
    if shuffle:
        datax, datay = _shuffle_data(datax, datay)

    # On split
    datax_chunked = np.array_split(datax, pieces)
    datay_chunked = np.array_split(datay, pieces)

    # Il peut y'avoir un example en trop, on le retire
    real_dim = datax_chunked[-1].shape[-0]
    for i in range(len(datax_chunked)):
        if datax_chunked[i].shape[0] != real_dim:
            datax_chunked[i] = datax_chunked[i][:-1]
            datay_chunked[i] = datay_chunked[i][:-1]
    return datax_chunked, datay_chunked


def _shuffle_data(datax, datay):
    """ Bouge aléatoirement la position de toutes les données tout en
    conservant l'ordre des exemples et des labels.
    """
    permutations = np.random.permutation(len(datax))
    return datax[permutations], datay[permutations]


if __name__ == '__main__':
    pass
