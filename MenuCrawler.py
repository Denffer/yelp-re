# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
import urllib
import unicodedata
import json
import pprint
import time
import random
import sys
import uuid

class MenuCrawler:
    """ This program aims to crawl menus from yelp official website and add to business_list.json, creating business_list_with_menu.json """

    def __init__(self):
        self.scr = 'data/business_list1.json'
        self.dst = 'data/business_list_with_menu.json'
        self.maximum = 6

    def get_business_list(self):

        print "Loading data from:", self.scr
        f = open(self.scr)
        business_list = json.load(f)

        return business_list

    def pause(self):
        """ pause the method for a few seconds """
        time.sleep(random.randint(4,8))

    def crawl(self):
        """ crawl data from yelp official website """
        business_list = self.get_business_list()[:self.maximum]

        menu_list = []
        cnt = 0
        l = len(business_list)
        for business in business_list:

            cnt += 1
            print "Crawling data from:", business['business_name'], "| Status:", cnt, "/", l

            business['business_name'] = unicodedata.normalize('NFKD', business['business_name']).encode('ASCII', 'ignore')
            business['city'] = unicodedata.normalize('NFKD', business['city']).encode('ASCII', 'ignore')
            url = business['business_name'].replace(" ","-") + '-' + business['city'].replace(" ","-")
            url = url.lower().replace("&","and").replace("\'","")

            try:
                html_data = urllib.urlopen("http://www.yelp.com/menu/" + url).read()
                soup = BeautifulSoup(html_data, "html.parser")

                menu = []
                for div in soup.findAll("div", {"class": "menu-item-details"}):
                    dish = div.find("h4").getText()
                    dish = unicodedata.normalize('NFKD', dish).encode('ASCII', 'ignore')
                    dish = "".join(dish.split('\n'))
                    dish = dish.strip(" ").strip("*")
                    menu.append(dish)

                menu_list.append(menu)

            except:
                print("Unable to crawl menu from:"), business['business_name']
                menu_list.append('no dish')

            self.pause()

        return business_list, menu_list

    def get_business_list_with_menu(self):
        """ insert menu into business_list """
        business_list, menu_list = self.crawl()
        business_list_with_menu = []
        cnt = 0

        print "Inserting menu into business_list"
        length = len(business_list)
        for i in xrange(len(business_list)):
            business_list[i].update({'menu': NoIndent(menu_list[i])})
            business_list_with_menu.append(business_list[i])

            sys.stdout.write("\rStatus: %s / %s"%(i+1, length))
            sys.stdout.flush()

        return business_list_with_menu

    def render(self):
        """ append menu into business_list and render business_list_with_menu """

        business_list_with_menu = self.get_business_list_with_menu()

        print "\nWriting data to:", self.dst
        f = open('data/business_list_with_menu.json', 'w+')
        f.write( json.dumps( business_list_with_menu, indent = 4, cls=NoIndentEncoder))

        print "Done"
        #pprint.pprint(menu_list)

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
    menu_crawler = MenuCrawler()
    menu_crawler.render()
