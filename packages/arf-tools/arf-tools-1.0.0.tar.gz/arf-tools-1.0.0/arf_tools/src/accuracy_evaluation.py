""" This module contains all methods related to accuracy evaluation.

Most of these functions take two data set as parameters (datax, datay). The
first is the database containing all examples, and the second their respective
labels. They also take a classifieur to evaluate as a third parameter. This
classifieur must have the methods `fit` (for training it), `predict` (for
classifying) and `score` (for classification evaluation) implemented for the
modules's functions to work.

Authors :
* BIZZOZZERO Nicolas
* ADOUM Robert
"""

import numpy as np
from splitting import split_train_test, chunk


def train_test(datax, datay, classifieur, pourcentage_train=0.8, shuffle=True):
    """ Evalue l'accuracy d'un classifieur en séparant les données en deux
    bases, une d'apprentissage et une de test.
    Retourne le score de bonne classification sur la base d'apprentissage puis
    sur la base de test.

    Le classifieur doit possèder les méthodes `fit` pour l'apprentissage,
    `predict` pour une classification et `score` pour une évaluation.
    """
    # Séparation des données
    datax_train, datay_train, datax_test, datay_test = \
        split_train_test(datax, datay, pourcentage_train)

    # Apprentissage
    classifieur.fit(datax_train, datay_train)

    # Evaluation sur la base d'apprentissage puis de test
    return classifieur.score(datax_train, datay_train),\
        classifieur.score(datax_test, datay_test)


def cross_validation(datax, datay, classifieur, pieces=10, shuffle=True):
    """ Effectue une Cross Validation selon la méthode des K-folds afin
    d'évaluer l'accuracy d'un classifieur.
    Retourne la moyenne des classifications de toutes les sous-bases.

    Le classifieur doit possèder les méthodes `fit` pour l'apprentissage,
    `predict` pour une classification et `score` pour une évaluation.
    """
    # On partitionne les données
    v_datax, v_datay = chunk(datax, datay, pieces, shuffle)

    # On va itérer sur chaque base une fois pour la faire devenir une base de
    # test
    erreurs_en_test = list()
    for index_test in range(pieces):
        datax, datay, testx, testy = list(), list(), list(), list()

        # On va concaténer toutes les bases d'apprentissage
        for index in range(pieces):
            if index == index_test:
                testx.extend(v_datax[index])
                testy.extend(v_datay[index])
            else:
                datax.extend(v_datax[index])
                datay.extend(v_datay[index])

        # On apprends
        classifieur.fit(np.array(datax), np.array(datay))

        # On test
        score = classifieur.score(np.array(testx),
                                  np.array(testy))
        erreurs_en_test.append(score)

    return np.mean(erreurs_en_test)


if __name__ == '__main__':
    pass
