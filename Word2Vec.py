import itertools
import sys, os, uuid
from gensim.models import Word2Vec

import json

class Word2Vec:

    def __init__(self):
        self.src = "data/glovec_input/backend_reviews"
        self.dst_core1 = "data/coreProcess_input/unique_words_word2vec.txt"
        self.dst_core2 = "data/coreProcess_input/vectors100_word2vec.txt"

    def get_sentences(self):
        """ get every review in backend_reviews """

        sentences = []
        print "Loading data from:", self.src
        with open(self.src) as f:
            sentences = json.load(f)

        return sentences

    def run_word2vec(self):
        """ run word to vector """
        sentences = self.get_sentences()
        min_count = 2
        size = 100
        window = 4

        print '\n' + '-'*80
        print "Running Word2Vec"
        model = Word2Vec(sentences, min_count=min_count, size=size, window=window)
        unique_words = list(model.vocab.keys())

        print unique_words, model
        return unique_words, model

    def create_folder(self):
        """ create folder (1) coreProcess_input """
        dir1 = os.path.dirname("data/coreProcess_input/")
        if not os.path.exists(dir1):   # if the directory does not exist
            os.makedirs(dir1)          # create the directory

    def render(self):
        """ render into two files """
        unique_words, vectors100 = self.run_word2vec()
        self.create_folder()

        print "\n" + "-"*80
        print "Writing data to", self.dst_core1
        with open(self.dst_core1, 'w+') as f3:
            for word in unique_words:
                f3.write( word + "\n")

        print "Writing data to", self.dst_core2
        with open(self.dst_core2, 'w+') as f4:
            #f4.write(json.dumps(vectors100))
            for vector in vectors100:
                print vector
                f4.write(str(vector) + '\n')

if __name__ == '__main__':
    word2vec = Word2Vec()
    word2vec.render()

