import itertools
import sys, os, uuid
from gensim.models.word2vec import Text8Corpus
from glove import Corpus, Glove

class GloVec:

    def __init__(self):
        self.src = "data/backend_reviews"
        #self.dst_tsne1 = "data/tsne_input/unique_words.txt"
        #self.dst_tsne2 = "data/tsne_input/str_vector200s.txt"
        self.dst_core1 = "data/coreProcess_input/unique_words.json"
        self.dst_core2 = "data/coreProcess_input/vectors200.json"

    def get_source(self):
        """ get every review in backend_reviews """

        src_files = []
        source = []
        print "Loading data from:", self.src
        for f in os.listdir(self.src):
            file_path = os.path.join(self.src, f)

            if os.path.isfile(file_path):
                #print "Found:", file_path
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
        glove.fit(corpus.matrix, epochs=1, no_threads=4, verbose=True)
        glove.add_dictionary(corpus.dictionary)

        unique_words = []
        vectors200 = []
        #str_vector200s = []

        for word_id in glove.inverse_dictionary:
            unique_words.append(glove.inverse_dictionary[word_id])
            vectors200.append(glove.word_vectors[word_id])

#            vector200s.append(str(glove.word_vectors[word_id]))

#            """ transform every decimal in the list into string format and concaternate them with space """
#            """ E.g. [0.111, 0.222] -> 0.111 0.222 """
#            str_decimal = ''
#            for decimal in glove.word_vectors[word_id]:
#                str_decimal += str(decimal) + ' '
#            str_vector200s.append(str_decimal)
#
        processed_vectors200 = []
        processed_vector = []
        for vector in vectors200:
            for float_num in vector:
                processed_vector.append(float(float_num))
            processed_vectors200.append(NoIndent(processed_vector))

        print type(vectors200)
        print type(processed_vectors200)
        return unique_words, processed_vectors200

    def create_folder(self):
        """ create folder (1) tsne_input (2) coreProcess_input """
        #dir1 = os.path.dirname("data/tsne_input/")
        dir2 = os.path.dirname("data/coreProcess_input/")
        #if not os.path.exists(dir1):   # if the directory does not exist
        #    os.makedirs(dir1)          # create the directory
        if not os.path.exists(dir2):   # if the directory does not exist
            os.makedirs(dir2)          # create the directory

    def render(self):
        """ render into two files """
        unique_words, vector200s = self.run_glove()

        self.create_folder()

#        with open(self.dst_tsne1, 'w+') as f1:
#            for word in unique_words:
#                f1.write(word + '\n')
#
#        with open(self.dst_tsne2, 'w+') as f2:
#            for vector in str_vector200s:
#                f2.write(vector + '\n')

        with open(self.dst_core1, 'w+') as f3:
            f3.write(json.dumps(unique_words, indent = 4))

        with open(self.dst_core2, 'w+') as f4:
            f4.write(json.dumps(vectors200, indent = 4, cls=NoIndentEncoder))

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
    gloVec = GloVec()
    #gloVec.run_glove()
    gloVec.render()

