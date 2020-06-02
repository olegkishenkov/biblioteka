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
        parser.add_argument('ratings', nargs='+', help='ratings to parse apart from livelib')
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
        books_outer_list = []
        if 'readrate' in options['ratings']:
            response = requests.get('https://readrate.com/rus/ratings/top100')
            response.encoding = 'utf-8'
            html = response.text

            soup = BeautifulSoup(html, 'html.parser')
            books = soup.findAll('div', class_='books-list vertical-list')[0].findAll('div', class_='list-item')
            books_list = []
            for book in books:
                rank_string = book.findAll('div', class_='item-index unsellectable')[0].string.strip(' \n')
                title_string = book.findAll('div', class_='title')[0].string
                authors_string = book.findAll('li', class_='contributor item')[0].text
                books_list.append(
                    {
                        'rank': rank_string,
                        'title': title_string,
                        'author': authors_string,
                        'year': '1970',
                    }
                )
            books_dict = {'moment': timezone.now(), 'books': books_list, 'rating': 'readrate'}
            books_outer_list.append(books_dict)

        if 'livelib' in options['ratings']:
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
                rank_string = book.findAll('div', class_='brow-topno')[0].contents[0].strip('№')
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
            books_dict = {'moment': timezone.now(), 'books': books_list, 'rating': 'livelib'}
            books_outer_list.append(books_dict)

        if options['verbose']:
            self.stdout.write(pprint.pformat(books_outer_list))

        if not options['no_db_input']:
            for _ in books_outer_list:
                rating = _['rating']
                moment = _['moment']
                for book in _['books']:
                    author, created = Author.objects.get_or_create(name=book['author'])
                    author.save()
                    book_, created = Book.objects.get_or_create(
                        title=book['title'],
                        year=book['year'] + '-01-01',
                        author=author
                    )
                    book_.save()
                    if rating == 'livelib':
                        rating_ = Rating.objects.get(name='Livelib Top 100')
                    elif rating == 'readrate':
                        rating_ = Rating.objects.get(name='Readrate 100 лучших книг')
                    else:
                        raise NotImplementedError('the rating {} is not implemented'.format(rating))
                    entry = Entry.objects.create(
                        rating=rating_,
                        book=book_,
                        date=moment,
                        rank=book['rank'].lstrip('№'),
                    )
                    entry.save()

        if not options['no_message']:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'chat_default',
                {
                    'type': 'chat_message',
                    'message': pprint.pformat(books_outer_list),
                },
            )
