# -*- coding:utf-8 -*-
from django.db.models import Q
from updbm.db_api import *
from updbm.models import *


@auth_login()
def common_db(request):
    name = request.session.get('username', False)
    dev_dbname_list = []
    user_db_status = DBM_STATUS
    slave_dbname_list = dbname_list
    db = dbSource()
    #dev_dbname_list.append(x[0] for x in db.dev_db('show databases')[5::])
    for x in db.dev_db('show databases')[5::][::-1]:
        dev_dbname_list.append(x[0])
    dbm_list = DBManage.objects.filter(username=name)[::-1]

    # 搜索
    search_dbname = request.GET.get('search_dbname', False)
    search_status = request.GET.get('search_status', False)
    search_name = request.GET.get('search_name', False)
    smg = request.GET.get('smg', False)

    # POST方法获取的参数
    if request.method == "POST":
        db_user_name = request.POST.get('name', False).strip()
        db_user_ip = request.POST.get('ip', False).strip()
        db_name = request.POST.get('dbname', False)
        db_commont = request.POST.get('comment', False)
        # 判断用户是否存在
        if db_user_name and db_user_ip and db_name:
            try:
                user_info = UpUser.objects.get(name=db_user_name)
            except UpUser.DoesNotExist:
                emg = u"%s 不存在，请创建此用户，然后申请权限！" % db_user_name
            else:
                #password = user_info.password
                #db_authorization(db_user_name, db_user_ip, password, db_name)
                dbm = DBManage(username_id=db_user_name, use_ip=db_user_ip, use_db=db_name, comment=db_commont,
                               status=1)
                dbm.save()
                smg = u'%s 添加 %s 数据库已提交给管理员，请耐心等待！' % (db_user_name, db_name)

    # 查询搜索结果
    if search_dbname:
        dbm_list = DBManage.objects.filter(use_db=search_dbname)
    if search_name:
        dbm_list = DBManage.objects.filter(Q(use_db=search_name) | Q(username_id=search_name))
    if search_status:
        dbm_list = DBManage.objects.filter(status=search_status)

    # 分页器，分页
    objects, page_range = pagination(request, dbm_list)
    return my_render('common/dbm.html', locals(), request)
