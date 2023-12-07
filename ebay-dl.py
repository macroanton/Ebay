import argparse
import requests
from bs4 import BeautifulSoup
import json

def parse_price(text):
    '''
    Takes input as a string and returns the price of items, in cents

    >>> parse_price('$15.95')
    $1595
    >>> parse_price('$24.36 to $141.04')
    $2436 to $14104
    >>> parse_price('+$10.35 shipping')
    +$1035 shipping
    '''
    num = ''
    if '$' not in text:
        return 0
    elif ' to ' in text:
        list = text.split()
        text = list[0]
    for char in text:
        if char in '1234567890':
            num += char
    return int(num)








def parse_itemssold(s):
    '''
    Takes as input a string and returns the number of items sold, as specified in the string

    >>> parse_itemssold('38 sold')
    38
    >>> parse_itemssold('14 watchers')
    0
    >>> parse_itemssold('Almost Gone')
    0
    '''
    numbers = ''
    for char in s:
        if char in '1234567890':
            numbers += char
    if 'sold' in s:
        return int(numbers)
    else:
        return 0


#This if statement says only run code below when python runs "normally"
#where normally is not in doctests


#get command line arguements
parser = argparse.ArgumentParser(description='Download infromation from ebay and convert to JSON')
parser.add_argument('search_term')
parser.add_argument('--num-pages', default=10)
args = parser.parse_args()

print('args.search_term=', args.search_term)

# List of all items found in all ebay webpages
items = []

# Loop over the ebay webpages
for page_number in range(1,int(args.num_pages)+1):
    #build url
    url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=' 
    url += args.search_term 
    url += '&_sacat=0&_pgn='
    url += str(page_number)
    url += '&rt=nc'
    
    print('url=', url)
    
    #download HTML
    r = requests.get(url)
    status = r.status_code
    print('status=', status)

    html = r.text


    # process the html
    soup = BeautifulSoup(html, 'html.parser') 
    
    #loop over the items in the page
    tags_items = soup.select('.s-item')
    for tag_item in tags_items:
        
        name = None
        tags_name = tag_item.select('.s-item__title')
        for tag in tags_name:
            name = tag.text

        condition = None
        tags_condition = tag_item.select('.s-item__subtitle')
        for tag in tags_condition:
            condition = tag.text

        shipping = None
        tags_shipping = tag_item.select('.s-item__shipping.s-item__logisticsCost')
        for tag in tags_shipping:
            shipping = parse_price(tag.text)
            

        freereturns = False
        tags_freereturns = tag_item.select(' .s-item__free-returns')
        for tag in tags_freereturns:
            freereturns = True
        
        items_sold = None
        tags_itemssold = tag_item.select('.s-item__hotness')
        for tag in tags_itemssold:
            items_sold = parse_itemssold(tag.text)

        Price = None
        tags_itemprices = tag_item.select('.s-item__price')
        for tag in tags_itemprices:
            Price = parse_price(tag.text)
        



        item = {
            'name': name,
            'free_returns': freereturns,
            'items_sold': items_sold,
            'condition': condition,
            'shipping': shipping,
            'price' : Price
        }
        items.append(item)
    
    print('len(tags_item)=', len(tags_items))

# write the json to a file
filename = args.search_term +'.json'
with open(filename, 'w', encoding='ascii') as f:
    f.write(json.dumps(items))
