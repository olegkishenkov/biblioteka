from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from exlibris.models import Book, Author, Reader, Lend
from .forms import BookForm


# Create your views here.

class BookList(ListView):
    model = Book

    def get_queryset(self):
        return self.model.objects.filter(title__startswith='Harry')


class BookView(DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test'] = self.request.META['HTTP_USER_AGENT']

        return context


class BookCreate(CreateView):
    model = Book
    fields = ['title', 'year', 'author']
    success_url = reverse_lazy('book_list')


class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'year', 'author']
    success_url = reverse_lazy('book_list')


class BookDelete(DeleteView):
    model = Book
    fields = ['title', 'year', 'author']
    success_url = reverse_lazy('book_list')


class AuthorList(ListView):
    model = Author


class AuthorView(DetailView):
    model = Author

class ReaderList(ListView):
    model = Reader


class ReaderView(DetailView):
    model = Reader


class LendList(ListView):
    model = Lend
