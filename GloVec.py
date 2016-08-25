import itertools
import sys, os, uuid
from gensim.models.word2vec import Text8Corpus
from glove import Corpus, Glove
import json

class GloVec:

    def __init__(self):
        self.src = "data/glovec_input/backend_reviews.txt"
        self.dst_core1 = "data/coreProcess_input/unique_words_glovec.txt"
        self.dst_core2 = "data/coreProcess_input/vectors100_glovec.txt"

    def get_source(self):
        """ get every review in backend_reviews """

        print "Loading data from:", self.src
        with open(self.src) as f:
            source = f.readlines()

        #print source
        return source

    def get_words(self):
        """ transform source into a list of words """
        source = self.get_source()
        words = []

        cnt = 0
        length = len(source)
        for s in source:
            words.append(s.split())

            cnt += 1
            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        #print words
        return words

    def run_glove(self):
        """ run global vector """
        words = self.get_words()

        print '\n' + '-'*80
        print "Fitting words into corpus"
        corpus = Corpus()
        corpus.fit(words, window=10)

        print "Running GloVec"
        glove = Glove(no_components=100, learning_rate=0.05)
        glove.fit(corpus.matrix, epochs=1, no_threads=10, verbose=True)
        glove.add_dictionary(corpus.dictionary)

        print "Fitting words and vectors into unique_words and vectors100"
        unique_words = []
        vectors100 = []

        cnt1 = 0
        length1 = len(glove.inverse_dictionary)
        for word_id in glove.inverse_dictionary:
            cnt1 += 1
            unique_words.append(glove.inverse_dictionary[word_id])
            vectors100.append(glove.word_vectors[word_id])

            sys.stdout.write("\rStatus: %s / %s"%(cnt1, length1))
            sys.stdout.flush()

        print '\n' + "Processing vectors100"
        processed_vectors100 = []
        processed_vector = []

        cnt2 = 0
        length2 = len(vectors100)
        for vector in vectors100:
            cnt2 += 1
            for float_num in vector:
                processed_vector.append(float_num)

            processed_vectors100.append(processed_vector)

            sys.stdout.write("\rStatus: %s / %s"%(cnt2, length2))
            sys.stdout.flush()

        return unique_words, processed_vectors100

    def create_folder(self):
        """ create folder (1) coreProcess_input """
        dir1 = os.path.dirname("data/coreProcess_input/")
        if not os.path.exists(dir1):   # if the directory does not exist
            os.makedirs(dir1)          # create the directory

    def render(self):
        """ render into two files """
        unique_words, vectors100 = self.run_glove()
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
                f4.write(str(vector) + '\n')

if __name__ == '__main__':
    gloVec = GloVec()
    #gloVec.run_glove()
    gloVec.render()

