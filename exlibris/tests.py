from django.test import TestCase

# Create your tests here.
from django.urls import reverse

from exlibris.models import Author, Book, Reader


class TestExlibrisViews(TestCase):
    def test_book_list_get(self):
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)

    def test_book_detail_get__book_exists(self):
        author = Author.objects.create(name='John Doe')
        book = Book.objects.create(title='foo', year='1990-01-01', author=author)
        response = self.client.get(reverse('book_view', args=[book.pk]))
        self.assertEqual(response.status_code, 200)

    def test_book_detail_get__book_does_not_exist(self):
        response = self.client.get(reverse('book_view', args=[1]))
        self.assertEqual(response.status_code, 404)

    def test_book_create_get(self):
        response = self.client.get(reverse('book_new'))
        self.assertEqual(response.status_code, 200)

    def test_book_create_post__form_valid(self):
        author = Author.objects.create(name='John Doe')
        data = {
            'title': 'foo',
            'author': author.pk,
            'year': '1990-02-02',
        }
        response = self.client.post(reverse('book_new'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Book.objects.filter(title=data['title'], author=data['author'], year=data['year']))

    def test_book_create_post__form_invalid_date_empty_string(self):
        author = Author.objects.create(name='John Doe')
        data = {
            'title': 'foo',
            'author': author.pk,
            'year': '',
        }
        response = self.client.post(reverse('book_new'), data=data)
        self.assertFalse(Book.objects.filter(title=data['title'], author=author))
        self.assertEqual(response.status_code, 200)

    def test_book_edit_get__book_exists(self):
        author = Author.objects.create(name='Jonh Doe')
        book_data = {
            'title': 'Some Title',
            'year': '1990-01-01',
            'author': author,
        }
        book = Book.objects.create(**book_data)
        response = self.client.get(reverse('book_edit', args=[book.pk]))
        self.assertEqual(response.status_code, 200)

    def test_book_edit_get__book_does_not_exist(self):
        invalid_book_pk = 1
        response = self.client.get(reverse('book_edit', args=[invalid_book_pk]))
        self.assertEqual(response.status_code, 404)

    def test_book_edit_post__book_exists(self):
        author = Author.objects.create(name='John Doe')
        book_data = {
            'title': 'foo',
            'author': author,
            'year': '1990-02-02',
        }
        book = Book.objects.create(**book_data)
        book_form_data = {
            'title': 'bar',
            'author': author.pk,
            'year': '1991-03-03',
        }
        response = self.client.post(reverse('book_edit', args=[book.pk]), data=book_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Book.objects.filter(**book_data))

    def test_book_delete_get__book_exists(self):
        author = Author.objects.create(name='John Doe')
        book_data = {
            'title': 'foo',
            'author': author,
            'year': '1990-02-02',
        }
        book = Book.objects.create(**book_data)
        response = self.client.get(reverse('book_delete', args=[book.pk]))
        self.assertEqual(response.status_code, 200)

    def test_book_delete_post__book_exists(self):
        author = Author.objects.create(name='John Doe')
        book_data = {
            'title': 'foo',
            'author': author,
            'year': '1990-02-02',
        }
        book = Book.objects.create(**book_data)
        response = self.client.post(reverse('book_delete', args=[book.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Book.objects.filter(**book_data))

    def test_book_delete_get__book_does_not_exist(self):
        invalid_book_pk = 1
        response = self.client.get(reverse('book_delete', args=[invalid_book_pk]))
        self.assertEqual(response.status_code, 404)

    def test_author_list_get(self):
        response = self.client.get(reverse('author_list'))
        self.assertEqual(response.status_code, 200)

    def test_author_view_get__author_exists(self):
        author = Author.objects.create(name='John Doe')
        response = self.client.get(reverse('author_view', args=[author.pk]))
        self.assertEqual(response.status_code, 200)

    def test_author_view_get__author_does_not_exist(self):
        invalid_author_pk = 1
        response = self.client.get(reverse('author_view', args=[invalid_author_pk]))
        self.assertEqual(response.status_code, 404)

    def test_reader_list_get(self):
        response = self.client.get(reverse('reader_list'))
        self.assertEqual(response.status_code, 200)

    def test_reader_view_get__reader_exists(self):
        reader = Reader.objects.create(name='Rick Sanchez')
        response = self.client.get(reverse('reader_view', args=[reader.pk]))
        self.assertEqual(response.status_code, 200)

    def test_reader_view_get__reader_does_not_exist(self):
        invalid_reader_id = 1
        response = self.client.get(reverse('reader_view', args=[invalid_reader_id]))
        self.assertEqual(response.status_code, 404)

    def test_lend_list_get(self):
        response = self.client.get(reverse('lend_list'))
        self.assertEqual(response.status_code, 200)