
import itertools
from string import whitespace, punctuation
import re

import numpy as np


def string_kernel(d1, d2, n=2, lbda=0.1, normalize=True):
    # Calcul des features de la projection
    features = iter_features(d1, n=n)
    features = iter_features(d2, n=n, features=features)

    # Projection des données
    phi1, phi2 = string_projection(d1, n=n, lbda=lbda, features=features), \
        string_projection(d2, n=n, lbda=lbda, features=features)

    res = np.vdot(phi1, phi2)
    if normalize:
        return res / (np.linalg.norm(phi1) * np.linalg.norm(phi2))
    else:
        return res


def string_projection(document, n=2, lbda=0.5, features=[]):
    """ Effectue une projection d'un document de mots dans un espace de plus
    grande dimension.
    >>> document = np.array(["cat", "car", "bat", "bar"])
    >>> string_projection(document, n=2, lbda=0.5)
    [[ 0.25   0.125  0.25   0.     0.     0.     0.     0.   ]
     [ 0.25   0.     0.     0.125  0.25   0.     0.     0.   ]
     [ 0.     0.     0.25   0.     0.     0.25   0.125  0.   ]
     [ 0.     0.     0.     0.     0.25   0.25   0.     0.125]]
    """
    # Nettoyage du document
    document = np.vectorize(clean_string)(document)

    # Calcul des features de la projection
    features = iter_features(document, n=n, features=features)

    res = np.zeros((len(document), len(features)))
    for i_word, word in enumerate(document):
        for i_feature, feature in enumerate(features):
            min_occurency = len(smallest_occurency(word, feature))
            res[i_word, i_feature] = 0 if not min_occurency else\
                np.power(lbda, min_occurency)
    return res


def clean_string(string):
    """ Concatene tous les elements d'une string en ignorant les espaces et la
    ponctuation.
    """
    ignore_list = punctuation + whitespace
    return "".join(c for c in string if c not in ignore_list)


def iter_features(document, n, features=[]):
    """ Trouve toutes les features de taille `n` d'un document puis les
    retourne.
    """
    # Accumulate all features
    seen = set(features)
    for word in document:
        for feature in ("".join(w) for w in itertools.combinations(word, r=n)):
            if feature not in seen:
                seen.add(feature)
                features.append(feature)
    return features


def smallest_occurency(word, feature, subfeature=None, count=None):
    """ Retourne la plus petite occurence de `feature` dans `word`,
    possiblement séparée par d'autres caractères.
    """
    if len(feature) == 1:
        return 1 if feature in word else 0
    else:
        pattern = "(" + ".*".join(feature) + ")"
        all_occurencies = re.findall(pattern, word)
        try:
            return min(all_occurencies, key=len)
        except ValueError:
            # No match found
            return []


if __name__ == '__main__':
    d1 = np.array("science is organized knowledge".split())
    d2 = np.array("wisdom is organized life".split())
    print(string_kernel(d1, d2, n=3, lbda=0.5))
