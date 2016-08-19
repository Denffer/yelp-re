import itertools
import sys, os
from gensim.models.word2vec import Text8Corpus
from glove import Corpus, Glove

class GloVec:

    def __init__(self):
        self.src = "data/backend_reviews_1"
        self.dst1 = "data/unique_words.txt"
        self.dst2 = "data/vector200s.txt"

    def get_source(self):
        """ get every review in backend_reviews """

        src_files = []
        source = []
        print "Loading data from:", self.src
        for f in os.listdir(self.src):
            file_path = os.path.join(self.src, f)

            if os.path.isfile(file_path):
                print "Found:", file_path
                with open(file_path) as f:
                   source.append(f.read())

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

        return words

#sentences = list(itertools.islice(Text8Corpus('text8'),None))
#print type(sentences)

    def run_glove(self):
        """ run global vector """
        words = self.get_words()

        print '\n' + '-'*80
        corpus = Corpus()
        corpus.fit(words, window=10)

        glove = Glove(no_components=200, learning_rate=0.05)
        glove.fit(corpus.matrix, epochs=5, no_threads=4, verbose=True)
        glove.add_dictionary(corpus.dictionary)

        unique_words = []
        vector200s = []
        for word_id in glove.inverse_dictionary:
            #print type(glove.word_vectors[word_id].tolist()[1])
            unique_words.append(glove.inverse_dictionary[word_id])

            str_decimal = ''
            for decimal in glove.word_vectors[word_id]:
                str_decimal += str(decimal) + ' '
            vector200s.append(str_decimal)
            #vector200s.append(str(glove.word_vectors[word_id]))

        return unique_words, vector200s

    def render(self):
        """ render into two files """
        unique_words, vector200s = self.run_glove()

        with open(self.dst1, 'w+') as f1:
            for word in unique_words:
                f1.write(word + '\n')

        with open(self.dst2, 'w+') as f2:
            for vector in vector200s:
                f2.write(vector + '\n')

if __name__ == '__main__':
    gloVec = GloVec()
    #gloVec.run_glove()
    gloVec.render()

