import json, sys, uuid, math, glob, scipy, os
import numpy as np
from scipy.spatial import distance
from json import dumps, loads, JSONEncoder, JSONDecoder
from operator import itemgetter
from collections import OrderedDict
from scipy import spatial

class CoreProcess:
    """ This program aim to
    1) Take 'unique_words.txt' & 'vector2.txt' & 'vector200.txt' & 'sentiment_statistics.json' & 'restaurnat_dict_list.json' as inputs
    1) Calculate the score by the cosine distance between the sentiment word (in 'sentimentWords.json') and every dish (in restaurant_list.json)
    2) Put in the values (x & y & vector2 & vector 200) of the words into 'sentimentWords.json' and the dishes in 'restaurant_list_*.json'
    """

    def __init__(self):
        """ initialize path and lists to be used """
        self.src_uw = "data/coreProcess_word2vec/unique_words_word2vec.txt"
        self.src_v2 = "data/coreProcess_word2vec/vectors2_word2vec.txt"
        self.src_v200 = "data/coreProcess_word2vec/vectors200_word2vec.txt"

        self.src_ss = "data/coreProcess_word2vec/sentiment_statistics.json"
        self.src_rdl = "data/coreProcess_word2vec/restaurant_dict_list.json"

        self.dst_ss = "data/postProcess_word2vec/processed_sentiment_statistics.json"
        self.dst_rdl = "data/postProcess_word2vec/processed_restaurant_dict_list.json"

        self.sentiment_words = []
        self.restaurant_dict_list = []
        self.verbose = 1

    def get_unique_words(self):
        """  return a list of words from 'unique_words.txt' """
        print "Loading data from", self.src_uw

        uw = [line.rstrip('\n') for line in open(self.src_uw)]
        #print uw
        return uw

    def get_vectors2(self):
        """  return a list of vectors in 2 dimensionv """
        print "Loading data from", self.src_v2

        v2 = [line.rstrip('\n') for line in open(self.src_v2)]
        #print v2
        return v2

    def get_vectors200(self):
        """  return a list of vectors in 200 dimensionv """
        print "Loading data from", self.src_v200

        v200 = [line.rstrip('\n') for line in open(self.src_v200)]
        #print v200
        return v200

    def get_sentiment_words(self):
        """ return a list of sentiment words """
        print "Loading data from", self.src_ss

        with open(self.src_ss) as f:
            source = json.load(f)

        sw = []     # sw stands for sentiment word
        for word_dict in source:
            sw.append(word_dict)
        #print sw
        return sw

    def get_restaurant_dict_list(self):
        """ return a list of restaurant_dict and its details """
        print "Loading data from", self.src_rdl

        with open(self.src_rdl) as f:
            source = json.load(f)

        rdl = []
        for restaurant_dict in source:
            rdl.append(restaurant_dict)
        # print rdl
        return rdl

    def put_vectors(self):
        """ put vectors200 and vectors2 into every matched word in unique_words """

        unique_words = self.get_unique_words()
        vectors2 = self.get_vectors2()
        vectors200 = self.get_vectors200()

        print "-"*80
        print "Putting vectors into words of sentiment_words matched with unique_words"

        uw_length = len(unique_words)
        sw_length = len(self.sentiment_words)
        rdl_length = len(self.restaurant_dict_list)

        for i in xrange(len(self.sentiment_words)):

            # initialize value
            self.sentiment_words[i]['x'] = 0
            self.sentiment_words[i]['y'] = 0
            self.sentiment_words[i]['v200'] = [0]*200

            for j in xrange(len(unique_words)):
                if self.sentiment_words[i]['word'] == unique_words[j]:
                    self.sentiment_words[i]['x'] = json.loads(vectors2[j])[0]
                    self.sentiment_words[i]['y'] = json.loads(vectors2[j])[1]
                    self.sentiment_words[i]['v200'] = json.loads(vectors200[j])

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s | %s / %s"%(i+1, sw_length, j+1, uw_length))
                    sys.stdout.flush()

        print "\n" + "-"*80
        print "Putting vectors into dishes in restaurant_dict_list matched with unique_words"
        for i in xrange(len(self.restaurant_dict_list)):
            rd_length = len(self.restaurant_dict_list[i]['menu'])

            # initialize every value
            for j in xrange(len(self.restaurant_dict_list[i]['menu'])):
                self.restaurant_dict_list[i]['menu'][j]['x'] = 0
                self.restaurant_dict_list[i]['menu'][j]['y'] = 0
                self.restaurant_dict_list[i]['menu'][j]['v200'] = [0]*200

            for j in xrange(len(self.restaurant_dict_list[i]['menu'])):
                for k in xrange(len(unique_words)):
                    if self.restaurant_dict_list[i]['menu'][j]['name_ar'] == unique_words[k]:
                        self.restaurant_dict_list[i]['menu'][j]['x'] = json.loads(vectors2[k])[0]
                        self.restaurant_dict_list[i]['menu'][j]['y'] = json.loads(vectors2[k])[1]
                        self.restaurant_dict_list[i]['menu'][j]['v200'] = json.loads(vectors200[k])

                    if self.verbose:
                        sys.stdout.write("\rStatus: %s / %s | %s / %s | %s / %s"%(i+1, rdl_length, j+1, rd_length, k+1, uw_length))
                        sys.stdout.flush()

        #self.sentiment_words = sentiment_words
        #self.restaurant_dict_list = restaurant_dict_list
        #return sentiment_words, restaurant_dict_list

    def put_scores(self):
        """ Calculate the Euclidean Distance """
        print "\n" + "-"*80
        print "Calculating Euclidean Distance of every dish and every sentiment word"

        rd_cnt = 0
        rdl_length = len(self.restaurant_dict_list)
        for restaurant_dict in self.restaurant_dict_list:
            rd_cnt += 1

            dd_cnt = 0 # dish_dict_count
            menu_length = len(restaurant_dict['menu'])
            for dish_dict in restaurant_dict['menu']:
                dd_cnt += 1
                dish_dict['avg_score'] = -2
                dish_dict['min_score'] = -2
                dish_dict['nearest'] = [{"word": None, "distance": None}]*5

                if dish_dict["v200"] != [0]*200: # Check if empty

                    """ cosine similarity """
                    similarity_list = []
                    similarity_dict_list = []

                    """ euclidean distance """
                    distance_list = []
                    distance_dict_list = []

                    sw_cnt = 0
                    sw_length = len(self.sentiment_words)
                    for sentiment_word_dict in self.sentiment_words:
                        sw_cnt += 1

                        """ cosine similarity """
                        cosine_distance = spatial.distance.cosine(sentiment_word_dict["v200"], dish_dict["v200"])
                        cosine_similarity = 1 - cosine_distance
                        similarity_list.append(cosine_similarity)
                        similarity_dict_list.append({"word": sentiment_word_dict["word"], "cosine_similarity": cosine_similarity})

                        """ euclidean distance """
                        euclidean_distance = distance.euclidean(sentiment_word_dict["v200"], dish_dict['v200'])
                        distance_list.append(euclidean_distance)
                        distance_dict = {"word": sentiment_word_dict["word"], "euclidean_distance": euclidean_distance}
                        distance_dict_list.append(distance_dict)

                        if self.verbose:
                            sys.stdout.write("\rStatus: %s / %s | %s / %s | %s / %s"%(rd_cnt, rdl_length, dd_cnt, menu_length, sw_cnt, sw_length))
                            sys.stdout.flush()

                    """ cosine similarity """
                    cosine_avg_score = sum(similarity_list)/len(similarity_list)
                    cosine_max_score = max(similarity_list)
                    dish_dict["cosine_avg_score"] = cosine_avg_score
                    dish_dict["cosine_max_score"] = cosine_max_score
                    dish_dict["cosine_nearest"] = sorted(simiarity_dict_list, key=itemgetter('cosine_similarity'))[:10]

                    """ euclidean distance """
                    euclidean_avg_score = 1/(sum(distance_list)/len(distance_list))
                    euclidean_min_score = 1/min(distance_list)
                    dish_dict["euclidean_avg_score"] = euclidean_avg_score
                    dish_dict["euclidean_min_score"] = euclidean_min_score
                    dish_dict["euclidean_nearest"] = sorted(distance_dict_list, key=itemgetter('euclidean_distance'))[:10]

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname("data/postProcess_word2vec/")

        if not os.path.exists(dir1):
            os.makedirs(dir1)

    def render(self):
        """ customize output json file """

        self.sentiment_words = self.get_sentiment_words()
        self.restaurant_dict_list = self.get_restaurant_dict_list()

        self.put_vectors()
        self.put_scores()

        self.create_dirs()

        print '\n' + '-'*80
        print "Customizing restaurant_dict_list's json format"

        processed_restaurant_dict_list = []
        rd_cnt = 0
        rdl_length = len(self.restaurant_dict_list)
        for restaurant_dict in self.restaurant_dict_list:
            rd_cnt += 1
            dd_cnt = 0 # dish_dict_count
            menu_length = len(restaurant_dict['menu'])

            rd_ordered_dict = OrderedDict()
            rd_ordered_dict['index'] = restaurant_dict['index']
            rd_ordered_dict['restaurant_name'] = restaurant_dict['restaurant_name']
            rd_ordered_dict['restaurant_id'] = restaurant_dict['restaurant_id']
            rd_ordered_dict['stars'] = restaurant_dict['stars']
            rd_ordered_dict['review_count'] = restaurant_dict['review_count']
            rd_ordered_dict['menu_length'] = restaurant_dict['menu_length']

            ordered_dict_list = []
            for dish_dict in restaurant_dict['menu']:
                dd_cnt += 1

                ordered_dict = OrderedDict()
                ordered_dict["index"] = dish_dict['index']
                ordered_dict["name"] = dish_dict['name']
                ordered_dict["name_ar"] = dish_dict['name_ar']
                ordered_dict["count"] = dish_dict['count']

                """ cosine """
                ordered_dict["cosine_avg_score"] = dish_dict['cosine_avg_score']
                ordered_dict["cosine_max_score"] = dish_dict['cosine_max_score']

                cosine_nearest = []
                for word_dict in dish_dict["cosine_nearest"]:
                    ordered_dict = OrderedDict()
                    ordered_dict["word"] = word_dict.get('word')
                    ordered_dict["cosine_similarity"] = word_dict.get('cosine_similarity')
                    cosine_nearest.append(ordered_dict)

                ordered_dict["cosine_nearest"] = NoIndent(euclidean_nearest)

                """ euclidean """
                ordered_dict["euclidean_avg_score"] = dish_dict['euclidean_avg_score']
                ordered_dict["euclidean_min_score"] = dish_dict['euclidean_min_score']

                euclidean_nearest = []
                for word_dict in dish_dict["euclidean_nearest"]:
                    ordered_dict = OrderedDict()
                    ordered_dict["word"] = word_dict.get('word')
                    ordered_dict["euclidean_distance"] = word_dict.get('euclidean_distance')
                    euclidean_nearest.append(ordered_dict)

                ordered_dict["euclidean_nearest"] = NoIndent(euclidean_nearest)

                ordered_dict["x"] = dish_dict['x']
                ordered_dict["y"] = dish_dict['y']
                ordered_dict["v200"] = NoIndent(dish_dict['v200'])
                ordered_dict_list.append(ordered_dict)

                if self.verbose:
                    sys.stdout.write("\rStatus: %s / %s | %s / %s"%(rd_cnt, rdl_length, dd_cnt, menu_length))
                    sys.stdout.flush()

            restaurant_dict['menu'] = ordered_dict_list
            rd_ordered_dict['menu'] = restaurant_dict['menu']

            processed_restaurant_dict_list.append(rd_ordered_dict)


        f1 = open(self.dst_rdl, "w+")
        f1.write(json.dumps(processed_restaurant_dict_list, indent = 4, cls=NoIndentEncoder))
        f1.close()

        print '\n' + '-'*80
        print "Customizing sentiment_statistics's json format"

        sw_cnt = 0
        sw_length = len(self.sentiment_words)

        ordered_dict_list1 = []

        for word_dict in self.sentiment_words:
            sw_cnt += 1

            ordered_dict1 = OrderedDict()
            ordered_dict1['index'] = word_dict['index']
            ordered_dict1['word'] = word_dict['word']
            ordered_dict1['count'] = word_dict['count']
            ordered_dict1['x'] = word_dict['x']
            ordered_dict1['y'] = word_dict['y']
            ordered_dict1['v200'] = NoIndent(word_dict['v200'])
            ordered_dict_list1.append(ordered_dict1)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(sw_cnt, sw_length))
                sys.stdout.flush()

        self.sentiment_words = ordered_dict_list1

        f2 = open(self.dst_ss, "w+")
        f2.write(json.dumps(self.sentiment_words, indent = 4, cls=NoIndentEncoder))
        f2.close()

        print '\n' + '-'*80
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
    coreProcess = CoreProcess()
    coreProcess.render()
