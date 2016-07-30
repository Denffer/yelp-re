import json
import os
import sys
from collections import OrderedDict
import uuid

class MenuMerger:
    """ This program aims to (1) filter out redundant reviews (2) classify the reviews of the matched restaurants """

    def __init__(self):
        self.src_b = "./data/crawled_menu/"
        self.dst = "./data/business_list.json"

    def get_source(self):
        """ append every crawled business_list into source """

        src_files = []
        source = []
        print "Loading data from:", self.src_b
        for f in os.listdir(self.src_b):
            file_path = os.path.join(self.src_b, f)

            if os.path.isfile(file_path):
                print "Found:", file_path
                with open(file_path) as file:
                   source.append(json.load(file))

        return source

    def get_clean_business_list(self):
        """ (1) get every list in source (2) filter unwanted (3) append to business_list """
        source = self.get_source()

        clean_business_list = []
        cnt1 = 0
        length1 = len(source)
        for s in source:
            cnt1 += 1
            cnt2 = 0
            length2 = len(s)
            for business in s:
                cnt2 += 1
                if len(business["menu"]) < 2:
                    del business
                else:
                    for dish in business["menu"]:
                        dish = dish.strip("\n").strip("\"")
                    clean_business_list.append(business)

                sys.stdout.write("\rStatus: %s / %s | %s / %s"%(cnt1, length1, cnt2, length2))
                sys.stdout.flush()

        #print clean_business_list
        return clean_business_list

    def render(self):
        """ put keys in order and render json file """

        business_list = self.get_clean_business_list()

        print "\n" + "-"*100
        print "Writing data to:", self.dst

        cnt = 0
        length = len(business_list)
        ordered_dict_list = []
        for business in business_list:

            cnt += 1
            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt
            ordered_dict["business_name"] = business["business_name"]
            ordered_dict["city"] = business["city"]
            ordered_dict["stars"] = business["stars"]
            ordered_dict["review_count"] = business["review_count"]
            ordered_dict["business_id"] = business["business_id"]
            ordered_dict["menu_length"] = business["menu_length"]
            ordered_dict["menu"] = NoIndent(business["menu"])

            ordered_dict_list.append(ordered_dict)

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        f = open(self.dst, 'w+')
        f.write( json.dumps( ordered_dict_list, indent = 4, cls=NoIndentEncoder))

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
    merger = MenuMerger()
    merger.render()

