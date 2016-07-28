mkdir data
find -name 'ex50' -exec rm -r {} \;
find -name 'README.md' -exec rm {} \;
sudo pip install beautifulsoup4
scp cychao@clip2.cs.nccu.edu.tw:/tmp2/cychao/yelp/data/business_list_no_menu.json ./data/
