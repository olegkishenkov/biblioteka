from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookList.as_view(), name='book_list'),
    path('book_view/<int:pk>', views.BookView.as_view(), name='book_view'),
    path('book_new', views.BookCreate.as_view(), name='book_new'),
    path('book_edit/<int:pk>', views.BookUpdate.as_view(), name='book_edit'),
    path('book_delete/<int:pk>', views.BookDelete.as_view(), name='book_delete'),
    path('author_list', views.AuthorList.as_view(), name='author_list'),
    path('author_view/<int:pk>', views.AuthorView.as_view(), name='author_view'),
    path('reader_list', views.ReaderList.as_view(), name='reader_list'),
    path('reader_view/<int:pk>', views.ReaderView.as_view(), name='reader_view'),
    path('lend_list', views.LendList.as_view(), name='lend_list')
]