# from datetime import datetime
import pprint

import requests
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from channels.layers import get_channel_layer
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from exlibris.models import Author, Book, Rating, Entry

import re


class Command(BaseCommand):
    help = 'parses booklib.ru book top and sends the first 5 books\' names to the channel layer group chat_default'

    def add_arguments(self, parser):
        parser.add_argument('--verbose', '-w', action='store_true', help='print data to stdout')
        parser.add_argument(
            '--no-db-input',
            '-d',
            action='store_true',
            help='do not write parsed data to the database'
        )
        parser.add_argument(
            '--no-message',
            '-m',
            action='store_true',
            help='do not send a message to the channel layer'
        )

    def handle(self, *args, **options):
        response = requests.get('https://www.livelib.ru/books/top')
        response.encoding = 'utf-8'
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        books = soup.findAll('div', class_='blist-biglist')[0].contents
        # books_string = '\n'.join((book.findAll('div', class_='brow-topno')[0].contents[0] +
        #                           ' ' +
        #                           book.findAll('a', class_='brow-book-name')[0].string for book in books[:100]))
        books_list = []
        for book in books:
            rank_string = book.findAll('div', class_='brow-topno')[0].contents[0]
            title_string = book.findAll('a', class_='brow-book-name')[0].string
            author_string = book.findAll('a', class_='brow-book-author')[0].string
            details_string = book.findAll('div', class_='brow-details')[0]
            year_string = details_string.findAll(
                lambda _: (_.name == 'tr') and (_.text.find('Год издания') > -1)
            )[0].td.nextSibling.text
            books_list.append(
                {
                    'rank': rank_string,
                    'title': title_string,
                    'author': author_string,
                    'year': year_string,
                }
            )
        datetime_string = timezone.now()

        if options['verbose']:
            self.stdout.write(str(datetime_string) + '\n' + pprint.pformat(books_list))

        if not options['no_db_input']:
            # soup = BeautifulSoup(html, 'html.parser')
            # books = soup.findAll('div', class_='blist-biglist')[0].contents
            for book in books_list:
                author, created = Author.objects.get_or_create(name=book['author'])
                author.save()
                book_, created = Book.objects.get_or_create(
                    title=book['title'],
                    year=book['year'] + '-01-01',
                    author=author
                )
                book_.save()
                rating = Rating.objects.get(name='Livelib Top 100')
                entry = Entry.objects.create(
                    rating=rating,
                    book=book_,
                    date=datetime_string,
                    rank=book['rank'].lstrip('№'),
                )
                entry.save()

        if not options['no_message']:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'chat_default',
                {
                    'type': 'chat_message',
                    'message': '{}\n{}'.format(datetime_string, pprint.pformat(books_list)),
                },
            )
