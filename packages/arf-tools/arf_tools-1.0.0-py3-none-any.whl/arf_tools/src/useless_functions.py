# -*- coding: utf-8 -*-
""" Ce module contient de multiples fonctions ainsi que leurs dérivées utiles
à la descente de gradient.
"""

import numpy as np


def xcosx_1D(x):
    """ Return the value of the xcosx function. """
    return x * np.cos(x)


def xcosx_1D_d(x):
    """ Return the value of the xcosx function's derivative. """
    return np.cos(x) - (x * np.sin(x))


def minuslogxxtwo_1D(x):
    """ Return the value of the minuslogxxtwo function. """
    return -np.log(x) + np.power(x, 2)


def minuslogxxtwo_1D_d(x):
    """ Return the value of the minuslogxxtwo function's derivative. """
    return -(1 / x) + (2 * x)


def rosenbrock_2D(x1, x2):
    """ Return the value of the Rosenbrock function. """
    return 100 * np.power(x2 - np.power(x1, 2), 2) + np.power(1 - x1, 2)


def rosenbrock_2D_d(x1, x2):
    """ Return the value of the Rosenbrock function's derivative. """
    # return 2 * (-1 + x1 + (200 * np.power(x1, 3)) - (200 * x1 * x2)),\
    #     200 * (np.power(-x1, 2) + x2)
    return 100 * (-4 * x2 * x1 + 4 * x1 ** 3) + (-2 * x1 + 2 * x1),\
        2 * x2 - 2 * x1 ** 2


if __name__ == '__main__':
    pass
