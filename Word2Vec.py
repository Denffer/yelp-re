import os
import sys
import re
from collections import OrderedDict
import itertools

class Word2Vec:
    """ This program aims to (1) filter out redundant reviews (2) classify the reviews of the matched restaurants """

    def __init__(self):
        self.src_b = "./data/review_test/"

    def get_source(self):
        """ get every review in backend_reviews """

        src_files = []
        source = []
        print "Loading data from:", self.src_b
        for f in os.listdir(self.src_b):
            file_path = os.path.join(self.src_b, f)

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
            print words

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        return words

	abulary_size = 50000

    def build_dataset(words):
        count = [['UNK', -1]]
        count.extend(collections.Counter(words).most_common(vocabulary_size - 1))
        dictionary = dict()
        for word, _ in count:
            dictionary[word] = len(dictionary)
            data = list()
            unk_count = 0
            for word in words:
                if word in dictionary:
                    index = dictionary[word]
                else:
                    index = 0  # dictionary['UNK']
                    unk_count += 1
                data.append(index)
            count[0][1] = unk_count
            reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
        return data, count, dictionary, reverse_dictionary

	#del words  # Hint to reduce memory.

if __name__ == '__main__':
    w2v = Word2Vec()
    w2v.get_words()
    data, count, dictionary, reverse_dictionary = build_dataset(words)
