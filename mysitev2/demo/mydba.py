# -*- coding:utf-8 -*-
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from views import auth_login
from models import dbname_info, dbuser_info
from django.db.models import Q
from paginator import pagination
from dbsource import dbConfig, random_chars
import time


@auth_login
def dba_info_list(request):
    dbname_list = []
    search_content = request.GET.get('searchname', False)
    new_username = request.GET.get('new_username', False)
    new_passwd = request.GET.get('new_password', False)
    if new_username and new_passwd:
        new_user = {'username': new_username, 'password': new_passwd}
    else:
        new_user = False

    if search_content:
        info_list = dbname_info.objects.filter(Q(username=search_content) |
                                               Q(use_db=search_content) |
                                               Q(use_ip=search_content))
        status = False
    else:
        info_list = dbname_info.objects.all()
        status = True
    num = len(info_list)
    dbname_sql = "show databases"
    dbsource = dbConfig()
    db_list = dbsource.dev_db(dbname_sql)
    for i in range(len(db_list))[:3:-1]:
        dbname_list.append(db_list[i][0])

    objects, page_range = pagination(request, info_list[::-1])
    context = RequestContext(request,
                             {'objects': objects,
                              'page_range': page_range,
                              'num': num,
                              'page_switch': status,
                              'new_user': new_user,
                              'dbname_list': dbname_list}
                             )
    return render_to_response('dba.html', context)


@auth_login
def dba_user_info(request):
    search_content = request.GET.get('searchname', False)
    if search_content:
        user_list = dbuser_info.objects.filter(Q(username=search_content) |
                                               Q(use_ip=search_content))
        status = False
    else:
        user_list = dbuser_info.objects.all()
        status = True
    num = len(user_list)
    objects, page_range = pagination(request, user_list[::-1], display_amount=20)
    context = RequestContext(request,
                             {'objects': objects,
                              'page_range': page_range,
                              'num': num,
                              'page_switch': status}
                             )
    return render_to_response('dbamanage.html', context)


def dba_add_info(request):
    dbsource = dbConfig()
    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    if request.method == "GET":
        username = request.GET['username']
        ip = request.GET['iphost']
        dbname = request.GET['dbname']

    source_sql = "show grants for '%s'@'%s'" % (username, ip)
    passwd = random_chars(length=10)

    if dbname in ['czyb', 'czyb_pay', 'youcai']:
        result = dbsource.slave_db(source_sql)
    else:
        result = dbsource.dev_db(source_sql)

    if result is not "ERROR":
        if dbname == 'czyb':
            privilege_sql = "grant select on czyb.* to '%s'@'%s'" % (username, ip)
            dbsource.slave_db(privilege_sql)
        elif dbname == 'czyb_pay':
            privilege_sql = "grant select on czyb_pay.* to '%s'@'%s'" % (username, ip)
            dbsource.slave_db(privilege_sql)
        elif dbname == 'youcai':
            privilege_sql = "grant select on youcai.* to '%s'@'%s'" % (username, ip)
            dbsource.slave_db(privilege_sql)
        else:
            privilege_sql = "grant SELECT, INSERT, UPDATE, DELETE, DROP, CREATE, INDEX, ALTER, LOCK TABLES ON %s.* to '%s'@'%s'" % (dbname, username, ip)
            dbsource.dev_db(privilege_sql)

        db_info = dbname_info(username=username, use_ip=ip, use_db=dbname, create_time=str(time_now))
        db_info.save()
    else:
        if dbname == 'czyb':
            privilege_sql = "grant select on czyb.* to '%s'@'%s' identified by '%s'" % (username, ip, passwd)
            dbsource.slave_db(privilege_sql)

        elif dbname == 'czyb_pay':
            privilege_sql = "grant select on czyb_pay.* to '%s'@'%s' identified by '%s'" % (username, ip, passwd)
            dbsource.slave_db(privilege_sql)
        else:
            privilege_sql = "grant SELECT, INSERT, UPDATE, DELETE, DROP, CREATE, INDEX, ALTER, LOCK TABLES ON %s.* to '%s'@'%s' identified by '%s'" % (dbname, username, ip, passwd)
            dbsource.dev_db(privilege_sql)
        user_info = dbuser_info(username=username, use_ip=ip, passwd=passwd)
        user_info.save()
        db_info = dbname_info(username=username, use_ip=ip, use_db=dbname, create_time=str(time_now))
        db_info.save()
        return HttpResponseRedirect('/demo/dbashow/?new_username=%s&new_password=%s' % (username, passwd))

    return HttpResponseRedirect('/demo/dbashow/')


def revoke(request):
    dbsource =dbConfig()
    if request.method == "GET":
        mydba_id = request.GET['id']
        username = request.GET['username']
        ip = request.GET['ip']
        dbname = request.GET['dbname']

    if dbname:
        source_sql = "revoke all on %s.* from '%s'@'%s'" % (dbname, username, ip)
        dbname_info.objects.get(id=mydba_id).delete()
        url = "/demo/dbashow/"
    else:
        source_sql = "drop user '%s'@'%s'" % (username, ip)
        dbuser_info.objects.get(id=mydba_id).delete()
        url = "/demo/dbauser/"

    if dbname in ['czyb', 'czyb_pay']:
        dbsource.slave_db(source_sql)
    else:
        dbsource.dev_db(source_sql)
        dbsource.slave_db(source_sql)

    return HttpResponseRedirect(url)
