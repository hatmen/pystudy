from django.conf.urls import include, url
from views import *


urlpatterns = [
    url(r'^trust/host/$', trust_host, name='auto_trust_host'),
    url(r'^soft/install/$', install_soft, name='auto_soft_install'),
    url(r'^tomcat/install/$', install_tomcat, name='auto_tomccat_install')
]

