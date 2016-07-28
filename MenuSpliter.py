import json
import os
import sys
from collections import OrderedDict

class MenuSpliter:
    """ This program aims to (1) filter out redundant reviews (2) classify the reviews of the matched restaurants """

    def __init__(self):
        self.src_b = "./data/business_list_no_menu.json"

    def get_business_list(self):
        """ return business_id_list """

        print "Loading data from:", self.src_b
        with open(self.src_b) as f:
           business_list = json.load(f)

        return business_list

    def create_folder(self):
        """ create directroy if not found """
        directory = os.path.dirname("./data/menu/")
        if not os.path.exists(directory):   # if the directory does not exist
            os.makedirs(directory)          # create the directory

    def split(self):
        """ create a json file and dump the content in the review_list that match each business_id """

        self.create_folder()
        business_list = self.get_business_list()

        cnt = 0
        cnt2 = 0
        length = len(business_list)
        small_business_list = []
        for business in business_list:

            cnt += 1
            small_business_list.append(business)

            if cnt % 200 == 0:
                cnt2 += 1
                f = open("./data/menu/restaurant_%s.json"%(cnt2), "w+")
                f.write(json.dumps(small_business_list, indent=4))
                f.close()
                del small_business_list[:]

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length))
            sys.stdout.flush()

        print "\nDone"

if __name__ == '__main__':
    spliter = MenuSpliter()
    spliter.split()

