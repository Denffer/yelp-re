import json, sys, uuid, re
from collections import OrderedDict
from operator import itemgetter
from itertools import groupby

class LexiconMaker:
    """ This program aims to 
    (1) extract useful information out of the raw lexicon
    (2) render lexicon.json with only positive words  
    """

    def __init__(self):
        self.src = "./data/lexicon/subjectivity_clues_hltemnlp05/subjclueslen1-HLTEMNLP05.tff"
        self.dst = "./data/lexicon/lexicon.json"

    def get_source(self):
        """ append every line into source """

        source = []
        print "Loading data from:", self.src
        with open(self.src) as f:
            for line in f:
                source.append(line)

        return source

    def get_lexicon(self):
        """ (1) get every line in source (2) filter unwanted (3) append to lexicon """
        source = self.get_source()

        lexicon = []
        word_dict = {}
        cnt = 0
        length = len(source)

        for line in source:
            cnt += 1
            strength = re.search('type=(.+?)subj', line).group(1)
            word = re.search('word1=(.+?) ', line).group(1)
            polarity = re.search('priorpolarity=(.+?)', line).group(1)
            
            word_dict = {"strength": strength, "word": word, "polarity": polarity}
            lexicon.append(word_dict)

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        lexicon[:] = [word_dict for word_dict in lexicon if word_dict.get('polarity') == 'p']
        
        lexicon = [dict(t) for t in set([tuple(word_dict.items()) for word_dict in lexicon])]
        lexicon = sorted(lexicon, key=itemgetter('word'))

        #print lexicon
        return lexicon

    def render(self):
        """ put keys in order and render json file """

        lexicon = self.get_lexicon()

        print "\n" + "-"*100
        print "Writing data to:", self.dst

        cnt = 0
        length = len(lexicon)
        ordered_dict_list = []

        for word_dict in lexicon:

            cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt
            ordered_dict["word"] = word_dict["word"]
            ordered_dict["polarity"] = word_dict["polarity"]
            ordered_dict["strength"] = word_dict["strength"]

            ordered_dict_list.append(NoIndent(ordered_dict))

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        f = open(self.dst, 'w+')
        f.write( json.dumps(ordered_dict_list, indent = 4, cls=NoIndentEncoder))

        print "\n" + "-"*100
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
    lexiconMaker = LexiconMaker()
    lexiconMaker.render()
