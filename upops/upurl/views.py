# -*- coding:utf-8 -*-
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from upops.api import *
from models import *


# url组列表
@auth_login()
def group_list(request):
    # 搜索组名
    if request.method == "GET":
        search_name = request.GET.get('search_name', False)
        if search_name:
            group_info = UrlGroup.objects.filter(Q(name=search_name))
        else:
            # 列出所有组
            group_info = UrlGroup.objects.all()
        objects, page_range = pagination(request, group_info)
    return my_render('upurls/group_urls.html', locals(), request)


# url列表
@auth_login()
def url_list(request):
    url_group = UrlGroup.objects.all()
    if request.method == "GET":
        search_name = request.GET.get('search_name', False)
        if search_name:
            group_id = UrlGroup.objects.filter(name=search_name)
            if group_id:
                url_info = Url.objects.filter(Q(name=search_name) | Q(group_id=group_id))
            else:
                url_info = Url.objects.filter(name=search_name)
        else:
            # 列出所有url列表
            url_info = Url.objects.all()
        objects, page_range = pagination(request, url_info)
    return my_render('upurls/urls_list.html', locals(), request)


@auth_login()
def add_url(request):
    url_group = UrlGroup.objects.all()
    if request.method == "POST":
        url_name = request.POST.get('name', False)
        url = request.POST.get('url', False)
        group = request.POST.get('group', False)
        info = request.POST.get('info', False)
        comment = request.POST.get('comment', False)
        try:
            add_to_url = Url(name=url_name, http=url, info=info, group_id=group, comment=comment)
        finally:
            add_to_url.save()
            smg = u'%s 添加成功'% url_name
    return my_render('upurls/add_url.html', locals(), request)


@auth_login()
def add_group(request):
    url_group_null = Url.objects.filter(group_id=None)
    if request.method == "POST":
        group_name = request.POST.get('name', False)
        url_id_list = request.POST.getlist('url', False)
        comment = request.POST.get('comment', False)
        try:
            group = UrlGroup(name=group_name, comment=comment)
        finally:
            group.save()
            if url_id_list:
                for url_id in url_id_list:
                    url = Url.objects.get(id=url_id)
                    url.group_id = group.id
                    url.save()
            smg = u'%s组添加成功！' % group_name
    return my_render('upurls/add_group.html', locals(), request)


@auth_login()
def edit_group(request):
    if request.method == "GET":
        group_id = request.GET.get('id', False)
        info = UrlGroup.objects.get(id=group_id)
        url_list_info = info.url_set.all()
        url_group_null = Url.objects.filter(group_id=None)
        return my_render('upurls/group_edit.html', locals(), request)

    if request.method == "POST":
        group_id = request.POST.get('id', False)
        name = request.POST.get('name', False)
        url_id_list = request.POST.getlist('url', False)
        comment = request.POST.get('comment', False)
        UrlGroup.objects.filter(id=group_id).update(name=name, comment=comment)
        if url_id_list:
            for url_id in url_id_list:
                url = Url.objects.filter(id=url_id).update(group_id=group_id)
        else:
            info = UrlGroup.objects.get(id=group_id)
            info.url_set.all().update(group_id=None)

    return HttpResponseRedirect(reverse('url_group_list'))


@auth_login()
def edit_url(request):
    if request.method == "GET":
        url_id = request.GET.get('id', False)
        info = Url.objects.get(id=url_id)
        url_no_group = UrlGroup.objects.all().exclude(id=info.group_id)
        return my_render("upurls/url_edit.html", locals(), request)

    if request.method == "POST":
        id = request.POST.get('id', False)
        name = request.POST.get('name', False)
        url = request.POST.get('url', False)
        group = request.POST.get('group', False)
        info = request.POST.get('info', False)
        comment = request.POST.get('comment', False)
        if not group:
            group = None
        Url.objects.filter(id=id).update(name=name, http=url, info=info, comment=comment, group=group)
        return HttpResponseRedirect(reverse('url_list'))


@auth_login()
def del_url_group(request):
    if request.method == "GET":
        url_id = request.GET.get('url_id', False)
        group_id = request.GET.get('group_id', False)
        if url_id:
            Url.objects.get(id=url_id).delete()
            url = 'url_list'

        if group_id:
            UrlGroup.objects.get(id=group_id).delete()
            url = 'url_group_list'
    return HttpResponseRedirect(reverse(url))

