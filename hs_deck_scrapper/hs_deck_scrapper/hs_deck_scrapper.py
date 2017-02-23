import requests
import codecs
import urllib
from scrapy.selector import Selector
from enum import Enum
import json
import re
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
import sys
import datetime
import pymongo


class Render(QWebPage):  
  def __init__(self, url):  
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.mainFrame().load(QUrl(url))  
    self.app.exec_()  

  def _loadFinished(self, result):  
    self.frame = self.mainFrame()  
    self.app.quit()


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


# confirm 1: 인증글, gamemode 1: 정규전, concept 1: 전설등급
# 덱 리스트는 하루전날 올라온 리스트를 리턴
def get_deck_list(character, confirm=0, gamemode=1, page=1, concept=1):
    headers = {
        'Referer': BASE_URL
    }

    data = {
        'class': character,
        'concept': concept,
        'gamemode': gamemode,
        'page': page,
        'confirm': confirm
    }

    today = datetime.date.today()

    yesterday_deck_list = {}
    is_over = False
    month = 0
    day = 0

    while not is_over:
        url_template = 'list.ajax.php?class={0}&gamemode={1}&concept={2}&page={3}'.format(character, gamemode, concept, page)
        r = requests.post(BASE_URL + 'list.ajax.php', headers = headers, data = data)
        html =  r.text
        sel = Selector(text=html)
        deck_lists = sel.css('.subject a::attr(href)').extract()

        for row_html in sel.xpath('//tr').extract():
            row_sel = Selector(text=row_html)
            title = row_sel.xpath('//td[3]/a/text()').extract()[0]
            date = row_sel.xpath('//td[6]/text()').extract()[0]
            if '-' in date:
                month, day = date.split('-')
                month = int(month)
                day = int(day)
                if today.month == month and today.day - 1 == day:
                    yesterday_deck_list[title] = {}
                    yesterday_deck_list[title]['url'] = urllib.parse.urljoin(BASE_URL, row_sel.css('.subject a::attr(href)').extract()[0])
                    yesterday_deck_list[title]['date'] = str(month) + '-' + str(day)
                if today.month >= int(month) and today.day -1 > int(day):
                    is_over = True
                    break

        page += 1

    return yesterday_deck_list


def get_deck_info(deck_title, url):
    p = re.compile('(\d+)')
    m = p.search(url)
    if not m:
        return None

    idx = m.group()

    render = Render(BASE_URL + 'view.php?idx=' + idx)
    result = render.frame.toHtml()
    

    sel = Selector(text=result)
    deck_info_html = sel.xpath('//*[@class="deck-card-wrap"]').extract()
    
    full_html='{0}</br>'.format(deck_title)
    title_html = '<b style="color:#ff0000">{} 카드 {}</b></br>'
    body_html=''
    row_html = '<span style="color:#0070c0">[{0}] </span><a href="http://hs.inven.co.kr/dataninfo/card/detail.php?code={1}" target="_blank" hs-card="{1}" style="color:{2};">{3}</a> {4}</br>'

    page = ''
    rarity_colors = [ '#585858', '#000', '#000', '#0070dd', '#a335ee', '#ff8000']

    for info_html in deck_info_html:
        deck_sel = Selector(text = info_html)
        title = deck_sel.xpath('//*[@class="deck-card-title"]/text()').extract()[0]
        card_cnt = deck_sel.xpath('//*[@class="deck-card-title"]/span/text()').extract()[0]
        full_html += title_html.format(title, card_cnt)
        for card_html in deck_sel.xpath('//*[@class="deck-card-table"]/a').extract():
            card_sel = Selector(text = card_html)
            rarity = card_sel.css('.td b::attr(class)').extract()[0][-1]
            code = card_sel.css('a::attr(hs-card)').extract()[0]
            card_name = card_sel.css('.td b::text').extract()[0]
            cnt = card_sel.css('.count::text').extract()[0]
            cost = card_sel.css('.is-button::text').extract()[0]
            full_html += row_html.format(cost, code, rarity_colors[int(rarity)], card_name, cnt)
        full_html += '</br>'

    return full_html


#ds153719.mlab.com:53719/hs_deck, Home : { db : "hs_deck" }
def save_to_db(deck_title, date, deck_info):
    client = pymongo.MongoClient('mongodb://hs_deck:12345678@ds153719.mlab.com:53719/hs_deck')
    db = client.hs_deck
    hs_deck = db.hs_deck
    data = {
        'deck_title': deck_title,
        'date': date,
        'deck_info': deck_info
    }
    #hs_deck.insert(data)
    for item in hs_deck.find({'date': '2-22'}):
        print(item)


deck_lists = get_deck_list(Character.SHAMAN.value)
for deck_title, info in deck_lists.items():
    deck_info_html = get_deck_info(deck_title, info['url'])
    save_to_db(deck_title, info['date'], deck_info_html)

#with codecs.open("sample.html", "w", encoding='utf-8') as f:
#    f.write(test)

