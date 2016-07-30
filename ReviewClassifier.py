import json
import os
from collections import OrderedDict

class ReviewClassifier:
    """ This program aims to (1) filter out redundant reviews (2) classify the reviews of the matched restaurants """

    def __init__(self):
        self.src_b = "data/business_list.json"
        self.src_r = "data/review_list.json"

    def get_business_list(self):
        """ return business_id_list """

        print "Loading data from:", self.src_b
        with open(self.src_b) as f:
           business_list = json.load(f)

        return business_list

    def get_review_list(self):
        """ return review_list """

        print "Loading data from:", self.src_r
        with open(self.src_r) as f:
            review_list = json.load(f)

        return review_list

    def create_folder(self):
        """ create directroy if not found """
        directory = os.path.dirname("./data/reviews/")
        if not os.path.exists(directory):   # if the directory does not exist
            os.makedirs(directory)          # create the directory

    def classify(self):
        """ create a json file and dump the content in the review_list that match each business_id """

        self.create_folder()
        review_list = self.get_review_list()
        business_list = self.get_business_list()

        cnt = 0
        length = len(business_list)
        for business in business_list:
            f = open("data/reviews/restaurant_%s.json"%(cnt+1), "w+")

            cnt += 1
            text_list = []
            print "Looking for review that match", business["business_name"], "business_id:",  business["business_id"]
            for review in review_list:
                if business["business_id"] == review["business_id"]:
                   text_list.append(review["text"])

            ordered_dict = OrderedDict()
            ordered_dict["index"] = cnt
            ordered_dict["business_id"] = business["business_id"]
            ordered_dict["business_name"] = business["business_name"]
            ordered_dict["reviews"] = text_list

            f.write(json.dumps(ordered_dict, indent=4))
            f.close()

            sys.stdout.write("\rStatus: %s / %s"%(cnt, length)
            sys.stdout.flush()

            print "Done"

if __name__ == '__main__':
    classifier = ReviewClassifier()
    classifier.classify()

