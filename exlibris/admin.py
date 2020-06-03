from django.contrib import admin

# Register your models here.
from .models import Author, Book, Reader, Lend, Rating, Entry
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Reader)
admin.site.register(Lend)
admin.site.register(Rating)
admin.site.register(Entry)