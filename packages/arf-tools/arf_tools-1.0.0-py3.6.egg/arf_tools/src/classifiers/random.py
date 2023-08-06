# -*- coding: utf-8 -*-
""" Ce module contient toutes les fonctions nécessaires pour implémenter un
classifieur aléatoire
"""


import numpy as np


class Random:
    def __init__(self):
        pass

    def fit(self, datax, datay):
        self.all_labels = np.array(list(set(datay)))

    def predict(self, datax):
        return np.random.choice(self.all_labels)

    def score(self, datax, datay):
        return (self.predict(datax) == datay).mean()


if __name__ == '__main__':
    pass
