from datetime import datetime

import requests
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from channels.layers import get_channel_layer
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'parses booklib.ru book top and sends the first 5 books\' names to the channel layer group chat_default'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', '-w', action='store_true', help='print data to stdout')

    def handle(self, *args, **options):
        response = requests.get('https://www.livelib.ru/books/top')
        response.encoding = 'utf-8'
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        books = soup.findAll('div', class_='blist-biglist')[0].contents
        books_string = '\n'.join((book.findAll('div', class_='brow-topno')[0].contents[0] +
                                  ' ' +
                                  book.findAll('a', class_='brow-book-name')[0].string for book in books[:100]))
        datetime_string = datetime.now().ctime()
        if options['verbose']:
            self.stdout.write(datetime_string+'\n'+books_string)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_default',
            {
                'type': 'chat_message',
                'message': '{}\n{}'.format(datetime_string, books_string),
            },
        )
