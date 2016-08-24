# -*- coding: utf-8 -*-
import sys, re, json, os, uuid, itertools
from operator import itemgetter
from collections import OrderedDict
import SpellingChecker #self defined
import unicodedata

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

        self.backend_reviews = []
        self.frontend_reviews = []
        #self.menu = []
        self.switch = 0

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

        #print positive_list
        return positive_list

    def get_clean_menu(self):
        """ get menu from business_list and return a clean menu"""
        menu = self.get_business()["menu"]
        clean_menu = []

        for dish in menu:
            dish = re.sub("\(.*\)", "", dish)
            dish = dish.replace("(","").replace(")","")
            dish = dish.replace("&", "and").replace("\'", "").replace("*","").replace("-"," ")
            dish = re.sub("(\s)+", " ", dish)
            dish = dish.strip()
            dish = re.sub("(!|@|#|\$|%|\^|\*\:|\;|\.|\,|\"|\'|\\|\/)", r'', dish)

            clean_menu.append(dish)

        #print clean_menu
        return clean_menu

    def get_dishes_regex(self):
        """ dishes_regex is the regular expression for every dish in the dish_list # about to be changed """
        dishes_regex = self.get_clean_menu()

        for i in xrange(len(dishes_regex)):
            #dishes_regex[i] = dishes_regex[i].replace("-","\-").encode('utf-8').lower()

            dishes_regex[i] = dishes_regex[i].lower()
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
        #dishes_ar = self.get_business()['menu']
        dishes_ar = self.get_clean_menu()
        restaurant_name = self.get_business()['business_name']

        for i in xrange(len(dishes_ar)):
            dishes_ar[i] = dishes_ar[i] + "_" + restaurant_name
            dishes_ar[i] = re.sub("(\s)+", r" ", dishes_ar[i])
            dishes_ar[i] = dishes_ar[i].lower().replace("&", "and").replace(" ", "-").replace("\'", "").replace(".", "").replace(",","")

        #print dishes_ar
        return dishes_ar

    def get_marked_dishes(self):
        """ match the dishes in the reviews and mark the dish"""
        menu = self.get_clean_menu()
        #dishes = self.get_business()["menu"]
        marked_dishes = []

        if self.switch:
            print "\n" + "-"*70
            print "Marking dishes"

        cnt = 0
        length = len(menu)
        for dish in menu:
            cnt += 1
            #dish = re.sub("(!|@|#|\$|%|\^|\&|\*\:|\;|\.|\,|\"|\')", r'', dish)
            dish = dish.lower().replace("&","and").replace("'","").replace(" ","-")
            marked_dishes.append("<mark>" + dish + "</mark>")

            if self.switch:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        #print marked_dishes
        return marked_dishes

    def get_frontend_reviews(self):

        frontend_reviews = self.get_review_dict()["reviews"]
        dishes_regex = self.get_dishes_regex()
        marked_dishes = self.get_marked_dishes()

        if self.switch:
            print "\n" + "-"*70
            print "Processing frontend reviews"

        length1 = len(frontend_reviews)
        for i in xrange(len(frontend_reviews)):
            frontend_reviews[i] = re.sub("\\n+", r" ", frontend_reviews[i])
            length2 = len(marked_dishes)

            for j in xrange(len(marked_dishes)):
                """ Replacing | E.g. I love country pate. -> I love <mark>housemade country pate</mark>. """
                frontend_reviews[i] = re.sub(dishes_regex[j], marked_dishes[j], frontend_reviews[i], flags = re.IGNORECASE)

                if self.switch:
                    sys.stdout.write("\rStatus: %s / %s | %s / %s"%(i+1, length1, j+1, length2))
                    sys.stdout.flush()

            frontend_reviews[i] = frontend_reviews[i].replace("-"," ")

        return frontend_reviews

    def get_cleaned_reviews(self):
        """ clean reviews """
        raw_reviews = self.get_review_dict()["reviews"]

        if self.switch:
            print "Cleaning reviews"

        cnt = 0
        length = len(raw_reviews)
        clean_reviews = []
        for text in raw_reviews:
            cnt += 1
            #text = text.decode("utf-8").encode('ascii', 'ignore')

            text = text.lower()
            text = re.sub(r'https?:\/\/.*[\r\n]*', ' ', text, flags=re.MULTILINE)
            #text = ' '.join(re.findall('[A-Z][^A-Z]*', text)) # ThisIsAwesome -> This Is Awesome
            text = text.replace("!"," ! ").replace("@"," @ ").replace("#"," # ").replace("$"," $ ").replace("%"," % ")
            text = text.replace("^"," ^ ").replace("&"," & ").replace("*"," * ").replace("("," ( ").replace(")"," ) ")
            text = text.replace(":"," : ").replace(";"," ; ").replace("."," . ").replace(","," , ").replace("=", " = ")
            text = text.replace("+"," + ").replace("-"," - ").replace("|"," | ").replace("\\"," \ ").replace("/"," / ")
            text = text.replace("\""," ").replace("?", " ? ").replace("["," ").replace("]"," ").replace("{", " { ").replace("}", " } ")

            #text = re.sub("(!|@|#|\$|%|\^|\&|\*|\(|\)|\:|\;|\.|\,|\?|\")", r' \1 ', text)

            text = re.sub(r"'m", " am", text)
            text = re.sub(r"'re", " are", text)
            text = re.sub(r"'s", " is", text)
            text = re.sub(r"'ve", " have", text)
            text = re.sub(r"'d", " would", text)
            text = re.sub(r"n't", " not", text)
            text = re.sub(r"'ll", " will", text)

            text = text.replace("\'"," ")

            #FIXME Remove accents
            text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')

            #FIXME porterStemmer # but may lose information

            text = re.sub("(\\n)+", r" ", text)
            text = re.sub("(\s)+", r" ", text)

            text = ''.join(''.join(s)[:2] for _, s in itertools.groupby(text)) # sooo happppppy -> so happy
            #text = ' '.join(SpellingChecker.correction(word) for word in text.split())
            clean_reviews.append(text)

            if self.switch:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        return clean_reviews

    def get_backend_reviews(self):
        """ match the dishes in the reviews with dishes_regex and replace them with the dishes in dishes_ar  """

        backend_reviews = self.get_cleaned_reviews()
        dishes_regex = self.get_dishes_regex()
        dishes_ar = self.get_dishes_ar()

        if self.switch:
            print "\n" + "-"*70
            print "Processing backend_reviews"

        length1 = len(backend_reviews)
        for i in xrange(len(backend_reviews)):
            length2 = len(dishes_regex)
            for j in xrange(len(dishes_regex)):
                """ Replacement | E.g. I love country pate. -> I love housemade-country-pate_mon-ami-gabi. """
                backend_reviews[i] = re.sub(dishes_regex[j], dishes_ar[j], backend_reviews[i], flags = re.IGNORECASE)

                if self.switch:
                    sys.stdout.write("\rStatus: %s / %s | %s / %s"%(i+1, length1, j+1, length2))
                    sys.stdout.flush()

        return backend_reviews

    def get_restaurant_dict(self):
        """ match backend_review_list with dish_ar count the frequnecy of every dish"""

        business = self.get_business()
        #backend_reviews = self.get_backend_reviews()
        dishes_ar = self.get_dishes_ar()

        if self.switch:
            print "\n" + "-"*70
            print "Processing restaurant_dict"

        count_list = []
        count = 0
        """ counting the frequencies of dish in reviews"""
        cnt = 0
        length = len(dishes_ar)
        for dish in dishes_ar:
            cnt += 1
            for review in self.backend_reviews:
                count += review.count(dish)
            count_list.append(count)
            count = 0

            if self.switch:
                sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
                sys.stdout.flush()

        menu = self.get_clean_menu()
        """ sorted by count """
        i = 0
        dish_dict_list = []
        for i in xrange(len(menu)):
            dish_dict = {"count": count_list[i], "name": menu[i], "name_ar": dishes_ar[i]}
            i += 1
            dish_dict_list.append(dish_dict)
        dish_dict_list = sorted(dish_dict_list, key=itemgetter('count'), reverse = True)

        index = 0
        processed_menu = []
        for dish_dict in dish_dict_list:
            index += 1
            orderedDict = OrderedDict()
            orderedDict["index"] = index
            orderedDict["count"] = dish_dict["count"]
            orderedDict["name"] = dish_dict["name"]
            orderedDict["name_ar"] = dish_dict["name_ar"]
            orderedDict["x"] = 0
            orderedDict["y"] = 0

            processed_menu.append(NoIndent(orderedDict))

        business["menu"] = processed_menu
        restaurant_dict = business

        return restaurant_dict

    def get_statistics(self):
        """ count the sentiment word in reviews """
        #backend_reviews = self.get_backend_reviews()
        positive_list = self.get_lexicon()

        if self.switch:
            print "\n" + "-"*70
            print "Processing statistics"

        statistics = []
        index_cnt = 0
        length = len(positive_list)

        for word in positive_list:
            index_cnt += 1
            dish_count = 0
            for review in self.backend_reviews:
                dish_count += review.count(" " + word + " ")
            orderedDict = OrderedDict()
            orderedDict["index"] = index_cnt
            orderedDict["word"] = word
            orderedDict["count"] = dish_count
            statistics.append(NoIndent(orderedDict))

            if self.switch:
                sys.stdout.write("\rStatus: %s / %s"%(index_cnt, length))
                sys.stdout.flush()

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
        #self.menu = self.get_clean_menu()
        self.backend_reviews = self.get_backend_reviews()
        self.frontend_reviews = self.get_frontend_reviews()
        restaurant_dict = self.get_restaurant_dict()
        sentiment_statistics = self.get_statistics()

        self.create_dirs()

        if self.switch:
            print "\n" + "-"*70
            print "Rendering"

        filename = sys.argv[1][24]
        if sys.argv[1][25] != ".":
            filename = filename + sys.argv[1][25]
            if sys.argv[1][26] != ".":
                filename = filename + sys.argv[1][26]

        review_count = len(self.frontend_reviews)
        """ (1) render restaurant_*.json in ./frontend_reviews """

        orderedDict1 = OrderedDict()
        orderedDict1["restaurant_name"] = business["business_name"]
        orderedDict1["restaurant_id"] = business["business_id"]
        orderedDict1["stars"] = business["stars"]
        orderedDict1["review_count"] = review_count
        orderedDict1["reviews"] = self.frontend_reviews

        frontend_json = open("data/frontend_reviews/restaurant_%s.json"%(filename), "w+")
        frontend_json.write(json.dumps( orderedDict1, indent = 4))
        frontend_json.close()

        print sys.argv[1], "'s frontend json is completed"

        """ (2) render restaurant_*.json in ./backend_reviews """
        backend_txt = open("data/backend_reviews/restaurant_%s.txt"%(filename), "w+")
        for review in self.backend_reviews:
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
