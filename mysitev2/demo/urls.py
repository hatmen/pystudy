from django.conf.urls import include, url
from django.conf import settings
from demo import views, mydba, nginx_add_conf, task

urlpatterns = [
    url(r'^bootstrap/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.BOOTSTRAP_ROOT}),
    url(r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ASSETS_ROOT}),
    url(r'^vendors/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.VENDORS_ROOT}),
    url(r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.VENDORS_ROOT}),
    url(r'^images/(?P<path>.*)', 'django.views.static.serve', {'document_root': settings.IMAGE_ROOT}),
    url(r'^$', views.user_login),
    url(r'^login$', views.user_login),
    url(r'logout$', views.user_logout),
    url(r'^dbagrant/$', mydba.dba_add_info),
    url(r'^dbashow/$', mydba.dba_info_list),
    url(r'^dbauser/$', mydba.dba_user_info),
    url(r'^dbarevoke/$', mydba.revoke),
    url(r'^urlshow/$', nginx_add_conf.show_proxy_url),
    url(r'^urldel/$', nginx_add_conf.del_proxy_url),
    url(r'^urladd/$', nginx_add_conf.add_proxy_url),
    url(r'^taskshow/$', task.task_show),
    url(r'^taskcheck/$', task.task_check),
    url(r'taskupdate/$', task.task_update),
    url(r'^addtask/$', task.task_add),
    url(r'taskdel/$', task.task_del),
    url(r'taskstart/$', task.task_start),
    url(r'commurl/$', views.commonly_url),
    url(r'^(?P<page>.*)$', views.page),
]
