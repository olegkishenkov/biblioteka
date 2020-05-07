# from datetime import datetime

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

    def handle(self, *args, **options):
        response = requests.get('https://www.livelib.ru/books/top')
        response.encoding = 'utf-8'
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        books = soup.findAll('div', class_='blist-biglist')[0].contents
        books_string = '\n'.join((book.findAll('div', class_='brow-topno')[0].contents[0] +
                                  ' ' +
                                  book.findAll('a', class_='brow-book-name')[0].string for book in books[:100]))
        datetime_string = timezone.now()

        if options['verbose']:
            self.stdout.write(str(datetime_string)+'\n'+books_string)

        if not options['no_db_input']:
            soup = BeautifulSoup(html, 'html.parser')
            books = soup.findAll('div', class_='blist-biglist')[0].contents
            for book in books:
                rank_string = book.findAll('div', class_='brow-topno')[0].contents[0]
                title_string = book.findAll('a', class_='brow-book-name')[0].string
                author_string = book.findAll('a', class_='brow-book-author')[0].string
                details_string = book.findAll('div', class_='brow-details')[0]
                year_string = details_string.findAll(
                    lambda _: (_.name=='tr') and (_.text.find('Год издания')>-1)
                )[0].td.nextSibling.text
                author = Author.objects.create(name=author_string)
                author.save()
                book_ = Book.objects.create(title=title_string, year=year_string+'-01-01', author=author)
                book_.save()
                rating = Rating.objects.filter(name='Livelib Top 100')[0]
                entry = Entry.objects.create(
                    rating=rating,
                    book=book_,
                    date=datetime_string,
                    rank=rank_string.lstrip('№'),
                )
                entry.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_default',
            {
                'type': 'chat_message',
                'message': '{}\n{}'.format(datetime_string, books_string),
            },
        )
