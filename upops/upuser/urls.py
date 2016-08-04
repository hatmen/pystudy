from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'user/list/$', user_list, name='upuser_list'),
    url(r'user/add/', user_add, name='upuser_add'),
    url(r'access/list/$', access_list, name='upuser_access_list'),
    url(r'access/add/$', access_add, name='upuser_access_add'),
    url(r'user/edit/$', user_edit, name='upuser_edit'),
    url(r'access/edit/$', access_edit, name='upuser_access_edit'),
    url(r'user/del/$', user_del, name='upuser_del'),
    url(r'access/del/$', access_url_del, name='upuser_access_del'),
]

