from django.conf.urls import include, url
from upops.views import *
from upops.common_views import *

#handler400 = page_not_found
#handler404 = page_not_found
#handler500 = page_error

urlpatterns = [
    #url(r'^$', common_login, name='common_login'),
    url(r'^$', admin_login, name='admin_login'),
    url(r'admin/login/$', admin_login, name='admin_login'),
    url(r'^dbm/$', common_db, name='common_db'),
    url(r'^admin/index/$', index, name='upops_admin'),
    url(r'^logout/', login_out, name='logout'),
    url(r'^admin/upurl/', include('upurl.urls')),
    url(r'^admin/updbm/', include('updbm.urls')),
    url(r'^admin/upasset/', include('upasset.urls')),
    url(r'^admin/upmap/', include('upmap.urls')),
    url(r'^admin/upauto/', include('upauto.urls')),
    url(r'^admin/upuser/', include('upuser.urls')),
    url(r'^admin/set_password/$', modify_password, name='set_password'),
]
