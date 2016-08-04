# -*- coding:utf-8 -*-

from django.shortcuts import render
from upops.api import *
from upuser.user_api import *
from upops.models import *
import datetime
import logging
logging.basicConfig()
loginfo = logging.getLogger('upops_info')
logerror = logging.getLogger(('upops_error'))


@auth_login()
def user_list(request):
    if request.method == "GET":
        user_info = User.objects.all()
        objects, page_range = pagination(request, user_info)
    return my_render("upuser/user_list.html", locals(), request)


@auth_login()
def user_add(request):
    url = AccessUrl.objects.all()
    if request.method == "POST":
        password = random_chars(10)
        print password
        access_url = request.POST.getlist('access_url', '')
        print access_url
        username = request.POST.get('name', '')
        email = request.POST.get('email', '')
        is_active = request.POST.get('is_active', 1)
        is_email = request.POST.get('is_email', 1)
        try:
            if "" in [username, email]:
                emg = u'username, email 不能为空'
                raise ServerError, emg
            check_user_is_exist = User.objects.filter(username=username)
            if check_user_is_exist:
                emg = u'用户%s 已经存在' % username
                raise ServerError, emg
        except ServerError, e:
            loginfo.info(e)
        else:
            try:
                user = add_user(access_url, username=username, password=password, email=email, is_active=is_active,
                         date_joined=datetime.datetime.now())
                smg = u'%s 添加成功！' % username
                if [True if '1' == is_email else False]:
                    context = CONTEXT % (username, username, password, email)
                    mail_send(SUBJECT, email, context)
            except Exception, e:
                loginfo.error(e)

    return my_render('upuser/add_user.html', locals(), request)


@auth_login()
def access_list(request):
    if request.method == "GET":
        urls = AccessUrl.objects.all()
        objects, page_range = pagination(request, urls)
    return my_render("upuser/access_list.html", locals(), request)


@auth_login()
def access_edit(request):
    if request.method == "GET":
        url = request.GET.get('url', False)
        url_info = AccessUrl.objects.get(url=url)
        user_all = User.objects.all()

    if request.method == "POST":
        url = request.POST.get('url', False)
        comment = request.POST.get('comment', False)
        users = request.POST.getlist('username', False)
        url_info = AccessUrl.objects.filter(url=url)
        url_info.update(url=url, comment=comment)
        a = AccessUrl.objects.get(url=url)
        if users:
            a.user_set.clear()
            for user in users:
                u = User.objects.get(username=user)
                a.user_set.add(u)
        else:
            a.user_set.clear()
        return HttpResponseRedirect(reverse("upuser_access_list"))
    return my_render("upuser/access_edit.html", locals(), request)


@auth_login()
def access_add(request):
    if request.method == "GET":
        user_all = User.objects.all()
    if request.method == "POST":
        url = request.POST.get('url', False)
        comment = request.POST.get('comment', False)
        user = request.POST.getlist('username', False)
        if url and comment:
            access_url = AccessUrl(url=url, comment=comment)
            access_url.save()
            if user:
                for username in user:
                    user_info = User.objects.get(username=username)
                    access_url.user_set.add(user_info)

    return my_render("upuser/add_access.html", locals(), request)


@auth_login()
def user_edit(request):
    if request.method == "GET":
        id = request.GET.get('id', False)
        if id:
            user = User.objects.get(id=id)
            urls = user.url.all()
            url_all = AccessUrl.objects.all()
    if request.method == "POST":
        username = request.POST.get('name', False)
        email = request.POST.get('email', False)
        password = request.POST.get('password', False)
        access_url = request.POST.getlist('access_url', False)
        is_active = request.POST.get('is_active', 1)
        is_email = request.POST.get('email', 0)
        print username, email, password, access_url
        status = update_user(access_url, username=username, email=email, password=password, is_active=int(is_active))
        if status:
            smg = u"%s 更新成功" % username
        else:
            emg =  u"%s 更新失败" % username
        if is_email == "1":
            context = CONTEXT % (username, username, password, email)
            mail_send(SUBJECT, email, context)
        return HttpResponseRedirect(reverse("upuser_list"))
    return my_render("upuser/edit_user.html", locals(), request)


@auth_login()
def user_del(request):
    if request.method == "GET":
        username = request.GET.get('username')
        del_user(username=username)
    return HttpResponseRedirect(reverse("upuser_list"))


@auth_login()
def access_url_del(request):
    if request.method == "GET":
        url = request.GET.get('url', False)
        AccessUrl.objects.get(url=url).delete()
    return HttpResponseRedirect(reverse("upuser_access_list"))

