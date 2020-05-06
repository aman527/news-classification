import requests
import asyncio
import time
from bs4 import BeautifulSoup

base_url = 'https://www.newser.com/controlpage.aspx'

r = requests.get(base_url, params = {
    'control': 'storysquarecontainer',
    'sectionid': 117,
    'gridrownum': 100,
    'numgridrows': 100,
    'ajaxcall': 'y',
    'categoryid': 19,
    'ShowSimpleListView': True
})

soup = BeautifulSoup(r.content, 'lxml')

article_cards = soup.find_all('a', class_='aGridSquareLink')

articles = []
for card in article_cards:
    article = {
        'title': card.img['alt'],
        'url': 'https://www.newswer.com'+ card['href'],
        'description': ''
    }
    articles.append(article)

print(articles)