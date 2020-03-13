from django.contrib import admin

# Register your models here.
from .models import Author, Book, Reader, Lend
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Reader)
admin.site.register(Lend)