# -*- coding: utf-8 -*-
""" This module contains all methods related to loading and parsing common
datasets.
"""

import pickle

import numpy as np


PATH_DATA_IMDB = "data/imdb_extrait.pkl"
PATH_DATA_POI = "data/poi-paris.pkl"
PATH_DATA_USPS_TRAIN = "data/USPS_train.txt"
PATH_DATA_USPS_TEST = "data/USPS_test.txt"


def load_imdb(path=PATH_DATA_IMDB, encoding="latin1",
              threshold_good_rating=6.5, label_good_rating=1,
              label_bad_rating=-1):
    with open(path, "rb") as file:
        data, id2titles, fields = pickle.load(file, encoding=encoding)

    # Base contenant les données
    datax = data[:, :32]

    # Base contenant les labels
    datay = np.array([label_good_rating if x[33] > threshold_good_rating else
                      label_bad_rating for x in data])

    return datax, datay, fields


def load_poi(data_poi=PATH_DATA_POI):
    """ Charges les points d'interets et retourne le dictionnaire les
    contenant.
    """
    return pickle.load(open(data_poi, "rb"))


def clean_poi(data_poi, poi):
    """ Nettoie les données chargées en filtrant les POI non-désirés.
    Retourne une liste de coordonnées (x, y).
    """
    data = []
    for id_poi in data_poi[poi].keys():
        poi_x, poi_y = data_poi[poi][id_poi][0]
        data.append(np.array([poi_x, poi_y]))
    return np.array(data)


def load_usps(class_neg, class_pos, filename_train=PATH_DATA_USPS_TRAIN,
              filename_test=PATH_DATA_USPS_TEST, label_neg=0, label_pos=1):
    with open(filename_train, "r") as f:
        f.readline()
        data = [[float(x) for x in l.split()] for l in f if len(l.split()) > 2]
    tmp = np.array(data)
    datax_train, datay_train = tmp[:, 1:], tmp[:, 0].astype(int)
    indexes_neg = np.where(datay_train == class_neg)[0]
    indexes_pos = np.where(datay_train == class_pos)[0]
    datax_train = np.vstack((datax_train[indexes_neg],
                             datax_train[indexes_pos]))
    datay_train = np.hstack((np.ones((len(indexes_neg),)) * label_neg,
                             np.ones((len(indexes_pos),)) * label_pos))

    with open(filename_test, "r") as f:
        f.readline()
        data = [[float(x) for x in l.split()] for l in f if len(l.split()) > 2]
    tmp = np.array(data)
    datax_test, datay_test = tmp[:, 1:], tmp[:, 0].astype(int)
    indexes_neg = np.where(datay_test == class_neg)[0]
    indexes_pos = np.where(datay_test == class_pos)[0]
    datax_test = np.vstack((datax_test[indexes_neg],
                            datax_test[indexes_pos]))
    datay_test = np.hstack((np.ones((len(indexes_neg),)) * label_neg,
                            np.ones((len(indexes_pos),)) * label_pos))

    datax_train, datay_train = _shuffle_data(datax_train, datay_train)
    datax_test, datay_test = _shuffle_data(datax_test, datay_test)
    return datax_train, datay_train, datax_test, datay_test


def load_usps_1_vs_all(class_pos, filename_train=PATH_DATA_USPS_TRAIN,
                       filename_test=PATH_DATA_USPS_TEST, label_neg=-1,
                       label_pos=1):
    with open(filename_train, "r") as f:
        f.readline()
        data = [[float(x) for x in l.split()] for l in f if len(l.split()) > 2]
    tmp = np.array(data)
    datax_train, datay_train = tmp[:, 1:], tmp[:, 0].astype(int)
    indexes_neg = np.where(datay_train != class_pos)[0]
    indexes_pos = np.where(datay_train == class_pos)[0]
    datax_train = np.vstack((datax_train[indexes_neg],
                             datax_train[indexes_pos]))
    datay_train = np.hstack((np.ones((len(indexes_neg),)) * label_neg,
                             np.ones((len(indexes_pos),)) * label_pos))

    with open(filename_test, "r") as f:
        f.readline()
        data = [[float(x) for x in l.split()] for l in f if len(l.split()) > 2]
    tmp = np.array(data)
    datax_test, datay_test = tmp[:, 1:], tmp[:, 0].astype(int)
    indexes_neg = np.where(datay_test != class_pos)[0]
    indexes_pos = np.where(datay_test == class_pos)[0]
    datax_test = np.vstack((datax_test[indexes_neg],
                            datax_test[indexes_pos]))
    datay_test = np.hstack((np.ones((len(indexes_neg),)) * label_neg,
                            np.ones((len(indexes_pos),)) * label_pos))

    datax_train, datay_train = _shuffle_data(datax_train, datay_train)
    datax_test, datay_test = _shuffle_data(datax_test, datay_test)
    return datax_train, datay_train, datax_test, datay_test


def _shuffle_data(datax, datay):
    """ Bouge aléatoirement la position de toutes les données tout en
    conservant l'ordre des exemples et des labels.
    """
    permutations = np.random.permutation(len(datax))
    return datax[permutations], datay[permutations]


if __name__ == '__main__':
    pass
