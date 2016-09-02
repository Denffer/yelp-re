import json, sys, uuid, math, glob, scipy, os
import numpy as np
from scipy.spatial import distance
from json import dumps, loads, JSONEncoder, JSONDecoder
from operator import itemgetter
from collections import OrderedDict

class PostProcess:
    """ This program aim to
    1) Take 'processed_sentiment_statistics.json' & 'processed_restaurant_dict_list_.json' as inputs
    2) Filter out those without scores or vector200
    3) Render top 5 dishes with the highest min_score and avg_score'
    """

    def __init__(self):
        """ initialize path and lists to be used """
        self.src_ss = "data/postProcess_word2vec/processed_sentiment_statistics.json"
        self.src_rdl = "data/postProcess_word2vec/processed_restaurant_dict_list.json"

        self.dst_ss = "data/website_word2vec/frontend_sentiment_statistics.json"
        self.dst_rdl = "data/website_word2vec/frontend_restaurant_dict_list.json"

        self.sentiment_statistics = []
        self.restaurant_dict_list = []
        self.verbose = 1

    def get_sentiment_statistics(self):
        """ return a list of sentiment words """
        print "Loading data from", self.src_ss

        with open(self.src_ss) as f:
            source = json.load(f)

        self.sentiment_statistics = source

    def get_restaurant_dict_list(self):
        """ return a list of restaurant_dict and its details """
        print "Loading data from", self.src_rdl

        with open(self.src_rdl) as f:
            source = json.load(f)

        self.restaurant_dict_list = source

    def remove_v200(self):
        """ remove vectors200 in (1) sentiment_statistics (2) restaurant_dict_list """
        """ put keys in order"""

        print "-"*80
        print "Removing vectors200 into sentiment_words"

        wd_cnt = 0
        sw_length = len(self.sentiment_statistics)
        sentiment_statistics = []
        for word_dict in self.sentiment_statistics:

            wd_cnt += 1
            del word_dict['v200']
            if word_dict['x'] == 0 and word_dict['y'] == 0:
                del word_dict
            else:
                sentiment_statistics.append(word_dict)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(wd_cnt, sw_length))
                sys.stdout.flush()

        self.sentiment_statistics = sentiment_statistics

        print "\n" + "-"*80
        print "Removing vectors200 into sentiment_worrestaurant_dict_list"

        rd_cnt = 0
        rdl_length = len(self.restaurant_dict_list)
        for restaurant_dict in self.restaurant_dict_list:

            rd_cnt += 1
            rd_length = len(restaurant_dict['menu'])

            menu = []
            for dish_dict in restaurant_dict['menu']:
                del dish_dict['v200']
                if dish_dict['x'] == 0 and dish_dict['y'] == 0:
                    del dish_dict
                else:
                    menu.append(dish_dict)

            restaurant_dict['menu'] = menu

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(rd_cnt, rdl_length))
                sys.stdout.flush()

    def get_customized_restaurant_dict_list(self):
        """ customize output json file """

        print '\n' + '-'*80
        print "Customizing restaurant_dict_list's json format"

        restaurant_ordered_dict_list = []
        rd_cnt = 0
        rdl_length = len(self.restaurant_dict_list)
        for restaurant_dict in self.restaurant_dict_list:

            rd_cnt += 1

            restaurant_ordered_dict = OrderedDict()
            restaurant_ordered_dict['index'] = restaurant_dict['index']
            restaurant_ordered_dict['restaurant_name'] = restaurant_dict['restaurant_name']
            restaurant_ordered_dict['restaurant_id'] = restaurant_dict['restaurant_id']
            restaurant_ordered_dict['stars'] = restaurant_dict['stars']
            restaurant_ordered_dict['review_count'] = restaurant_dict['review_count']

            dish_dict_cnt = 0
            ordered_menu = []
            for dish_dict in restaurant_dict['menu']:
                dish_dict_cnt += 1

                ordered_dish_dict = OrderedDict()

                ordered_dish_dict = OrderedDict()
                ordered_dish_dict["index"] = dish_dict_cnt
                ordered_dish_dict["name"] = dish_dict['name']
                ordered_dish_dict["name_ar"] = dish_dict['name_ar']
                ordered_dish_dict["count"] = dish_dict['count']

                """ cosine """
                ordered_dish_dict["cosine_avg_score"] = dish_dict['cosine_avg_score']
                ordered_dish_dict["cosine_max_score"] = dish_dict['cosine_max_score']

                cosine_nearest = []
                for word_dict in dish_dict["cosine_nearest"]:
                    ordered_word_dict = OrderedDict()
                    ordered_word_dict["word"] = word_dict.get('word')
                    ordered_word_dict["cosine_similarity"] = word_dict.get('cosine_similarity')
                    cosine_nearest.append(ordered_word_dict)

                ordered_dish_dict["cosine_nearest"] = NoIndent(cosine_nearest)
                """ cosine """

                """ euclidean """
                ordered_dish_dict["euclidean_avg_score"] = dish_dict['euclidean_avg_score']
                ordered_dish_dict["euclidean_min_score"] = dish_dict['euclidean_min_score']

                euclidean_nearest = []
                for word_dict in dish_dict["euclidean_nearest"]:
                    ordered_word_dict2 = OrderedDict()
                    ordered_word_dict2["word"] = word_dict.get('word')
                    ordered_word_dict2["euclidean_distance"] = word_dict.get('euclidean_distance')
                    euclidean_nearest.append(ordered_word_dict2)

                ordered_dish_dict["euclidean_nearest"] = NoIndent(euclidean_nearest)
                """ euclidean """

                ordered_dish_dict["x"] = dish_dict['x']
                ordered_dish_dict["y"] = dish_dict['y']
                ordered_menu.append(ordered_dish_dict)

            #restaurant_ordered_dict['menu'] = ordered_menu

            """ (1) top5_frequent (2) top5_cosine_avg (3) top5_cosine_max (4) top5_euclidean_avg (5) top5_euclidean_min """
            restaurant_ordered_dict["top5_frequent"] = sorted(ordered_menu, key=itemgetter('count'), reverse=True)[:5]
            restaurant_ordered_dict["top5_frequent"] = self.get_reindex(restaurant_ordered_dict["top5_frequent"])

            restaurant_ordered_dict["top5_cosine_avg"] = sorted(ordered_menu, key=itemgetter('cosine_avg_score'), reverse=True)[:5]
            restaurant_ordered_dict["top5_cosine_avg"] = self.get_reindex(restaurant_ordered_dict["top5_cosine_avg"])

            restaurant_ordered_dict["top5_cosine_max"] = sorted(ordered_menu, key=itemgetter('cosine_max_score'), reverse=True)[:5]
            restaurant_ordered_dict["top5_cosine_max"] = self.get_reindex(restaurant_ordered_dict["top5_cosine_max"])

            restaurant_ordered_dict["top5_euclidean_avg"] = sorted(ordered_menu, key=itemgetter('euclidean_avg_score'), reverse=True)[:5]
            restaurant_ordered_dict["top5_euclidean_avg"] = self.get_reindex(restaurant_ordered_dict["top5_euclidean_avg"])

            restaurant_ordered_dict["top5_euclidean_min"] = sorted(ordered_menu, key=itemgetter('euclidean_min_score'), reverse=True)[:5]
            restaurant_ordered_dict["top5_euclidean_min"] = self.get_reindex(restaurant_ordered_dict["top5_euclidean_min"])

            restaurant_ordered_dict_list.append(restaurant_ordered_dict)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(rd_cnt, rdl_length))
                sys.stdout.flush()

        self.restaurant_dict_list = restaurant_ordered_dict_list
        print self.restaurant_dict_list[1]['top5_euclidean_avg']

    def get_reindex(self, input_dict_list):
        """ re-index sorted ordered_dict_list """

        cnt = 0
        processed_dict_list = []
        for word_dict in input_dict_list:
            cnt += 1
            word_dict["index"] = cnt
            processed_dict_list.append(word_dict)

        return processed_dict_list

    def get_customized_sentiment_statistics(self):

        print '\n' + '-'*80
        print "Customizing sentiment_statistics's json format"

        sw_cnt = 0
        sw_length = len(self.sentiment_statistics)

        ordered_word_dict_list = []

        for word_dict in self.sentiment_statistics:
            sw_cnt += 1

            ordered_word_dict = OrderedDict()
            ordered_word_dict['index'] = sw_cnt
            ordered_word_dict['word'] = word_dict['word']
            ordered_word_dict['count'] = word_dict['count']
            ordered_word_dict['x'] = word_dict['x']
            ordered_word_dict['y'] = word_dict['y']
            ordered_word_dict_list.append(ordered_word_dict)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(sw_cnt, sw_length))
                sys.stdout.flush()

        self.sentiment_words = ordered_word_dict_list

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname("data/website_word2vec/")

        if not os.path.exists(dir1):
            os.makedirs(dir1)

    def render(self):

        self.get_sentiment_statistics()
        self.get_restaurant_dict_list()

        self.remove_v200()
        self.get_customized_restaurant_dict_list()
        self.get_customized_sentiment_statistics()

        self.create_dirs()

        f1 = open(self.dst_rdl, "w+")
        f1.write(json.dumps(self.restaurant_dict_list, indent = 4, cls=NoIndentEncoder))
        f1.close()

        f2 = open(self.dst_ss, "w+")
        f2.write(json.dumps(self.sentiment_statistics, indent = 4, cls=NoIndentEncoder))
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
    postProcess = PostProcess()
    postProcess.render()
