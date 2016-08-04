from django.conf.urls import include, url
from views import *


urlpatterns = [
    url(r'idc/$', asset_idc, name='asset_idc'),
    url(r'idc/add/$', asset_add_idc, name='asset_add_idc'),
    url(r'idc/edit/$', idc_edit, name='asset_idc_edit'),
    url(r'idc/del/$', asset_del, name='asset_idc_del'),
    url(r'host/$', asset_host, name='asset_host'),
    url(r'host/add/$', host_add, name='asset_add_host'),
    url(r'host/edit/$', host_edit, name='asset_host_edit'),
    url(r'host/del/$', asset_del, name='asset_host_del'),
    url(r'group/$', asset_group, name='asset_group'),
    url(r'group/add/$', add_group, name='asset_add_group'),
    url(r'group/edit/$', group_edit, name='asset_group_edit'),
    url(r'group/del/$', asset_del, name='asset_group_del'),
]
