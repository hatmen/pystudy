from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'dbperm/$', db_add_perm, name='dbm_db_perm'),
    url(r'dbuser/$', db_user_info, name='dbm_user_info'),
    url(r'dbuser/add/$', db_add_user, name='dbm_db_user'),
    url(r'dbuser/info/$', db_user_info, name='dbm_db_user_info'),
    url(r'dbrevoke/$', db_revoke, name='dbm_db_revoke'),
    url(r'dbaudit/$', db_audit, name='dbm_db_audit'),
    url(r'dbtest/$', db_backup_test, name='dbm_db_test'),
    url(r'dbimport/$', db_import_test, name='dbm_import_test')
]
