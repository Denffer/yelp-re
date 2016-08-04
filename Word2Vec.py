import os
import sys
import re
from collections import OrderedDict
import itertools

class Word2Vec:
    """ This program aims to (1) filter out redundant reviews (2) classify the reviews of the matched restaurants """

    def __init__(self):
        self.src_b = "./data/backend_reviews/"

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

    def get_cleaned_source(self):
        source = self.get_source()

        appostophes = {"'m":" am", "'re":" are", "'s":" is", "'ve": " have"}
        print "Cleaning data ..."
        for text in source:
            text = text.decode("utf-8").encode('ascii', 'ignore')
            text = ' '.join(re.findall('[A-Z][^A-Z]*', text)) # ThisIsAwesome -> This Is Awesome
            text = ' '.join([appostophes[word] if word in appostophes else word for word in text.split()])
            #FIXME #text = _slang_loopup(text) # luv -> love
            text = ''.join(''.join(s)[:2] for _, s in itertools.groupby(text)) # sooo happppppy -> so happy
            print text

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

if __name__ == '__main__':
    w2v = Word2Vec()
    w2v.get_cleaned_source()

