# -*- coding: utf-8 -*-
""" Ce module contient toutes les fonctions nécessaires pour générer des
données artificielles.
"""

import numpy as np


def genere_gaussiennes_LS(nombre_exemples, epsilon=0, centerx=3, centery=-3):
    """ Utilise gen_arti pour générer des données gaussiennes linéairement
    séparables.
    """
    return gen_arti(centerx, centery, 0.1, nombre_exemples, 0, epsilon)


def genere_gaussiennes_NLS(nombre_exemples, epsilon=1, centerx=2, centery=-2):
    """ Utilise gen_arti pour générer des données gaussiennes non
    linéairement séparables.
    """
    return gen_arti(centerx, centery, 0.1, nombre_exemples, 0, epsilon)


def genere_XOR(nombre_exemples, epsilon=1, centerx=4, centery=-4):
    """ Utilise gen_arti pour générer des données gaussiennes formant le
    problème du XOR.
    """
    return gen_arti(centerx, centery, 0.02, nombre_exemples, 1, epsilon)


def genere_echiquier(nombre_exemples, epsilon=1, centerx=1, centery=1):
    """ Utilise gen_arti pour générer des données gaussiennes formant le
    problème de l'échiquier.
    """
    return gen_arti(centerx, centery, 0.1, nombre_exemples, 2, epsilon)


def gen_arti(centerx=1, centery=1, sigma=0.1, nbex=1000, data_type=0,
             epsilon=0.02):
    """ Generateur Artificielle, génère des données artificiellement.
        :param centerx: centre des gaussiennes
        :param centery:
        :param sigma: des gaussiennes
        :param nbex: nombre d'exemples
        :param data_type: 0: melange 2 gaussiennes,
                          1: melange 4 gaussiennes,
                          2:echequier
        :param epsilon: bruit dans les donnees
        :return: data matrice 2d des donnnes,y etiquette des donnnees
    """
    if data_type == 0:
        # melange de 2 gaussiennes
        xpos = np.random.multivariate_normal(
            [centerx, centerx], np.diag([sigma, sigma]), nbex // 2)
        xneg = np.random.multivariate_normal(
            [-centerx, -centerx], np.diag([sigma, sigma]), nbex // 2)
        data = np.vstack((xpos, xneg))
        y = np.hstack((np.ones(nbex // 2), -np.ones(nbex // 2)))

    if data_type == 1:
        # melange de 4 gaussiennes
        xpos = np.vstack((np.random.multivariate_normal([centerx, centerx],
                                                        np.diag(
                                                            [sigma, sigma]),
                                                        nbex // 4),
                          np.random.multivariate_normal([-centerx, -centerx],
                                                        np.diag(
                                                            [sigma, sigma]),
                                                        nbex // 4)))
        xneg = np.vstack((np.random.multivariate_normal([-centerx, centerx],
                                                        np.diag(
                                                            [sigma, sigma]),
                                                        nbex // 4),
                          np.random.multivariate_normal([centerx, -centerx],
                                                        np.diag(
                                                            [sigma, sigma]),
                                                        nbex // 4)))
        data = np.vstack((xpos, xneg))
        y = np.hstack((np.ones(nbex // 2), -np.ones(nbex // 2)))

    if data_type == 2:
        # echiquier
        data = np.reshape(np.random.uniform(-4, 4, 2 * nbex), (nbex, 2))
        y = np.ceil(data[:, 0]) + np.ceil(data[:, 1])
        y = 2 * (y % 2) - 1

    # un peu de bruit
    data[:, 0] += np.random.normal(0, epsilon, nbex)
    data[:, 1] += np.random.normal(0, epsilon, nbex)

    # on mélange les données
    idx = np.random.permutation((range(y.size)))
    data = data[idx, :]
    y = y[idx]

    return data, y


def make_grid(data=None, xmin=-5, xmax=5, ymin=-5, ymax=5, step=20):
    """ Cree une grille sous forme de matrice 2d de la liste des points
    :param data: pour calcluler les bornes du graphe
    :param xmin: si pas data, alors bornes du graphe
    :param xmax:
    :param ymin:
    :param ymax:
    :param step: pas de la grille
    :return: une matrice 2d contenant les points de la grille
    """
    if data is not None:
        xmax, xmin, ymax, ymin = np.max(data[:, 0]), np.min(
            data[:, 0]), np.max(data[:, 1]), np.min(data[:, 1])
    x, y = np.meshgrid(np.arange(xmin, xmax, (xmax - xmin) * 1. / step),
                       np.arange(ymin, ymax, (ymax - ymin) * 1. / step))
    grid = np.c_[x.ravel(), y.ravel()]
    return grid, x, y


if __name__ == '__main__':
    pass
