""" This module contains all methods used for evaluating density functions.

Authors :
* BIZZOZZERO Nicolas
* ADOUM Robert
"""

import numpy as np

import utils.kernels as kernels


class EstimateurHistogramme:
    def __init__(self, steps=100):
        self.steps = steps
        self.tab = np.array([np.array([0 for _ in range(self.steps)])
                             for _ in range(self.steps)])

    def fit(self, data):
        # Calcul des extremums et des pas en fonction des données
        self.xmin, self.xmax = data[:, 0].min(), data[:, 0].max()
        self.ymin, self.ymax = data[:, 1].min(), data[:, 1].max()
        self.step_x = (self.xmax - self.xmin) / self.steps
        self.step_y = (self.ymax - self.ymin) / self.steps

        # Apprentissage
        for poi_x, poi_y in data:
            bin_x = self._bin_x(poi_x)
            bin_y = self._bin_y(poi_y)
            self.tab[bin_y, bin_x] += 1

        # Normalisation
        self.tab = self.tab / len(data)

    def predict(self, liste_points):
        tab = []
        for poi_x, poi_y in liste_points:
            bin_x = self._bin_x(poi_x)
            bin_y = self._bin_y(poi_y)
            tab.append(self.tab[bin_y][bin_x])
        return np.array(tab)

    def _bin_x(self, poi_x):
        """ Transforme un echantillon en dehors du domaine de l'estimateur en
        un echantillon dans le domaine de l'estimateur.
        Applicable sur l'axe X.
        """
        if poi_x < self.xmin:
            return 0
        elif poi_x >= self.xmax:
            return -1
        else:
            return int((poi_x - self.xmin) // self.step_x)

    def _bin_y(self, poi_y):
        """ Transforme un echantillon en dehors du domaine de l'estimateur en
        un echantillon dans le domaine de l'estimateur.
        Applicable sur l'axe Y.
        """
        if poi_y < self.ymin:
            return 0
        elif poi_y >= self.ymax:
            return -1
        else:
            return int((poi_y - self.ymin) // self.step_y)


class EstimateurNoyau:
    def __init__(self, noyau=kernels.parzen_ND, fenetre=0.8):
        self.noyau = noyau
        self.fenetre = fenetre

    def fit(self, data):
        self.data = data
        self.N, self.d = data.shape

    def predict(self, liste_points):
        tab = []
        for point in liste_points:
            # On somme tous les points
            somme = np.array([self.noyau((point - xi) / self.fenetre)
                              for xi in self.data]).sum()

            # On normalise
            somme /= self.N

            tab.append(somme)
        return np.array(tab)


if __name__ == '__main__':
    pass
