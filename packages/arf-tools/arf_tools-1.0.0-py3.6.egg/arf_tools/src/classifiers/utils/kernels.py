# -*- coding: utf-8 -*-
""" ARF - TME2, Estimation de densité
Contient tous les noyaux utilisés pour une estimation de densité.

Auteurs :
* BIZZOZZERO Nicolas
* ADOUM Robert

Source :
* https://en.wikipedia.org/wiki/Kernel_(statistics)
"""

import numpy as np


def parzen_ND(v):
    return 1 if np.linalg.norm(v) < 1 / 2 else 0


def gaussian_ND(v):
    d = len(v)
    return np.power((1 / np.sqrt(2 * np.pi)), d) * \
        np.exp(-0.5 * np.power(np.linalg.norm(v), 2))


if __name__ == '__main__':
    pass
