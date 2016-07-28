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
import re
from collections import OrderedDict

class MenuCrawler:
    """ This program aims to crawl menus from yelp official website and add to business_list.json, creating business_list_with_menu.json """

    def __init__(self):
        self.scr = 'data/menu/restaurant_1.json'
        self.dst = 'data/business_list_1.json'
        self.maximum = 200

    def get_business_list(self):

        print "Loading data from:", self.scr
        f = open(self.scr)
        business_list = json.load(f)

        return business_list

    def pause(self):
        """ pause the method for a few seconds """
        time.sleep(random.randint(10,20))

    def crawl(self):
        """ crawl data from yelp official website """
        business_list = self.get_business_list()[self.maximum-200:self.maximum]

        menu_list = []
        cnt = 0
        l = len(business_list)
        for business in business_list:

            print '-'*100
            menu = []
            cnt += 1
            if 'menu' in business:
                print "Status:", cnt, "/", l, "| Detecting menu existed in:", business['business_name']
                menu = business['menu']
                continue
            else:
                print "Status:", cnt, "/", l, "| Restaurant:", business['business_name']
                business['business_name'] = unicodedata.normalize('NFKD', business['business_name']).encode('ASCII', 'ignore')
                business['city'] = unicodedata.normalize('NFKD', business['city']).encode('ASCII', 'ignore')
                url = business['business_name'].replace(" ","-") + '-' + business['city'].replace(" ","-")
                url = url.lower().replace("&","and").replace("\'","")
                full_url = "http://www.yelp.com/menu/" + url  # E.g. http://www.yelp.com/menu/mon-ami-gabi-las-vegas

                print "Reaching into:", full_url
                try:
                    connection = urllib.urlopen(full_url).getcode()
                    if connection == 503:
                        print "Error", connection, "(IP Banned)"
                        menu.append("Error_503")
                        menu_list.append(menu)
                        continue
                    elif connection == 404:
                        print "Error:", connection
                        menu.append("Error_404")
                        menu_list.append(menu)
                        self.pause()
                    else:
                        print "Successful:", connection
                        html_data = urllib.urlopen(full_url).read()
                        soup = BeautifulSoup(html_data, "html.parser")

                        print "sub_menus found:",
                        sub_menus = []
                        for li in soup.findAll("li", {"class": "sub-menu"}):
                            sub_menu = li.getText()
                            sub_menu = "".join(sub_menu.split('\n'))
                            sub_menu.replace(" ", "-")
                            sub_menus.append(sub_menu.lower())
                        print sub_menus

                        for sub_menu in sub_menus:
                            extended_url = full_url + "/" + sub_menu
                            print "Crawling data from:", extended_url
                            html_data = urllib.urlopen(extended_url).read()
                            soup = BeautifulSoup(html_data, "html.parser")

                            for div in soup.findAll("div", {"class": "menu-item-details"}):
                                dish = div.find("h4").getText()
                                dish = unicodedata.normalize('NFKD', dish).encode('ASCII', 'ignore')
                                dish = "".join(dish.split('\n'))
                                dish = dish.strip(" ").strip("*")
                                menu.append(dish)

                            self.pause()

                        menu = list(set(menu))
                        menu_list.append(sorted(menu))
                except:
                    self.pause()
                    continue

        return business_list, menu_list

    def get_business_list_with_menu(self):
        """ insert {'menu':[dish1, dish2, ...]} into business_list and render business_list_with_menu """
        business_list, menu_list = self.crawl()
        business_list_with_menu = []
        cnt = 0

        print "-"*100
        print "Inserting menu into business_list"
        length = len(business_list)
        for i in xrange(len(business_list)):
            business_list[i].update({'menu': menu_list[i], 'menu_length': len(menu_list[i])})
            business_list_with_menu.append(business_list[i])

            sys.stdout.write("\rStatus: %s / %s"%(i+1, length))
            sys.stdout.flush()

        return business_list_with_menu

    def render(self):
        """ remove dictionary if (1) no dish is found in menu (2) buffet is found in business_name"""
        """ put keys in order and render json file """

        business_list_with_menu = self.get_business_list_with_menu()

        print "\n" + "-"*100
        print "Writing data to:", self.dst

        cnt = 0
        length = len(business_list_with_menu)
        ordered_dict_list = []
        for business in business_list_with_menu:

            regex_pattern = re.compile('buffet', re.IGNORECASE)

            if not business["menu"]:
                continue
            elif regex_pattern.search(business["business_name"]):
                continue
            else:
                cnt += 1
                ordered_dict = OrderedDict()
                ordered_dict["index"] = business["index"]
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
