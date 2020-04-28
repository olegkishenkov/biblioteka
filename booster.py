import json
import os
import random
import time

import requests
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from channels.layers import get_channel_layer
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteka.settings.base')
channel_layer = get_channel_layer()

response = requests.get('https://www.livelib.ru/books/top')
response.encoding = 'utf-8'
html = response.text
soup = BeautifulSoup(html, 'html.parser')
books = soup.findAll('div', class_='blist-biglist')[0].contents
books_string = '; '.join((book.findAll('div', class_='brow-topno')[0].contents[0] +
                      ' ' +
                      book.findAll('a', class_='brow-book-name')[0].string for book in books[:5]))
datetime_string = datetime.now().ctime()

async_to_sync(channel_layer.group_send)(
    'chat_default',
    {
        'type': 'chat_message',
        'message': '{} {}'.format(datetime_string, books_string),
    },
)