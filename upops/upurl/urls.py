from django.conf.urls import include, url
from views import *


urlpatterns = [
    url(r'group/$', group_list, name='url_group_list'),
    url(r'group/add/$', add_group, name='url_add_group'),
    url(r'url/$', url_list, name='url_list'),
    url(r'url/add/$', add_url, name='add_url'),
    url(r'group/edit/$', edit_group, name='url_edit_group'),
    url(r'url/edit/$', edit_url, name='url_edit'),
    url(r'url/del/$', del_url_group, name='url_del'),
]
