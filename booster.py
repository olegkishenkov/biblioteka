import argparse
import json
import os
import random
import time

import requests
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from channels.layers import get_channel_layer
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--Proxies', help='path to file with proxies')
args = parser.parse_args()
proxy_dict = {}
if args.Proxies:
    with open(args.Proxies) as f:
        proxy_list = f.readlines()
    proxy = proxy_list[random.randrange(len(proxy_list))]
    proxy_dict = {
        'http': 'http://{}'.format(proxy),
        'https': 'http://{}'.format(proxy),
    }

response = requests.get('https://www.livelib.ru/books/top', proxies=proxy_dict)
response.encoding = 'utf-8'
html = response.text

soup = BeautifulSoup(html, 'html.parser')
books = soup.findAll('div', class_='blist-biglist')[0].contents
books_string = '; '.join((book.findAll('div', class_='brow-topno')[0].contents[0] +
                      ' ' +
                      book.findAll('a', class_='brow-book-name')[0].string for book in books[:5]))
datetime_string = datetime.now().ctime()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteka.settings.base')
channel_layer = get_channel_layer()
async_to_sync(channel_layer.group_send)(
    'chat_default',
    {
        'type': 'chat_message',
        'message': '{} {}'.format(datetime_string, books_string),
    },
)