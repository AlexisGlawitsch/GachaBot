import json
from urllib.request import urlopen

def get_cards():
    return json.load(urlopen('http://schoolido.lu/api/cards/'))

cardlist = get_cards()
# cardlist.get('results')[page_size] = cardlist.get('count')
for x in cardlist.get('results'):
    print(x)

for x in cardlist.get('results'):
    print(x.get('idol').get('name'))

idlist = json.load(urlopen('http://schoolido.lu/api/cardids/'))
print(idlist)
