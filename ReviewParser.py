# -*- coding: utf-8 -*-
import sys, re, json, os, uuid, itertools
from operator import itemgetter
from collections import OrderedDict
import SpellingChecker #self defined

class ReviewParser:
    """ This program aims to transform restaurant_*.json into
        (1) restaurant_*.txt in 'data/backend_reviews'
        (2) restaurant_dict_*.json in 'data/restaurant_dic_list'
        (3) restaurant_1.json in 'data/frontend_reviews'
        (4) count sentiment words in the reviews
    """

    def __init__(self):
        print "Processing", sys.argv[1]
        self.src = sys.argv[1]  # E.g. data/reviews/restaurant_3.json
        self.src_b = 'data/business_list.json'

    def get_review_dict(self):
        #print "Loading data from", self.src
        with open(self.src) as f:
            review_dic = json.load(f)
        return review_dic

    def get_business(self):
        """ match business_id in review_dict with business_list.json """
        review_dic = self.get_review_dict()
        with open(self.src_b) as f:
            business_list = json.load(f)

        for business in business_list:
            if business["business_id"] == review_dic["business_id"]:
                matched_business = business
        return matched_business

    def get_lexicon(self):
        """ return p_list containing dictionaries of positive words """

        positive_list = []
        with open('data/lexicon/lexicon.json') as f:
            lexicon = json.load(f)
            for word_dict in lexicon:
                positive_list.append(word_dict["word"])

        return positive_list

    def get_dishes_regex(self):
        """ dishes_regex is the regular expression for every dish in the dish_list # about to be changed """
        dishes_regex = self.get_business()["menu"]

        for i in xrange(len(dishes_regex)):
            dishes_regex[i] = dishes_regex[i].replace("-","\-").encode('utf-8').lower()
            dishes_regex[i] = re.sub("\&|\.|\(.*\)|[0-9]|([0-9]*-[0-9])+|oz","",dishes_regex[i])

            dishes_regex[i] = dishes_regex[i].split()
            dishes_regex[i][0]= "(" + dishes_regex[i][0] # adding '(' before the first word

            for word in xrange(len(dishes_regex[i])-1):
                dishes_regex[i][word] += "\\s*"

            for word in xrange(len(dishes_regex[i])-2):
                dishes_regex[i][word] += "|"

            dishes_regex[i][len(dishes_regex[i])-2] = dishes_regex[i][len(dishes_regex[i])-2] + ")+"
            dishes_regex[i] = "".join(dishes_regex[i])[:-1]
            dishes_regex[i] += "[a-z]+(s|es|ies)?"

        #print dishes_regex
        return dishes_regex

    def get_dishes_ar(self):
        """ dishes_ar is the dish_list with every dish 'a'ppending 'r'estaurant_name E.g. dish_restaurant """
        dishes_ar = self.get_business()['menu']
        restaurant_name = self.get_business()['business_name']

        for i in xrange(len(dishes_ar)):
            dishes_ar[i] = re.sub("\(.*\)", r'', dishes_ar[i])
            dishes_ar[i] = re.sub("(!|@|#|\$|%|\^|\&|\*\:|\;|\.|\,|\"|\')", r'', dishes_ar[i])
            dishes_ar[i] = dishes_ar[i] + "_" + restaurant_name
            dishes_ar[i] = dishes_ar[i].lower().replace("&", "and").replace(" ", "-").replace("\'", "").replace(".", "")
        return dishes_ar

    def get_marked_dishes(self):
        """ match the dishes in the reviews and mark the dish"""
        dishes = self.get_business()["menu"]
        marked_dishes = []
        for dish in dishes:
            dish = re.sub("\(.*\)", r'', dish)
            dish = re.sub("(!|@|#|\$|%|\^|\&|\*\:|\;|\.|\,|\"|\')", r'', dish)
            dish = dish.lower().replace("&","and").replace("'","").replace(" ","-")
            marked_dishes.append("<mark>" + dish + "</mark>")
        #print marked_dishes
        return marked_dishes

    def get_frontend_reviews(self):

        frontend_reviews = self.get_review_dict()["reviews"]
        dishes_regex = self.get_dishes_regex()
        marked_dishes = self.get_marked_dishes()

        for i in xrange(len(frontend_reviews)):
            #frontend_reviews[i] = ' '.join(frontend_reviews[i].split())
            frontend_reviews[i] = re.sub("\\n+", r" ", frontend_reviews[i])
            """ Replacing | E.g. I love country pate. -> I love <mark>housemade country pate</mark>. """
            for j in xrange(len(marked_dishes)):
                frontend_reviews[i] = re.sub(dishes_regex[j], marked_dishes[j], frontend_reviews[i], flags = re.IGNORECASE)
            frontend_reviews[i] = frontend_reviews[i].replace("-"," ")

        return frontend_reviews

    def get_cleaned_reviews(self):
        """ clean reviews """
        raw_reviews = self.get_review_dict()["reviews"]

        clean_reviews = []
        for text in raw_reviews:
            #text = text.decode("utf-8").encode('ascii', 'ignore')

            text = re.sub(r'https?:\/\/.*[\r\n]*', ' ', text, flags=re.MULTILINE)
            text = ' '.join(re.findall('[A-Z][^A-Z]*', text)) # ThisIsAwesome -> This Is Awesome
            text = re.sub("(!|@|#|\$|%|\^|\&|\*|\(|\)|\:|\;|\.|\,|\?|\")", r' \1 ', text)
            text = re.sub("(\\n)+", r" ", text)
            text = re.sub("(\s)+", r" ", text)

            text = text.lower()

            text = re.sub(r"'m", " am", text)
            text = re.sub(r"'re", " are", text)
            text = re.sub(r"'s", " is", text)
            text = re.sub(r"'ve", " have", text)
            text = re.sub(r"'d", " would", text)
            text = re.sub(r"n't", " not", text)
            text = re.sub(r"'ll", " will", text)

            text = ''.join(''.join(s)[:2] for _, s in itertools.groupby(text)) # sooo happppppy -> so happy
            #text = ' '.join(SpellingChecker.correction(word) for word in text.split())

            clean_reviews.append(text)

        return clean_reviews

    def get_backend_reviews(self):
        """ match the dishes in the reviews with dishes_regex and replace them with the dishes in dishes_ar  """

        backend_reviews = self.get_cleaned_reviews()
        dishes_regex = self.get_dishes_regex()
        dishes_ar = self.get_dishes_ar()

        for i in xrange(len(backend_reviews)):
            """ Replacement | E.g. I love country pate. -> I love housemade-country-pate_mon-ami-gabi. """
            for j in xrange(len(dishes_regex)):
                backend_reviews[i] = re.sub(dishes_regex[j], dishes_ar[j], backend_reviews[i], flags = re.IGNORECASE)

        return backend_reviews

    def get_restaurant_dict(self):
        """ match backend_review_list with dish_ar count the frequnecy of every dish"""

        business = self.get_business()
        backend_reviews = self.get_backend_reviews()
        dishes_ar = self.get_dishes_ar()

        count_list = []
        count = 0
        for dish in dishes_ar:
            for review in backend_reviews:
                count += review.count(dish)
            count_list.append(count)
            count = 0

        menu = []
        """ sorted by count """
        i = 0
        for dish in business["menu"]:
            dish_dict = {"count": count_list[i], "name": dish, "name_ar": dishes_ar[i]}
            i += 1
            menu.append(dish_dict)
        menu = sorted(menu, key=itemgetter('count'), reverse = True)

        index = 0
        new_menu = []
        for dish_dict in menu:
            index += 1
            orderedDict = OrderedDict()
            orderedDict["index"] = index
            orderedDict["count"] = dish_dict["count"]
            orderedDict["name"] = dish_dict["name"]
            orderedDict["name_ar"] = dish_dict["name_ar"]
            orderedDict["x"] = 0
            orderedDict["y"] = 0

            new_menu.append(NoIndent(orderedDict))

        business["menu"] = new_menu
        restaurant_dict = business

        return restaurant_dict

    def get_statistics(self):
        """ count the sentiment word in reviews """
        backend_reviews = self.get_backend_reviews()
        positive_list = self.get_lexicon()

        statistics = []
        index_cnt = 0
        for word in positive_list:
            index_cnt += 1
            count = 0
            for review in backend_reviews:
                count += review.count(" " + word + " ")
            orderedDict = OrderedDict()
            orderedDict["index"] = index_cnt
            orderedDict["word"] = word
            orderedDict["count"] = count
            statistics.append(NoIndent(orderedDict))

        return statistics

    def create_dirs(self):
        """ create the directory if not exist"""
        dir1 = os.path.dirname("data/backend_reviews/")
        dir2 = os.path.dirname("data/frontend_reviews/")
        dir3 = os.path.dirname("data/restaurant_dict_list/")
        dir4 = os.path.dirname("data/sentiment_statistics/")

        if not os.path.exists(dir1):
            os.makedirs(dir1)
        if not os.path.exists(dir2):
            os.makedirs(dir2)
        if not os.path.exists(dir3):
            os.makedirs(dir3)
        if not os.path.exists(dir4):
            os.makedirs(dir4)

    def render(self):
        """ render frontend_review & backend_reviews & restaurant_list """
        business = self.get_business()
        backend_reviews = self.get_backend_reviews()
        frontend_reviews = self.get_frontend_reviews()
        restaurant_dict = self.get_restaurant_dict()
        sentiment_statistics = self.get_statistics()

        self.create_dirs()
        filename = sys.argv[1][24]
        if sys.argv[1][25] != ".":
            filename = filename + sys.argv[1][25]
            if sys.argv[1][26] != ".":
                filename = filename + sys.argv[1][26]

        review_count = len(frontend_reviews)
        """ (1) render restaurant_*.json in ./frontend_reviews """

        orderedDict1 = OrderedDict()
        orderedDict1["restaurant_name"] = business["business_name"]
        orderedDict1["restaurant_id"] = business["business_id"]
        orderedDict1["stars"] = business["stars"]
        orderedDict1["review_count"] = review_count
        orderedDict1["reviews"] = frontend_reviews

        frontend_json = open("data/frontend_reviews/restaurant_%s.json"%(filename), "w+")
        frontend_json.write(json.dumps(orderedDict1, indent = 4))
        frontend_json.close()

        print sys.argv[1], "'s frontend json is completed"

        """ (2) render restaurant_*.json in ./backend_reviews """
        backend_txt = open("data/backend_reviews/restaurant_%s.txt"%(filename), "w+")
        for review in backend_reviews:
            backend_txt.write(review.encode("utf-8") + '\n')
        backend_txt.close()

        print sys.argv[1], "'s backend json is completed"

        """ (3) render restaurant_dict, in which menu is transformded from a list to a detailed dictionary """

        orderedDict2 = OrderedDict()
        orderedDict2["restaurant_name"] = restaurant_dict["business_name"]
        orderedDict2["restaurant_id"] = restaurant_dict["business_id"]
        orderedDict2["stars"] = restaurant_dict["stars"]
        orderedDict2["review_count"] = review_count
        orderedDict2["menu_length"] = restaurant_dict["menu_length"]
        orderedDict2["menu"] = restaurant_dict["menu"]

        #dish_list = sorted(dish_list, key=lambda k: k['count'])

        restaurant_json = open("data/restaurant_dict_list/restaurant_dict_%s.json"%(filename), "w+")
        restaurant_json.write(json.dumps( orderedDict2, indent = 4, cls=NoIndentEncoder))
        restaurant_json.close()

        print sys.argv[1], "'s restaurant_dic json is completed"

        """ (4) render restaurant.json containing dictionaries of each positive sentiment word """

        restaurant_json = open("data/sentiment_statistics/restaurant_%s.json"%(filename), "w+")
        restaurant_json.write(json.dumps(sentiment_statistics, indent = 4, cls=NoIndentEncoder))
        restaurant_json.close()

        print sys.argv[1], "'s sentiment analysis is completed"

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

if  __name__ == '__main__':
    parser = ReviewParser()
    parser.render()
