# -*- coding:utf-8 -*-
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from updbm.db_api import *
from models import *
import json
import os

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))


def page_not_found(request):
    return render_to_response('404.html')


def page_error(request):
    return render_to_response('500.html')


@auth_login()
def index(request):
    return my_render('index.html', locals(), request)


def common_login(request):
    if request.method == "POST":
        email = request.POST.get('email', False).strip()
        if not email:
            smg = u'请输入正确的邮箱地址！'
        else:
            info = email.split('@')
            if info[1] == 'czyb360.com':
                name = info[0]
                message = add_db_user(name=name, email=email, status=1, comment='')
                request.session['username'] = name
                request.session.set_expiry(12000)
                if message == "success":
                    welcome = u'恭喜您注册成功，请查看邮件内容！'
                    return HttpResponseRedirect(reverse('common_db')+"?smg=%s" % welcome)

                elif message == "forbidden":
                    smg = u'你已经被禁用，请联系管理员'
                    return my_render('login.html', locals(), request)

                elif message == 'error':
                    smg = u'邮箱可能不存在！'
                    return my_render('login.html', locals(), request)
                else:
                    pass
                return HttpResponseRedirect(reverse('common_db'))

            else:
                smg = u'您不在czyb360.com域中，请确认输入是否无误！'
    return my_render('login.html', locals(), request)


def admin_login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('upops_admin'))
    if request.method == "GET":
        return my_render('admin_login.html', locals(), request)

    if request.method == "POST":
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                request.session['username'] = username
                a = User.objects.get(username=username)
                access_url = a.url.all().values_list()
                urls_list = [url for url in access_url]
                urls = [url[0] for url in urls_list]
                request.session['access_url'] = urls
                request.session.set_expiry(12000)
                login(request, user)
                return HttpResponseRedirect(reverse('upops_admin'))
            else:
                message = u"用户已经被禁用！"
                return my_render('admin_login.html', locals(), request)
        else:
            message = u"用户名或密码输入不正确！"
            return my_render('admin_login.html', locals(), request)


def login_out(request):
    if request.session['username']:
        del request.session['username']
        logout(request)
    else:
        pass
    return HttpResponseRedirect(reverse("admin_login"))

@auth_login()
def modify_password(request):
    if request.method == "POST":
        username = request.session['username']
        password = request.POST.get('password', False)
        user = User.objects.get(username=username)
        if password:
            if password.strip():
                user.set_password(password)
                user.save()
                smg = u'修改成功'
            return HttpResponseRedirect(reverse('upops_admin'))
    return my_render('set_password.html', locals(), request)

