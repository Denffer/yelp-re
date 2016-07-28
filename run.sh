mkdir data
find -name 'ex50' -exec rm -r {} \;
scp cychao@clip2.cs.nccu.edu.tw:/tmp2/cychao/yelp/data/business_list_no_menu.json ./data/
python MenuSpliter.py
sudo pip install beautifulsoup4
