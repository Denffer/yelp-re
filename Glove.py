import itertools
import sys, os, uuid
from gensim.models.word2vec import Text8Corpus
from glove import Corpus, Glove
import json

class Glove:

    def __init__(self):
        self.src = "data/backend_reviews/"
        self.dst_uw = "data/coreProcess_glove/unique_words_glove.txt"
        self.dst_v200 = "data/coreProcess_glove/vectors200_glove.txt"

    def get_source(self):
        """ get every review in backend_reviews """

        src_files = []
        source = []
        print "Loading data from:", self.src

        cnt = 0
        length = len(os.listdir(self.src))
        for f in os.listdir(self.src):

            cnt += 1
            file_path = os.path.join(self.src, f)
            if os.path.isfile(file_path):
                #print "Found:", file_path
                with open(file_path) as f:
                   source.append(f.read())

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        #print source
        return source

    def get_sentences(self):
        """ get a list of lists of words | E.g. sentences = [["sentence","one"], ["sentence","two"]] """
        source = self.get_source()

        sentences = []
        for sentence in source:
            sentences.append(sentence.split())

        #print sentences
        return sentences

    def run_glove(self):
        """ run global vector """
        words = self.get_sentences()

        print '\n' + '-'*80
        print "Fitting words into corpus"
        corpus = Corpus()
        corpus.fit(words, window=10)

        print "Running Glove"
        glove = Glove(no_components=100, learning_rate=0.05)
        glove.fit(corpus.matrix, epochs=1, no_threads=10, verbose=True)
        glove.add_dictionary(corpus.dictionary)

        print "Fitting words and vectors into unique_words and vectors200"
        unique_words = []
        vectors200 = []

        cnt1 = 0
        length1 = len(glove.inverse_dictionary)
        for word_id in glove.inverse_dictionary:
            cnt1 += 1
            unique_words.append(glove.inverse_dictionary[word_id])
            vectors200.append(glove.word_vectors[word_id])

            sys.stdout.write("\rStatus: %s / %s"%(cnt1, length1))
            sys.stdout.flush()

        print '\n' + "Processing vectors200"
        processed_vectors200 = []
        processed_vector = []

        cnt2 = 0
        length2 = len(vectors200)
        for vector in vectors200:
            cnt2 += 1
            for float_num in vector:
                processed_vector.append(float_num)

            processed_vectors200.append(processed_vector)

            sys.stdout.write("\rStatus: %s / %s"%(cnt2, length2))
            sys.stdout.flush()

        return unique_words, processed_vectors200

    def create_folder(self):
        """ create folder (1) coreProcess_input """
        dir1 = os.path.dirname("data/coreProcess_input/")
        if not os.path.exists(dir1):   # if the directory does not exist
            os.makedirs(dir1)          # create the directory

    def render(self):
        """ render into two files """
        unique_words, vectors200 = self.run_glove()
        self.create_folder()

        print "\n" + "-"*80
        print "Writing data to", self.dst_uw
        with open(self.dst_uw, 'w+') as f3:
            for word in unique_words:
                f3.write( word + "\n")

        print "Writing data to", self.dst_v200
        with open(self.dst_v200, 'w+') as f4:
            for vector in vectors200:
                f4.write(str(vector) + '\n')

if __name__ == '__main__':
    glove = Glove()
    glove.render()

