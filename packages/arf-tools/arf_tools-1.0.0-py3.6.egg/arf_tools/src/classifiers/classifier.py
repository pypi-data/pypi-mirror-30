class Classifier(object):
    """ Classe generique d'un classifieur.
    Dispose de 3 méthodes :
        - `fit`, pour apprendre.
        - `predict` pour predire.
        - `score` pour évaluer la precision.
    """

    def fit(self, data, y):
        raise NotImplementedError()

    def predict(self, data):
        raise NotImplementedError()

    def score(self, data, y):
        return (self.predict(data) == y).mean()


if __name__ == '__main__':
    pass
