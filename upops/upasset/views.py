# -*- coding:utf-8 -*-
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Q
from models import *
from upops.api import *


@auth_login()
def asset_idc(request):
    if request.method == "GET":
        search_name = request.GET.get('search_name', False)
        if search_name:
            idc_info = IDC.objects.filter(name=search_name)
        else:
            idc_info = IDC.objects.all()
        objects, page_range = pagination(request, idc_info)
    return my_render('upasset/asset_idc.html', locals(), request)


@auth_login()
def asset_group(request):
    if request.method == "GET":
        group_all = AssetGroup.objects.all()
        search = request.GET.get('search_name', False)
        if search:
            group_all = AssetGroup.objects.filter(name=search)

        objects, page_range = pagination(request, group_all)
    return my_render('upasset/asset_group.html', locals(), request)


@auth_login()
def add_group(request):
    host_all = Asset.objects.all()
    if request.method == "POST":
        name = request.POST.get('name', '')
        host_list = request.POST.getlist('host', '')
        comment = request.POST.get('comment', '')

        try:
            get_name = AssetGroup.objects.filter(name=name)
            if not name:
                emg = u'主机组不能为空'
                raise ServerError(emg)
            if get_name:
                emg = u'主机组已经存在'
                raise ServerError(emg)

        except ServerError:
            print emg

        else:
            add_group = AssetGroup(name=name, comment=comment)
            add_group.save()
            smg = u'%s组添加成功' % name
            group_id = AssetGroup.objects.filter(name=name)
            if host_list:
                for host_id in host_list:
                    host = Asset.objects.get(id=host_id)
                    group = AssetGroup.objects.get(id=group_id)
                    host.group.add(group)
            else:
                pass
    return my_render('upasset/add_group.html', locals(), request)


@auth_login()
def group_edit(request):
    if request.method == "GET":
        group_id = request.GET.get('id', False)
        group = AssetGroup.objects.get(id=group_id)
        host_all = Asset.objects.all()
        return my_render('upasset/group_edit.html', locals(), request)

    if request.method == "POST":
        group_id = request.POST.get('id', False)
        name = request.POST.get('name', '')
        host_list = request.POST.getlist('host', '')
        comment = request.POST.get('comment', '')
        if group_id:
            a = AssetGroup.objects.filter(id=group_id).update(name=name, comment=comment)
            if host_list:
                for host_id in host_list:
                    h = Asset.objects.get(id=host_id)
                    g = AssetGroup.objects.get(id=group_id)
                    g.asset_set.clear()
                    g.asset_set.add(h)
            else:
                a = AssetGroup.objects.get(id=group_id)
                a.asset_set.clear()
    return HttpResponseRedirect(reverse('asset_group'))


@auth_login()
def asset_host(request):
    idc = IDC.objects.all()
    asset_group = AssetGroup.objects.all()
    asset_type = ASSET_TYPE
    host = Asset.objects.all()
    if request.method == "GET":
        host_id = request.GET.get('id', '')
        idc_id = request.GET.get('search_idc', False)
        group_id = request.GET.get('search_group', False)
        type_id = request.GET.get('search_type', False)
        search = request.GET.get('search_name', False)

        if idc_id:
            host_idc = IDC.objects.get(id=idc_id)
            host = host_idc.asset_set.all()
        if group_id:
            group = AssetGroup.objects.get(id=group_id)
            host = group.asset_set.all()
        if type_id:
            host = Asset.objects.filter(asset_type=type_id)
        if search:
            host = Asset.objects.filter(Q(hostname=search) | Q(ip=search))
        # if not host_id:
        #     host = Asset.objects.all()
        # else:
        #     host = Asset.objects.get(id=host_id)
        objects, page_range = pagination(request, host)
    return my_render('upasset/asset_host.html', locals(), request)


@auth_login()
def host_add(request):
    asset_types = ASSET_TYPE
    asset_envs = ASSET_ENV
    system_types = SYSTEM_TYPE
    idc_name = IDC.objects.all()
    #host_group = AssetGroup.objects.all()
    group = AssetGroup.objects.all()

    if request.method == "POST":
        hostname = request.POST.get('hostname', '')
        ip = request.POST.get('ip', '')
        # other_ip = request.GET['other_ip']
        port = request.POST.get('port', '')
        group_id = request.POST.getlist('group', '')
        # username = request.GET['username']
        idc = request.POST.get('idc', '')
        brand = request.POST.get('brand', '')
        cpu = request.POST.get('cpu', '')
        memory = request.POST.get('memory', '')
        disk = request.POST.get('disk', '')
        system_type = request.POST.get('system_type', '')
        system_version = request.POST.get('system_version', '')
        system_arch = request.POST.get('system_arch', '')
        cabinet = request.POST.get('cabinet', '')
        number = request.POST.get('number', '')
        asset_type = request.POST.get('asset_type', '')
        env = request.POST.get('env', '')
        sn = request.POST.get('sn', '')
        comment = request.POST.get('comment', False)

        try:
            asset_ip = Asset.objects.filter(ip=ip)
            asset_hostname = Asset.objects.filter(hostname=hostname)
            if asset_ip:
                emg = u"IP地址重复"
                raise ServerError(emg)

            if asset_hostname:
                emg = u"主机名重复"
                raise ServerError(emg)

        except ServerError:
            pass
        else:
            print hostname, ip, group_id, sn, system_type
            add_host = Asset(hostname=hostname, ip=ip, port=port, idc_id=idc, brand=brand, cpu=cpu, memory=memory,
                             disk=disk, system_type=unicode(system_type), system_version=system_version,
                             system_arch=system_arch, cabinet=cabinet, number=number, asset_type=asset_type, env=env,
                             sn=sn, comment=comment)
            add_host.save()
            for group_list in group_id:
                g = AssetGroup.objects.get(id=group_list)
                h = Asset.objects.get(hostname=hostname)
                h.group.add(g)
            smg = u'主机%s, 添加成功' % hostname
    return my_render('upasset/add_host.html', locals(), request)


@auth_login()
def host_edit(request):
    system_types = SYSTEM_TYPE
    asset_types = ASSET_TYPE
    asset_envs = ASSET_ENV

    if request.method == 'GET':
        host_id = request.GET.get('id', False)
        host = Asset.objects.get(id=host_id)
        idc_all = IDC.objects.all()
        group = AssetGroup.objects.all()

        return my_render('upasset/host_edit.html', locals(), request)

    if request.method == "POST":
        host_id = request.POST.get('id', False)
        hostname = request.POST.get('hostname', '')
        ip = request.POST.get('ip', '')
        port = request.POST.get('port', '')
        group_id = request.POST.getlist('group', '')
        idc = request.POST.get('idc', '')
        brand = request.POST.get('brand', '')
        cpu = request.POST.get('cpu', '')
        memory = request.POST.get('memory', '')
        disk = request.POST.get('disk', '')
        system_type = request.POST.get('system_type', '')
        system_version = request.POST.get('system_version', '')
        system_arch = request.POST.get('system_arch', '')
        cabinet = request.POST.get('cabinet', '')
        number = request.POST.get('number', '')
        asset_type = request.POST.get('asset_type', '')
        env = request.POST.get('env', '')
        sn = request.POST.get('sn', '')
        comment = request.POST.get('comment', False)

        if host_id:
            Asset.objects.filter(id=host_id).update(hostname=hostname, ip=ip, port=port, idc=idc, brand=brand,
                            cpu=cpu, memory=memory, disk=disk, system_type=unicode(system_type),
                            system_version=system_version, system_arch=system_arch, cabinet=cabinet, number=number,
                            asset_type=asset_type, env=env, sn=sn, comment=comment)
            if group_id:
                g = []
                for id in group_id:
                    g.append(AssetGroup.objects.get(id=id))
                h = Asset.objects.get(id=host_id)
                h.group = g
                h.save()
            else:
                h = Asset.objects.get(id=host_id)
                h.group = ''
        return HttpResponseRedirect(reverse('asset_host'))


@auth_login()
def asset_add_idc(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        bandwidth = request.POST.get('bandwidth', '')
        linkman = request.POST.get('linkman', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        network = request.POST.get('network', '')
        operator = request.POST.get('operator', '')
        comment = request.POST.get('comment', '')
        try:
            if not name:
                emg = u'IDC机房名称不能为空'
                raise ServerError(emg)

            get_name = IDC.objects.filter(name=name)
            if get_name:
                emg = u'IDC名称不能重复'
                raise ServerError(emg)
        except ServerError:
            pass

        else:
            add_idc = IDC(name=name, bandwidth=bandwidth, linkman=linkman, phone=phone,
                          address=address, network=network, operator=operator, comment=comment)
            add_idc.save()
            smg = u'%s机房添加成功' % name
    return my_render('upasset/add_idc.html', locals(), request)


@auth_login()
def idc_edit(request):
    if request.method == "GET":
        idc_id = request.GET.get('id', False)
        idc = IDC.objects.get(id=idc_id)
        return my_render('upasset/idc_edit.html', locals(), request)

    elif request.method == "POST":
        idc_id = request.POST.get('id', '')
        name = request.POST.get('name', '')
        bandwidth = request.POST.get('bandwidth', '')
        linkman = request.POST.get('linkman', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        network = request.POST.get('network', '')
        operator = request.POST.get('operator', '')
        comment = request.POST.get('comment', '')

        if idc_id:
            IDC.objects.filter(id=idc_id).update(name=name, bandwidth=bandwidth, linkman=linkman, phone=phone,
                          address=address, network=network, operator=operator, comment=comment)
    return HttpResponseRedirect(reverse('asset_idc'))


@auth_login()
def asset_del(request):
    if request.method == "GET":
        group_id = request.GET.get('group_id', False)
        host_id = request.GET.get('host_id', False)
        idc_id = request.GET.get('idc_id', False)
        if group_id:
            AssetGroup.objects.get(id=group_id).delete()
            return HttpResponseRedirect(reverse('asset_group'))
        elif idc_id:
            IDC.objects.get(id=idc_id).delete()
            return HttpResponseRedirect(reverse('asset_idc'))
        elif host_id:
            Asset.objects.get(id=host_id).delete()
            return HttpResponseRedirect(reverse('asset_host'))

