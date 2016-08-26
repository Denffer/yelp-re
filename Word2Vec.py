import itertools
import sys, os, uuid
import gensim

import json

class Word2Vec:

    def __init__(self):
        """ initalize paths """
        self.src = "data/backend_reviews_1/"
        self.dst_core1 = "data/coreProcess_input/unique_words_word2vec.txt"
        self.dst_core2 = "data/coreProcess_input/vectors200_word2vec.txt"

        self.verbose = 1

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

    def run_word2vec(self):
        """ run word to vector """
        sentences = self.get_sentences()

        print '\n' + '-'*80
        print "Running Word2Vec"
        model = gensim.models.Word2Vec(sentences, min_count=3, size=100, window = 10, workers=4)
        unique_words = list(model.vocab.keys())

        vectors200 = []
        for word in unique_words:
            vectors200.append(model[word].tolist())

        #print unique_words, vectors200
        return unique_words, vectors200

    def create_folder(self):
        """ create folder (1) coreProcess_input """
        dir1 = os.path.dirname("data/coreProcess_input/")
        if not os.path.exists(dir1):   # if the directory does not exist
            os.makedirs(dir1)          # create the directory

    def render(self):
        """ render into two files """
        unique_words, vectors200 = self.run_word2vec()
        self.create_folder()

        print "-"*80
        print "Writing data to", self.dst_core1
        with open(self.dst_core1, 'w+') as f3:
            for word in unique_words:
                f3.write( word + "\n")

        print "Writing data to", self.dst_core2
        with open(self.dst_core2, 'w+') as f4:
            #f4.write(json.dumps(vectors200))
            for vector in vectors200:
                f4.write(str(vector) + '\n')

if __name__ == '__main__':
    word2vec = Word2Vec()
    word2vec.render()

