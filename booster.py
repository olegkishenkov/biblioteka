import json
import os
import random
import time

import requests
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from channels.layers import get_channel_layer

response = requests.get('https://www.livelib.ru/books/top')
response.encoding = 'utf-8'
html = response.text
soup = BeautifulSoup(html, 'html.parser')
books = soup.findAll('div', class_='blist-biglist')[0].children
books_dict = {'books': []}
for book in books:
    rank = book.findAll('div', class_='brow-topno')[0].contents[0]
    title = book.findAll('a', class_='brow-book-name')[0].string
    author = book.findAll('a', class_='brow-book-author')[0].string
    year = book.findAll('div', class_='brow-details')[0].findAll('table')[0].findAll('tr')[1].findAll('td')[1].string
    books_dict['books'].append({
        'rank': rank,
        'title': title,
        'author': author,
        'year': year,
    })

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteka.settings')
channel_layer = get_channel_layer()

while True:
    async_to_sync(channel_layer.group_send)(
        'chat_default',
        {
            'type': 'chat_message',
            'message': str(books_dict['books'][random.randrange(0, len(books_dict['books']))]),
        },
    )
    time.sleep(5)