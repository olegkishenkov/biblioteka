import json
import os
import random
import time

import requests
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from channels.layers import get_channel_layer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteka.settings')
channel_layer = get_channel_layer()

while True:
    response = requests.get('https://www.livelib.ru/books/top')
    response.encoding = 'utf-8'
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    books = soup.findAll('div', class_='blist-biglist')[0].contents
    books_string = '; '.join((book.findAll('div', class_='brow-topno')[0].contents[0] +
                              ' ' +
                              book.findAll('a', class_='brow-book-name')[0].string for book in books[:5]))

    async_to_sync(channel_layer.group_send)(
        'chat_default',
        {
            'type': 'chat_message',
            'message': books_string,
        },
    )

    time.sleep(5)
