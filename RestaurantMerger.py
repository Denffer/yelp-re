import json, os, sys, uuid
from collections import OrderedDict
import numpy as np
from operator import itemgetter

class RestaurantMerger:
    """ This program aims to
        (1) Merge data/backend_reviews/restaurant_1~523.txt into backend_reviews.txt
        (2) Merge data/restaurant_dict_list/restaurant_dict_1~523.json into restaurant_dict_list.json
        (3) Merge data/sentiment_statistics/restaurant_1~523.json into sentiment_statistics.json  """

    def __init__(self):
        self.src_rdl = "data/restaurant_dict_list/"
        self.src_ss = "data/sentiment_statistics/"

        self.dst_w2v_rdl = "data/coreProcess_word2vec/restaurant_dict_list.json"
        self.dst_w2v_ss = "data/coreProcess_word2vec/sentiment_statistics.json"
        self.dst_glove_rdl = "data/coreProcess_glove/restaurant_dict_list.json"
        self.dst_glove_ss = "data/coreProcess_glove/sentiment_statistics.json"

        self.switch = 1

    def get_restaurant_dict_list(self):
        """ open and append every restaurnat_dict in data/restaurant_dict_list """

        src_files = []
        restaurant_dict_list = []

        print "Loading data from:", self.src_rdl

        cnt = 0
        length = len(os.listdir(self.src_rdl))

        for f in os.listdir(self.src_rdl):

            cnt += 1
            file_path = os.path.join(self.src_rdl, "restaurant_dict_")
            file_path = file_path + str(cnt) + ".json"

            if os.path.isfile(file_path):
                #print "Found:", file_path
                with open(file_path) as file:
                    restaurant_dict_list.append(json.load(file))

                if self.switch:
                    sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                    sys.stdout.flush()

        #print restaurant_dict_list
        return restaurant_dict_list

    def get_sentiment_statistics(self):
        """ open and append every sentiment_staticstic(dictionary) in data/sentiment_statistics """

        src_files = []
        sentiment_statistics = []

        print '\n' + '-'*70
        print "Loading data from:", self.src_ss

        cnt = 0
        length = len(os.listdir(self.src_ss))

        for f in os.listdir(self.src_ss):

            file_path = os.path.join(self.src_ss, f)
            if os.path.isfile(file_path):
                cnt += 1
                #print "Found:", file_path
                with open(file_path) as file:
                   sentiment_statistics.append(json.load(file))

                if self.switch:
                    sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                    sys.stdout.flush()

        #print sentiment_statistics
        return sentiment_statistics

    def get_customized_restaurant_dict_list(self):
        """ take every list or dictionary and customize as how it should be originally """

        restaurant_dict_list = self.get_restaurant_dict_list()
        print '\n' + '-'*70
        print "Customizing the json format for restaurnat_dict_list"

        cnt1 = 0
        length1 = len(restaurant_dict_list)
        for restaurant_dict in restaurant_dict_list:
            cnt1 += 1
            dish_dict_list = []

            for dish_dict in restaurant_dict['menu']:
                dish_dict_list.append(NoIndent(dish_dict))

            restaurant_dict['menu'] = dish_dict_list

            sys.stdout.write("\rStatus: %s / %s"%(cnt1, length1))
            sys.stdout.flush()

        return restaurant_dict_list

    def get_customized_sentiment_statistics(self):
        """ take every list or dictionary and customize as how it should be originally """

        sentiment_statistics = self.get_sentiment_statistics()
        print '\n' + '-'*70
        print "Customizing the json format for sentiment_statistics"

        print "Merging every word and its counts"
        cnt1 = 0
        length1 = len(sentiment_statistics)

        word_list = []
        count_list = np.zeros(len(sentiment_statistics[0]))
        for statistic in sentiment_statistics:
            tmp_word_list = []
            cnt1 += 1

            for i in xrange(len(statistic)):
                tmp_word_list.append(statistic[i]['word'])
                count_list[i] += (np.asarray(statistic[i]['count']))

            word_list = tmp_word_list

            sys.stdout.write("\rStatus: %s / %s"%(cnt1, length1))
            sys.stdout.flush()

        print "\n" + "Sorting it by count"
        cnt2 = 0
        length2 = len(word_list)
        word_dict_list = []
        for i in xrange(len(word_list)):

            cnt2 += 1
            word_dict = {"word": word_list[i], "count": int(count_list[i])}
            word_dict_list.append(word_dict)

            sys.stdout.write("\rStatus: %s / %s"%(cnt2, length2))
            sys.stdout.flush()

        sentiment_statistics = sorted(word_dict_list, key=itemgetter('count'), reverse = True)

        return sentiment_statistics

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname("data/coreProcess_word2vec/")
        dir2 = os.path.dirname("data/coreProcess_glove/")

        if not os.path.exists(dir1):
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            os.makedirs(dir2)

    def render(self):
        """ put keys in order and render json file """

        restaurant_dict_list = self.get_customized_restaurant_dict_list()
        sentiment_statistics = self.get_customized_sentiment_statistics()

        self.create_dirs()

        print "\n" + "-"*70
        print "Writing data to:", self.dst_w2v_rdl, "and", self.dst_glove_rdl

        cnt1 = 0
        length1 = len(restaurant_dict_list)
        ordered_restaurant_dict_list = []
        for restaurant_dict in restaurant_dict_list:

            cnt1 += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt1
            ordered_dict["restaurant_name"] = restaurant_dict["restaurant_name"]
            ordered_dict["restaurant_id"] = restaurant_dict["restaurant_id"]
            ordered_dict["stars"] = restaurant_dict["stars"]
            ordered_dict["review_count"] = restaurant_dict["review_count"]
            ordered_dict["menu_length"] = restaurant_dict["menu_length"]
            ordered_dict["menu"] = restaurant_dict["menu"]

            ordered_restaurant_dict_list.append(ordered_dict)

            sys.stdout.write("\rStatus: %s / %s"%(cnt1, length1))
            sys.stdout.flush()

        f1 = open(self.dst_w2v_rdl, 'w+')
        f1.write( json.dumps( ordered_restaurant_dict_list, indent = 4, cls=NoIndentEncoder))
        f2 = open(self.dst_glove_rdl, 'w+')
        f2.write( json.dumps( ordered_restaurant_dict_list, indent = 4, cls=NoIndentEncoder))

        print "\n" + "-"*70
        print "Writing data to:", self.dst_w2v_ss, "and", self.dst_glove_ss

        cnt2 = 0
        length2 = len(sentiment_statistics)
        ordered_word_dict_list = []
        for word_dict in sentiment_statistics:
            cnt2 += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt2
            ordered_dict["word"] = word_dict["word"]
            ordered_dict["count"] = word_dict["count"]
            ordered_word_dict_list.append(NoIndent(ordered_dict))

            sys.stdout.write("\rStatus: %s / %s"%(cnt2, length2))
            sys.stdout.flush()

        f3 = open(self.dst_w2v_ss, 'w+')
        f3.write( json.dumps( ordered_word_dict_list, indent = 4, cls=NoIndentEncoder))
        f3 = open(self.dst_glove_ss, 'w+')
        f3.write( json.dumps( ordered_word_dict_list, indent = 4, cls=NoIndentEncoder))

        print "\n" + "-"*70
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
    merger = RestaurantMerger()
    merger.render()

