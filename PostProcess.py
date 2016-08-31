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

    def remove_vectors200(self):
        """ remove vectors200 in (1) sentiment_statistics (2) restaurant_dict_list """

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

            restaurant_dict["top5_avg"] = sorted(restaurant_dict['menu'], key=itemgetter('avg_score'), reverse=True)[:5]
            restaurant_dict["top5_min"] = sorted(restaurant_dict['menu'], key=itemgetter('min_score'), reverse=True)[:5]

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(rd_cnt, rdl_length))
                sys.stdout.flush()


    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname("data/website_word2vec/")

        if not os.path.exists(dir1):
            os.makedirs(dir1)

    def render(self):
        """ customize output json file """

        self.get_sentiment_statistics()
        self.get_restaurant_dict_list()
        self.remove_vectors200()

        self.create_dirs()

        print '\n' + '-'*80
        print "Customizing frontend_restaurant_dict_list's json format"

        frontend_restaurant_dict_list = []
        rd_cnt = 0
        rdl_length = len(self.restaurant_dict_list)
        for restaurant_dict in self.restaurant_dict_list:

            rd_cnt += 1

            rd_ordered_dict = OrderedDict()
            rd_ordered_dict['index'] = restaurant_dict['index']
            rd_ordered_dict['restaurant_name'] = restaurant_dict['restaurant_name']
            rd_ordered_dict['restaurant_id'] = restaurant_dict['restaurant_id']
            rd_ordered_dict['stars'] = restaurant_dict['stars']
            rd_ordered_dict['review_count'] = restaurant_dict['review_count']

            dd_cnt1 = 0 # dish_dict_count
            ordered_dict_list1 = []
            for dish_dict in restaurant_dict['top5_avg']:

                dd_cnt1 += 1

                ordered_dict = OrderedDict()
                ordered_dict["index"] = dd_cnt1
                ordered_dict["name"] = dish_dict['name']
                ordered_dict["name_ar"] = dish_dict['name_ar']
                ordered_dict["count"] = dish_dict['count']
                ordered_dict["avg_score"] = dish_dict['avg_score']
                ordered_dict["min_score"] = dish_dict['min_score']


                nearest = []
                for word_dict in dish_dict["nearest"]:
                    ordered_dict2 = OrderedDict()
                    ordered_dict2["word"] = word_dict.get('word')
                    ordered_dict2["distance"] = word_dict.get('distance')
                    nearest.append(ordered_dict2)

                ordered_dict["nearest"] = NoIndent(nearest)
                ordered_dict["x"] = dish_dict['x']
                ordered_dict["y"] = dish_dict['y']
                ordered_dict_list1.append(ordered_dict)

            restaurant_dict['top5_avg'] = ordered_dict_list1

            ##

            dd_cnt2 = 0 # dish_dict_count
            ordered_dict_list2 = []
            for dish_dict in restaurant_dict['top5_min']:

                dd_cnt2 += 1

                ordered_dict = OrderedDict()
                ordered_dict["index"] = dd_cnt2
                ordered_dict["name"] = dish_dict['name']
                ordered_dict["name_ar"] = dish_dict['name_ar']
                ordered_dict["count"] = dish_dict['count']
                ordered_dict["avg_score"] = dish_dict['avg_score']
                ordered_dict["min_score"] = dish_dict['min_score']

                nearest = []
                for word_dict in dish_dict["nearest"]:
                    ordered_dict2 = OrderedDict()
                    ordered_dict2["word"] = word_dict.get('word')
                    ordered_dict2["distance"] = word_dict.get('distance')
                    nearest.append(ordered_dict2)

                ordered_dict["nearest"] = NoIndent(nearest)
                ordered_dict["x"] = dish_dict['x']
                ordered_dict["y"] = dish_dict['y']
                ordered_dict_list2.append(ordered_dict)

            restaurant_dict['top5_min'] = ordered_dict_list2


            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(rd_cnt, rdl_length))
                sys.stdout.flush()

            rd_ordered_dict['top5_avg'] = restaurant_dict['top5_avg']
            rd_ordered_dict['top5_min'] = restaurant_dict['top5_min']

            frontend_restaurant_dict_list.append(rd_ordered_dict)


        f1 = open(self.dst_rdl, "w+")
        f1.write(json.dumps(frontend_restaurant_dict_list, indent = 4, cls=NoIndentEncoder))
        f1.close()

        print '\n' + '-'*80
        print "Customizing frontend_sentiment_statistics's json format"

        sw_cnt = 0
        sw_length = len(self.sentiment_statistics)

        ordered_dict_list3 = []

        for word_dict in self.sentiment_statistics:
            sw_cnt += 1

            ordered_dict = OrderedDict()
            ordered_dict['index'] = word_dict['index']
            ordered_dict['word'] = word_dict['word']
            ordered_dict['count'] = word_dict['count']
            ordered_dict['x'] = word_dict['x']
            ordered_dict['y'] = word_dict['y']
            ordered_dict_list3.append(ordered_dict)

            if self.verbose:
                sys.stdout.write("\rStatus: %s / %s"%(sw_cnt, sw_length))
                sys.stdout.flush()

        self.sentiment_words = ordered_dict_list1

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
