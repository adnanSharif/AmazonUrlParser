from lxml import html
# from bs4 import BeautifulSoup as bs 
import csv
import os
import json
from furl import furl
import requests
import random
from time import sleep


userAgent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36', 
    'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.107 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36 OPR/32.0.1948.25',
    'Opera/9.80 (Linux armv6l ; U; CE-HTML/1.0 NETTV/3.0.1;; en) Presto/2.6.33 Version/10.60'
]

def AmzonParser(url, ASIN):
    global userAgent
    headers = {
        'User-Agent': userAgent[random.randint(0,len(userAgent)-1)]}
    page = requests.get(url, headers=headers, timeout=5)
    for i in range(0, 5):  #try few times
        sleep(2)
        try:
            print('status code', page.status_code)

            doc = html.fromstring(page.content)
            XPATH_TITLE = '//*[@id="title"]//text()'
            XPATH_BRAND = '//*[@id="bylineInfo"]//text()'
            XPATH_FEATURE = '//*[@id="feature-bullets"]/ul/li/span/text()'
            XPATH_DESCRIPTION = '//*[@id="productDescription"]/p/text()'
            XPATH_DIMENTION = '''
            //*[contains(text(),"Product Dimensions")]/following-sibling::*/text()
            |
            //*[contains(text(),"Product Dimensions")]/following-sibling::text()
            '''
            XPATH_WEIGHT = '''
            //*[contains(text(),"Shipping Weight")]/following-sibling::*/text()
            |
            //*[contains(text(),"Shipping Weight")]/following-sibling::text()
            '''
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            XPATH_ORIGINAL_PRICE = '//span[ contains(@id, "listPriceLegalMessage")]/preceding-sibling::*/text()'
            
            XPATH_IMAGES = '//input[@class="a-button-input"]/following-sibling::span[@class="a-button-text"]/img[contains(@src, ".jpg")]/@src'
            XPATH_CATEGORIES = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            XPATH_NODES = '//a[@class="a-link-normal a-color-tertiary"]/@href'
            XPATH_RATING = '//*[@data-hook="rating-out-of-text"]/text()'
            XPATH_SIMILAR = '//a[contains(@href, "/dp/") or contains(@href, "url=") ]/@href' 
            XPATH_ATTRIBUTE_NAME = '//form[@id="twister"]/div/div/label[@class="a-form-label"]/text()'
            XPATH_ATTRIBUTE_VALUE = '''
            //form[@id="twister"]/div/div/span[@class="selection"]/text()
            |
            //*[@class="a-dropdown-prompt"]/text()
            '''

            RAW_TITLE = doc.xpath(XPATH_TITLE)
            RAW_BRAND = doc.xpath(XPATH_BRAND)
            RAW_FEATURE = doc.xpath(XPATH_FEATURE)
            RAW_DESCRIPTION = doc.xpath(XPATH_DESCRIPTION)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_NODES = doc.xpath(XPATH_NODES)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            RAW_DIMENTION = doc.xpath(XPATH_DIMENTION)
            RAW_WEIGHT = doc.xpath(XPATH_WEIGHT)
            RAW_IMAGES = doc.xpath(XPATH_IMAGES)
            RAW_CATEGORIES = doc.xpath(XPATH_CATEGORIES)
            RAW_RATING = doc.xpath(XPATH_RATING)
            RAW_SIMILAR = doc.xpath(XPATH_SIMILAR)
            RAW_ATTRIBUTE_NAME = doc.xpath(XPATH_ATTRIBUTE_NAME)
            RAW_ATTRIBUTE_VALUE = doc.xpath(XPATH_ATTRIBUTE_VALUE)
            print('raw attribute name', RAW_ATTRIBUTE_NAME)
            print('raw attribute value', RAW_ATTRIBUTE_VALUE)

            TITLE = ' '.join(''.join(RAW_TITLE).split()) if RAW_TITLE else None
            BRAND = ' '.join(''.join(RAW_BRAND).split()) if RAW_BRAND else None
            FEATURE = list(filter(None, [i.strip() for i in RAW_FEATURE])) if RAW_FEATURE else None
            DESCRIPTION = ' '.join(''.join(RAW_DESCRIPTION).split()) if RAW_DESCRIPTION else None
            PRIME = True
            print('dimention', RAW_DIMENTION)
            IMAGES = list(filter(None, [i.strip() for i in RAW_IMAGES])) if RAW_IMAGES else None
            DIMENTION = list(filter(None, [i.strip() for i in RAW_DIMENTION]))[0].split() if RAW_DIMENTION else None
            LENGTH = None
            WIDTH = None
            HEIGHT = None
            print('dimention', DIMENTION)
            if DIMENTION:
                LENGTH = float(DIMENTION[0]) * 100.0
                WIDTH = float(DIMENTION[2]) * 100.0
                HEIGHT = float(DIMENTION[4]) * 100.0
            WEIGHTS = list(filter(None, [i.strip() for i in RAW_WEIGHT])) if RAW_WEIGHT else None
            WEIGHT = None
            print('weights', WEIGHTS)
            if WEIGHTS:
                WEIGHTS = WEIGHTS[0].split()
                if WEIGHTS[1] == 'ounces':
                    WEIGHT = float(WEIGHTS[0])*(100.0/16)
                else:
                    WEIGHT = float(WEIGHTS[0])*100.0
            
            CATEGORIES = list(filter(None, [i.strip() for i in RAW_CATEGORIES])) if RAW_CATEGORIES  else None
            print('categories', CATEGORIES)
            FINAL_CATEGORIES = []
            if CATEGORIES:
                for i in range(0,len(CATEGORIES)):
                    f = furl(RAW_NODES[i])
                    FINAL_CATEGORIES.append({
                        'node': f.args['node'],
                        'title': CATEGORIES[i]
                    })
            RATING = list(filter(None, [i.strip() for i in RAW_RATING]))[0].split()[0] if RAW_RATING else None
            
            ATTRIBUTE_NAME = list(filter(None, [i.strip() for i in RAW_ATTRIBUTE_NAME])) if RAW_ATTRIBUTE_NAME  else None
            ATTRIBUTE_VALUE = list(filter(None, [i.strip() for i in RAW_ATTRIBUTE_VALUE])) if RAW_ATTRIBUTE_VALUE  else None
            ATTRIBUTES = None
            if ATTRIBUTE_NAME and ATTRIBUTE_VALUE:
                ATTRIBUTES = []
                for i in range (0, min(len(ATTRIBUTE_NAME), len(ATTRIBUTE_VALUE))):
                    ATTRIBUTES.append({
                        'name' : ATTRIBUTE_NAME[i],
                        'value' : ATTRIBUTE_VALUE[i]
                    })

            SET_OF_SIMILAR = set([])
            SIMILAR = list(filter(None, [i for i in RAW_SIMILAR])) if RAW_SIMILAR else None
            # print('similar similar', SIMILAR)
            # if SIMILAR:
            for item in SIMILAR:
                f = furl(item)
                if f.query.params.get('url') :
                    url = f.args['url']
                    # print('url ', url)
                    f = furl(url)
                segments = f.path.segments
                for i in range(1,len(segments)):
                    if segments[i-1] == "dp" and segments[i] != ASIN:
                        SET_OF_SIMILAR.add(segments[i])
                        break

            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()) if RAW_SALE_PRICE else None
            ORIGINAL_PRICE = ' '.join(''.join(RAW_ORIGINAL_PRICE).split()) if RAW_ORIGINAL_PRICE else None

            if ORIGINAL_PRICE:
                ORG = ''
                for i in range(1, len(ORIGINAL_PRICE)):
                    ORG += ORIGINAL_PRICE[i]
                if( ORIGINAL_PRICE[0] == '$'):
                    ORG = float(ORG) * 100.0 
                ORIGINAL_PRICE = ORG
            
            if SALE_PRICE:
                ORG = ''
                for i in range(1, len(SALE_PRICE)):
                    ORG += SALE_PRICE[i]
                if( SALE_PRICE[0] == '$'):
                    ORG = float(ORG) * 100.0 
                SALE_PRICE = ORG

            if page.status_code != 200:
                raise ValueError('captha')
            
            data = {
				'asin': ASIN,
				'title': TITLE,
				'brand': BRAND,
				'feature': FEATURE,
				'description': DESCRIPTION,
				'price': SALE_PRICE,
				'listPrice': ORIGINAL_PRICE,
				'prime': PRIME,
				'dimensions': {
                    'weight': WEIGHT,
                    'length': LENGTH,
                    'width': WIDTH,
					'height': HEIGHT,
				},
				'images': IMAGES,
				'attributes': ATTRIBUTES,
				'categories': FINAL_CATEGORIES,
				'similar': list(SET_OF_SIMILAR),
				'rating': RATING,
				}
            f=open(str('data/'+ASIN)+'.json','w')
            json.dump(data,f,indent=4)
            f.close()
            return
        except Exception as e:
            print(e)

def ReadAsin():
    f=open("input.txt", "r")
    AsinList = list(f)
    # print(AsinList)
    f.close()
    count = 1
    for item in AsinList:
        url = "http://www.amazon.com/dp/"+item.strip()+"/ref=nav_timeline_asin?_encoding=UTF8&psc=1"
        print (count,"Processing: ",url)
        count +=1
        if os.path.exists('data/'+item.strip()+'.json') == False:
            AmzonParser(url, item.strip())
            sleep(3)
 
if __name__ == "__main__":
    ReadAsin()
