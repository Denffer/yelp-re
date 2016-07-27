import os
import json
import sys
import pprint
from operator import itemgetter

class Preprocess:
    """ This program takes all json files in ./raw_data and filter out top 2000 restaurants with the most reviews. """

    def __init__(self):

        self.src_b = 'data/raw_data/yelp_academic_dataset_business.json'
        self.src_r = 'data/raw_data/yelp_academic_dataset_review.json'
        self.src_t = 'data/raw_data/yelp_academic_dataset_tip.json'
        self.dst = 'data/'

    def get_business_list(self):
        """ filter 'business_id' and 'name' out of a long chunk of unwanted information """

        print "Filtering data from", self.src_b
        f = open(self.src_b)
        business_list = []

        cnt = 0
        for line in f:
            cnt += 1
            raw_dict = json.loads(line)
            business_dict = {"business_id": raw_dict["business_id"], "business_name": raw_dict["name"], "stars": raw_dict["stars"], "city": raw_dict["city"], "review_count": raw_dict["review_count"]}
            business_list.append(business_dict)

            sys.stdout.write("\rStatus: %s"%(cnt))
            sys.stdout.flush()

        print ""
        #pprint.pprint(business_list)
        return business_list

    def get_review_list(self):
        """ filter 'business_id' & 'review_stars' & 'text' out of a long chunk of unwanted information """

        print "Filtering data from", self.src_r
        f = open(self.src_r)
        review_list = []

        cnt = 0
        for line in f:
            cnt += 1
            raw_dict = json.loads(line)
            review_dict = {"business_id": raw_dict["business_id"], "review_stars": raw_dict["stars"], "text": raw_dict["text"]}
            review_list.append(review_dict)

            sys.stdout.write("\rStatus: %s" %(cnt))
            sys.stdout.flush()

        print ""
        #pprint.pprint(review_list)
        return review_list

    def get_tip_list(self):
        """ filter 'business_id' & 'text' from tip.json """

        print "Filtering data from", self.src_t
        f = open(self.src_t)
        tip_list = []

        cnt = 0
        for line in f:
            cnt += 1
            raw_dict = json.loads(line)
            tip_dict = {"text": raw_dict["text"], "business_id": raw_dict["business_id"]}
            tip_list.append(tip_dict)

            sys.stdout.write("\rStatus: %s" %(cnt))
            sys.stdout.flush()

        print ""
        #pprint.pprint(tip_list)
        return tip_list

    def get_extended_review_list(self):
        """ matching restaurant_id in tip_list with the restaurant_id in review_list """
        """ reviewfy tips in tip_list and append into review_list """

        business_list = self.get_business_list()
        tip_list = self.get_tip_list()
        review_list = self.get_review_list()

        print "Updating stars into tip_list"
        cnt = 0
        for tip in tip_list:
            cnt += 1
            # initializing review_stars in tip
            tip.update({"review_stars":0})
            for business in business_list:
                if business["business_id"] == tip["business_id"]:
                    tip.update({"review_stars": business["stars"]})

            sys.stdout.write("\rStatus: %s"%(cnt))
            sys.stdout.flush()

        print "\nExtending tip_list into review_list"

        review_list.extend(tip_list)
        #pprint.pprint(review_list)

        return review_list, business_list

    def add_business_count(self, business_list):
        """ add business_count to every business dictionary """

        cnt = 0
        for business in business_list:
            cnt += 1
            business.update({"business_count": cnt})

        return business_list

    def add_review_count(self, review_list):
        """ add review_count to every review dictionary """

        cnt = 0
        for review in review_list:
            cnt += 1
            review.update({"review_count": cnt})

        return review_list

    def render(self):
        review_list, business_list = self.get_extended_review_list()

        print "Writing business_list.json"
        business_list = sorted( sorted(business_list, key=itemgetter('business_name')), key=itemgetter('review_count'), reverse=True)
        business_list = self.add_business_count(business_list)
        f = open('data/business_list.json', 'w+')
        f.write(json.dumps(business_list, indent = 4))

        print "Writing review_list.json"
        review_list = sorted( sorted(review_list, key=itemgetter('business_id')), key=itemgetter('review_stars'), reverse=True)[:2000]
        review_list = self.add_review_count(review_list)
        f = open('data/review_list.json', 'w+')
        f.write(json.dumps(review_list, indent = 4))

        print "Done"

if __name__ == '__main__':
    preprocess = Preprocess()
    preprocess.render()

