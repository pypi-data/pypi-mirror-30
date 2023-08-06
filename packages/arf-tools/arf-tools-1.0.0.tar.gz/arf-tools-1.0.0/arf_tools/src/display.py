# -*- coding: utf-8 -*-
""" This module contains all methods related to displaying data and plotting
stuff.
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

from data_generation import make_grid


PARIS_MAP = 'res/paris-48.806-2.23--48.916-2.48.jpg'
XMIN, XMAX = 2.23, 2.48
YMIN, YMAX = 48.806, 48.916


def plot_histo_2D(x_histo, f_histo, grad_histo, show=True):
    """ Plot un graphe en 2D représentant les valeurs de f et du gradient de
    f en fonction des itérations de x.
    """
    plt.plot(x_histo, f_histo, '+', label="f(x)")
    plt.plot(x_histo, grad_histo, '*', label=u"∇f(x)")
    plt.xlim(min(x_histo), max(x_histo))
    plt.ylim(min(min(f_histo), min(grad_histo)),
             max(max(f_histo), max(grad_histo)))
    plt.xlabel("x")
    plt.ylabel(u"f(x) et ∇f(x)")
    plt.legend(loc=2)
    if show:
        plt.show()


def plot_opti_2D(fonc, x_histo, f_histo, show=True):
    """ Plot un graphe en 2D représentant la fonction f ainsi que la
    trajectoire de l'optimisation de f.
    """
    plt.plot(x_histo, fonc(x_histo), label="f(x)")
    plt.plot(x_histo, f_histo, "+", label="f(x^t)")
    plt.xlim(min(x_histo), max(x_histo))
    plt.ylim(min(f_histo), max(f_histo))
    plt.xlabel("x")
    plt.ylabel(u"f(x) et f(x^t)")
    plt.legend(loc=3)
    if show:
        plt.show()


def plot_logx_2D(x_histo, show=True):
    """ Plot un graphe en 2D représentant l'evolution de la distance
    logarithmique de chaque x avec le x final en fonction des itérations.
    """
    x_star = x_histo[-1]
    logx = np.array([np.log(np.linalg.norm(x - x_star)) for x in x_histo])
    plt.plot(range(len(x_histo)), logx, label="log(||x^t − x^*||)")
    plt.xlim(0, len(x_histo) - 1)
    plt.xlabel("t")
    plt.ylabel(u"log(||x^t − x^*||)")
    plt.legend(loc=3)
    if show:
        plt.show()


def plot_3D(x_histo, f_histo, grad_histo, fonc, show=True):
    # Grille de discretisation
    grid, xx, yy = make_grid(xmin=-1, xmax=1, ymin=-1, ymax=1)

    # # Affichage 2D
    # plt.contourf(xx, yy, grid.reshape(xx.shape))
    fig = plt.figure()

    # Construction du référentiel 3D
    ax = fig.gca(projection='3d')
    result_fonc = np.array([fonc(*case) for case in grid])
    surf = ax.plot_surface(xx, yy, result_fonc.reshape(xx.shape),
                           rstride=1, cstride=1, cmap=cm.gist_rainbow,
                           linewidth=0, antialiased=False)
    fig.colorbar(surf)
    ax.plot(x_histo[:, 0], x_histo[:, 1], f_histo.ravel(), color="black")
    if show:
        plt.show()


def plot_poi_density_in_map(estimateur, data, type_poi, steps=100, xmin=XMIN,
                            xmax=XMAX, ymin=YMIN, ymax=YMAX, transparence=0.3,
                            taille=0.8, color="r", title=None):
    """ Affiche une prediction d'un modèle estimant une densité de
    probabilité d'un POI.
    ATTENTION : Le modèle doit posséder une méthode `predict` pour sa
    prediction, et elle doit renvoyer une np.array.
    """
    # discretisation pour l'affichage des modeles d'estimation de densite
    xx, yy = np.meshgrid(np.linspace(xmin, xmax, steps),
                         np.linspace(ymin, ymax, steps))
    grid = np.c_[yy.ravel(), xx.ravel()]  # Les coordonnées sont inversées

    # Estimation de densité
    prediction = estimateur.predict(grid).reshape(steps, steps)

    # Affichage de la prediction
    plot_poi_in_map(data, type_poi, prediction, transparence=transparence,
                    taille=taille, color=color, title=title)


def plot_poi_in_map(data, type_poi, prediction=None, xmin=XMIN, xmax=XMAX,
                    ymin=YMIN, ymax=YMAX, transparence=0.3, taille=1,
                    color="r", title=None, show=True):
    """ Plot la carte de paris, les POI et optionnellement une estimation de
    densité sur une figure matplotlib.
    """
    plt.ion()
    plt.figure()
    plot_map()
    plot_poi(data, type_poi, transparence=transparence, taille=taille,
             color=color)

    # Affiche optionnel d'une prediction
    if prediction is not None:
        plot_densite(prediction, transparence=transparence)

    # Informations de la figure
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    if title:
        plt.title(title)
    else:
        plt.title(("Estimation de densité pour le POI {poi}"
                   "").format(poi=type_poi))

    if show:
        plt.show(block=True)


def plot_map(paris_map=PARIS_MAP, xmin=XMIN, xmax=XMAX, ymin=YMIN, ymax=YMAX,
             show=False):
    """ Plot la carte de Paris sur une figure matplotlib. """
    plt.imshow(mpimg.imread(paris_map), extent=[xmin, xmax, ymin, ymax],
               aspect=1.5)
    if show:
        plt.show(block=True)


def plot_poi(data, type_poi, transparence=0.3, taille=1, color="r",
             show=False):
    """ Plot des POI sur une figure matplotlib. """
    geo_mat = _compute_geo_mat(data, type_poi)
    plt.scatter(geo_mat[:, 1], geo_mat[:, 0], alpha=transparence,
                s=taille, c=color)
    if show:
        plt.show(block=True)


def plot_densite(prediction, xmin=XMIN, xmax=XMAX, ymin=YMIN, ymax=YMAX,
                 transparence=0.3, show=False):
    """ Plot une prediction d'un modèle estimant une densité de
    probabilité sur une figure matplotlib.
    """
    plt.imshow(prediction, extent=[xmin, xmax, ymin, ymax],
               interpolation='none', alpha=transparence, origin="lower")
    plt.colorbar()
    if show:
        plt.show(block=True)


def _compute_geo_mat(data, type_poi):
    geo_mat = np.zeros((len(data), 2))
    for i, (x, y) in enumerate(data):
        geo_mat[i, :] = (x, y)
    return geo_mat


def plot_error(datax, datay, f, w_histo=None, step=10, show=False):
    grid, x1list, x2list = make_grid(xmin=-4, xmax=4, ymin=-4, ymax=4)
    plt.contourf(x1list, x2list,
                 np.array([f(datax, datay, w)
                           for w in grid]).reshape(x1list.shape), 25)
    plt.colorbar()

    # Cas où l'historique d'une descente de gradient est disponible
    if w_histo is not None:
        pass

    if show:
        plt.show()


def plot_data(data, labels=None):
    """
    Affiche des donnees 2D
    :param data: matrice des donnees 2d
    :param labels: vecteur des labels (discrets)
    :return:
    """
    cols = ["red", "green", "blue", "orange", "black", "cyan"]
    marks = [".", "+", "*", "o", "x", "^"]
    if labels is None:
        plt.scatter(data[:, 0], data[:, 1], marker="x")
        return
    for i, l in enumerate(sorted(list(set(labels.flatten())))):
        plt.scatter(data[labels == l, 0], data[
                    labels == l, 1], c=cols[i], marker=marks[i])


def plot_frontiere(data, f, step=20):
    """ Trace un graphe de la frontiere de decision de f
    :param data: donnees
    :param f: fonction de decision
    :param step: pas de la grille
    :return:
    """
    grid, x, y = make_grid(data=data, step=step)
    plt.contourf(x, y, f(grid).reshape(x.shape),
                 colors=('gray', 'blue'), levels=[-1, 0, 1])


def show_usps(data, show=True):
    plt.imshow(data.reshape((16, 16)), interpolation="nearest", cmap="gray")
    if show:
        plt.show()


def show_argmax_pixel_classes(data, show=True):
    sns.heatmap(data.reshape((16, 16)), annot=True, fmt="d", vmin=0, vmax=9,
                cbar=False, cmap="YlGnBu")
    if show:
        plt.xticks([], [])
        plt.yticks([], [])
        plt.show()


if __name__ == '__main__':
    pass
