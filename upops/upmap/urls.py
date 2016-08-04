from django.conf.urls import include, url
from upmap.views import *

urlpatterns = [
    url('^$', show_proxy_url, name='map_info'),
    url('urldel/$', del_proxy_url, name='map_url_del'),
    url('urladd/$', add_proxy_url, name='map_url_add'),
]
