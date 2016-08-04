# -*- coding:utf-8 -*-
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from upops.models import *
from models import *
from django.db.models import Q
from db_api import *
import logging
import threading

logging.basicConfig()
logger = logging.getLogger('upops_info')


# 用户权限添加
@auth_login()
def db_add_perm(request):
    user_db_status = DBM_STATUS
    slave_dbname_list = dbname_list
    #dev_dbname_list = []
    db = dbSource()
    #for x in db.slave_db('show databases')[5::][::-1]:
        #dev_dbname_list.append(x[0])
    dbm_list = DBManage.objects.all()[::-1]
    user_list = UpUser.objects.filter(role=1)
    # 搜索
    if request.method == "GET":
        search_dbname = request.GET.get('search_dbname', False)
        search_status = request.GET.get('search_status', False)
        search_name = request.GET.get('search_name', False)
            # 查询搜索结果
        if search_dbname:
            dbm_list = DBManage.objects.filter(use_db=search_dbname)
        if search_name:
            dbm_list = DBManage.objects.filter(Q(use_db=search_name) |
                                               Q(username_id=search_name))
        if search_status:
            dbm_list = DBManage.objects.filter(status=search_status)

    # POST方法获取的参数
    if request.method == "POST":
        db_user_name = request.POST.get('name', False).strip()
        db_user_ip = request.POST.get('ip', False).strip()
        db_name = request.POST.get('dbname', False)
        db_commont = request.POST.get('comment', False)
        life_time = request.POST.get('time', False)

        # 判断用户是否存在
        if db_user_name and db_user_ip and db_name:
            try:
                user_info = UpUser.objects.get(name=db_user_name)
            except UpUser.DoesNotExist:
                emg = u"%s 不存在，请创建此用户，然后申请权限！" % db_user_name
            else:
                password = user_info.password
                if life_time:
                    if life_time == 1:
                        db_authorization(db_user_name, db_user_ip, password, db_name)
                        dbm = DBManage(username_id=db_user_name, use_ip=db_user_ip, use_db=db_name, comment=db_commont,
                               status=2)
                        dbm.save()
                        smg = u'%s 添加 %s 数据库成功！' % (db_user_name, db_name)
                    else:
                        life_time = float(life_time) + time.time()
                        db_authorization(db_user_name, db_user_ip, password, db_name)
                        db_life_time = DbLifeTime(username_id=db_user_name, use_ip=db_user_ip, use_db=db_name,
                                                  life_time=life_time)
                        db_life_time.save()
                        smg = u'%s 添加 %s 数据库成功！' % (db_user_name, db_name)


    # 需要审计的用户
    db_audit_list = DBManage.objects.filter(status=1)
    audit_num = len(db_audit_list)
    if audit_num > 3:
        db_audit_list = db_audit_list[0:3]

    # 分页器，分页
    objects, page_range = pagination(request, dbm_list)
    return my_render('updbm/dbperm.html', locals(), request)


# 用户信息
@auth_login()
def db_user_info(request):
    smg = request.GET.get('smg', False)
    emg = request.GET.get('emg', False)
    status = request.GET.get('search_status', False)
    name = request.GET.get('search_name', False)
    user_status = USER_STATUS
    # 用户列表
    db_user_all = UpUser.objects.all()[::-1]
    if status:
        db_user_all = UpUser.objects.filter(role=status)
    if name:
        db_user_all = UpUser.objects.filter(name=name)
    # 分页器
    objects, page_range = pagination(request, db_user_all)
    return my_render('updbm/dbuser.html', locals(), request)


# 用户添加
@auth_login()
def db_add_user(request):
    # POST方法获取的参数
    if request.method == "POST":
        name = request.POST.get('name', False)
        email = request.POST.get('email', False)
        status = request.POST.get('status', False)
        comment = request.POST.get('comment', False)
        message = add_db_user(name=name, email=email, status=status, comment=comment)
        mg = ''
        mg_name = ''
        if message == "success":
            mg = u'%s 添加成功！' % name
            mg_name = 'smg'
        elif message == "ok":
            mg = u'%s 已经存在！' % name
            mg_name = 'emg'
        elif message == "error":
            mg = u'%s 用户邮箱不正确！' % name
            mg_name = 'emg'
        logger.info(u'用户%s 添加数据库成功' % name)
        return HttpResponseRedirect(reverse('dbm_user_info')+'?%s=%s' % (mg_name, mg))


def dbm_user_info(request):
    return my_render('updbm/dbuser_info.html', locals(), request)


# 权限回收
@auth_login()
def db_revoke(request):
    db = dbSource()
    if request.method == "GET":
        dbm_id = request.GET.get('id', False)
        username = request.GET.get('username', False)
        ip = request.GET.get('ip', False)
        dbname = request.GET.get('dbname', False)
        role = request.GET.get('status', False)
        source_sql = ''
        url = ''
        # 判断数据库，并删除DBmanage表
        if dbname:
            source_sql = "revoke all on %s.* from '%s'@'%s'" % (dbname, username, ip)
            DBManage.objects.get(id=dbm_id).delete()
            url = 'dbm_db_perm'
            if dbname in dbname_list:
                db.slave_db(source_sql)
                pass
            else:
                db.dev_db(source_sql)
                pass

        elif role:
            a = UpUser.objects.get(name=username)
            a.role = role
            a.save()
            url = 'dbm_user_info'
        else:
            select_user = "select user, host from mysql.user where user='%s'" % username
            dev_result = db.dev_db(select_user)
            if dev_result:
                for dev_user, dev_host in dev_result:
                    dev_user_del_sql = "drop user '%s'@'%s'" % (dev_user, dev_host)
                    try:
                        msg = db.dev_db(dev_user_del_sql)
                    except :
                        logger.error(msg)
            slave_result = db.slave_db(select_user)
            if slave_result:
                for slave_user, slave_host in slave_result:
                    slave_user_del_sql = "drop user '%s'@'%s'" % (slave_user, slave_host)
                    db.slave_db(slave_user_del_sql)
            UpUser.objects.get(name=username).delete()
            url = 'dbm_user_info'
            logger.info(u'删除数据库用户%s' % username) 
        return HttpResponseRedirect(reverse(url))


@auth_login()
def db_audit(request):
    if request.method == "GET":
        passed = request.GET.getlist('pass', False)
        rejected = request.GET.getlist('reject', False)
        list_info = []
        status = ''
        if passed:
            list_info = passed[0].split(',')
            status = 2

        if rejected:
            list_info = rejected[0].split(',')
            status = 3

        if list_info:
            print list_info
            if list_info[0] == 'on':
                for dbm_id in list_info[1:]:
                    a = DBManage.objects.get(id=dbm_id)
                    username = a.username
                    b = UpUser.objects.get(name=username)
                    password = b.password
                    ip = a.use_ip
                    dbname = a.use_db
                    if status == 2:
                        db_authorization(username, ip, password, dbname)
                        pass
                    a.status = status
                    a.save()
            else:
                dbm_id = list_info[0]
                a = DBManage.objects.get(id=dbm_id)
                username = a.username
                b = UpUser.objects.get(name=username)
                password = b.password
                ip = a.use_ip
                dbname = a.use_db
                if status == 2:
                    db_authorization(username, ip, password, dbname)
                    pass
                a.status = status
                a.save()
    return HttpResponseRedirect(reverse('dbm_db_perm'))


@auth_login()
def db_backup_test(request):
    DB_TEST_NAME = ['3307_czyb', '3308_czyb', '3309_czyb', '3310_czyb']
    if request.method == "GET":
        backdb = []
        msg = backup_list()
        if msg:
            for i in backup_list():
                if i.isdigit():
                    backdb.append(i)
            backdb.sort()
        db_test = DbImportTest.objects.all()
        objects, page_range = pagination(request, db_test[::-1])
    return my_render('updbm/importdb.html', locals(), request)


@auth_login()
def db_import_test(request):
    if request.method == "GET":
        testdb = request.GET.get('testdb', False)
        backdb = request.GET.get('backdb', False)
        #tables_path_list = []
        if backdb and testdb:
            path_dir = backup_tables_list + backdb
            #table_list = backup_list(path_dir)
            #if table_list:
                #for x in table_list:
                    #tables_path_list.append(path_dir+'/'+x)

                #table_sum = len(tables_path_list)

            if testdb == "3306_czyb":
                port = 3306
            elif testdb == "3307_czyb":
                port = 3307
            elif testdb == "3308_czyb":
                port = 3308
            elif testdb == "3309_czyb":
                port = 3309
            elif testdb == "3310_czyb":
                port = 3310

            a = DbImportTest(testdb=testdb, backdb=backdb,  status=3)
            a.save()
            db_id = a.id
            #db_backup_tables(table_sum=table_sum, port=port, db_id=db_id, tables=tables_path_list, num=10, date_path=backdb)
            # 启动一个守护线程执行
            d = threading.Thread(target=db_myloader_tables, kwargs={'db_id': db_id, 'port': port, 'path': path_dir})
            d.setDaemon(True)
            d.start()
            #db_myloader_tables(db_id=db_id, port=port, path=path_dir)
        return HttpResponseRedirect(reverse("dbm_db_test"))



def db_life_revoke():
    db = dbSource()
    fields_list = DbLifeTime.objects.all()
    if fields_list:
        for field in fields_list:
            print field.use_db
            if float(field.life_time) < time.time():
                source_sql = "revoke all on %s.* from '%s'@'%s'" % (field.use_db, field.username, field.use_ip)
                # 从库脱敏
                #proxy_user = choice_db_views(field.use_db)
                #source_sql = "revoke proxy on %s from '%s'@'%s'" % (proxy_user, field.username, field.use_ip)
                if db.slave_db(source_sql) == "error":
                    loginfo.info(source_sql+ " fail ")
                else:
                    field.delete()
                    loginfo.info(source_sql+" success ")

