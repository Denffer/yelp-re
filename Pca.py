import json, uuid
import numpy as np
from sklearn import decomposition
#import matplotlib.pyplot as plt

class Pca:
    """ This program aims to (1) filter out redundant reviews (2) classify the reviews of the matched restaurants """

    def __init__(self):
        self.src = "./data/coreProcess_input/vectors100_word2vec.json"
        self.dst = "./data/coreProcess_input/vectors2.json"

    def get_vectors100(self):
        """ append every crawled business_list into source """

        source = []
        print "Loading data from:", self.src

        with open(self.src) as f:
            vectors100 = json.load(f)

        return vectors100

    def get_reduction(self):
        """ (1) get vectors100 (2) perform reduction by pca """
        source = self.get_vectors100()

        print "Performing reduction by pca"
        pca = decomposition.PCA(n_components=2)
        pca.fit(source)
        vectors2 = pca.transform(source).tolist()

        return vectors2

    def render(self):
        """ put keys in order and render json file """

        vectors2 = self.get_reduction()

        print "Writing data to:", self.dst

        f = open(self.dst, 'w+')
        f.write( json.dumps(vectors2))

        print "Done"

class NoIndent(object):
    def __init__(self, value):
        self.value = value

class NoIndentEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(NoIndentEncoder, self).__init__(*args, **kwargs)
        self.kwargs = dict(kwargs)
        del self.kwargs['indent']
        self._replacement_map = {}

    def default(self, o):
        if isinstance(o, NoIndent):
            key = uuid.uuid4().hex
            self._replacement_map[key] = json.dumps(o.value, **self.kwargs)
            return "@@%s@@" % (key,)
        else:
            return super(NoIndentEncoder, self).default(o)

    def encode(self, o):
        result = super(NoIndentEncoder, self).encode(o)
        for k, v in self._replacement_map.iteritems():
            result = result.replace('"@@%s@@"' % (k,), v)
        return result

if __name__ == '__main__':
    pca = Pca()
    pca.render()

