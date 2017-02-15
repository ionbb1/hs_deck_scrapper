import requests
import codecs
import urllib
from scrapy.selector import Selector
from enum import Enum
import json
import re
import robobrowser

class Character(Enum):
    ALL = 1
    DRUID = 2
    HUNTER = 3
    WIZARD = 4
    PALADIN = 5
    PRIEST = 6
    THIEF = 7
    SHAMAN = 8
    WARLOCK = 9
    KNIGHT = 10

BASE_URL = 'http://hs.inven.co.kr/dataninfo/deck/new/'

def fetch_page(url, headers=None):
    r = requests.get(url, headers=headers)
    return r.text

def subject_links_from_listpage(url):
    headers = {
        'Referer': 'http://hs.inven.co.kr/dataninfo/deck/new/'
    }
    html = fetch_page(url, headers)
    sel = Selector(text=html)
    subject_links = sel.css('.subject a::attr(href)').extract()
    subject_links = [urllib.parse.urljoin(url, subject_link) for subject_link in subject_links]
    return subject_links
    '''
    with codecs.open("sample.html", "w", encoding='utf-8') as f:
        html = fetch_page("http://hs.inven.co.kr/dataninfo/deck/new/list.ajax.php?class=10,gamemode=1")
        f.write(html)
    '''

def get_deck_list(character, confirm=0, gamemode=1, page=1, concept=1):
    headers = {
        'Referer': 'http://hs.inven.co.kr/dataninfo/deck/new/'
    }
    data = {
        'class': character,
        'concept': concept,
        'gamemode': gamemode,
        'page': page,
        'confirm': confirm
    }

    url_template = 'list.ajax.php?class={0}&gamemode={1}&concept={2}&page={3}'.format(character, gamemode, concept, page)

    r = requests.post(BASE_URL + 'list.ajax.php', headers = headers, data = data)
    html =  r.text

    sel = Selector(text=html)
    deck_lists = sel.css('.subject a::attr(href)').extract()
    deck_lists = [urllib.parse.urljoin(BASE_URL, deck_list) for deck_list in deck_lists]

    return deck_lists

def get_deck_info(url):
    p = re.compile('(\d+)')
    m = p.search(url)
    if not m:
        return None

    idx = m.group()

    headers = {
        'Referer': 'http://hs.inven.co.kr/dataninfo/deck/new/'
    }
    data = {
        'idx': idx
    }

    r = requests.get(BASE_URL + 'view.php', headers = headers, params = data)
    html = r.text

    sel = Selector(text=html)
    sel.css('.subject a::attr(href)').extract()

    deck = []
    category = sel.xpath("//div[@id='hsDbDeckCardList']//div[@class='deck-card-left']//div[@class='deck-card-wrap']//div[@class='deck-card-title']//text()").extract()
    for i in category:
        deck.append({})
        deck[i]['category'] = sel.css('.deck-card-wrap deck-card-title::text').extract()

    return html

deck_lists = get_deck_list(Character.WIZARD.value)

test = get_deck_info(deck_lists[1])

#subject_links = subject_links_from_listpage("http://hs.inven.co.kr/dataninfo/deck/new/list.ajax.php")

#from pprint import pprint
#pprint(subject_links)


#with codecs.open("sample.html", "w", encoding='utf-8') as f:
#    f.write(temp)

