#from django.conf.urls import patterns, include, url
from django.conf.urls import include, url
from django.contrib import admin
from mybook.api import UsersList
import mybook.views
import rest_framework_swagger
from mybook.views import home, auth, signout, books_recs, add_list, view_list, author, genre, delete_book

from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='API name')
urlpatterns = [
    url(r'^docs/', schema_view)
]

urlpatterns += [
    url(r'^$', home, name='home'),
    url(r'^auth/', auth, name='auth'),
    url(r'^signout/',signout,name='signout'),
    url(r'^author/',author,name='author'),
    url(r'^genre/',genre,name='genre'),
    url(r'^delete_book/',delete_book,name='delete_book'),
    url(r'^add_list/',add_list,name='add_list'),
    url(r'^view_list/',view_list,name='view_list'),
    url(r'^books-recs/',books_recs,name='books_recs'),
    url(r'^admin/', admin.site.urls),
    url(r'^users-list/',UsersList.as_view(),name='users-list')
]
