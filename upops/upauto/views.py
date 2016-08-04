# -*- coding:utf-8 -*-

from django.shortcuts import render, HttpResponseRedirect
from django.core.urlresolvers import reverse
from upops.api import *
from models import *
import logging
from ansible_api import *

logging.basicConfig()
loginfo = logging.getLogger('upops_info')
logerror = logging.getLogger(('upops_error'))


@auth_login()
def trust_host(request):
    page_name = u'主机互信'
    host_all = TrustHost.objects.all()
    objects, page_range = pagination(request, host_all)
    host_dict = {}
    host_list = []
    if request.method == "POST":
        host = request.POST.getlist('ip', False)
        user = request.POST.getlist('user', False)
        port = request.POST.getlist('port', False)
        password = request.POST.getlist('password', False)

        for x in range(len(host)):
            host_dict['hostname'] = host[x]
            host_dict['port'] = port[x]
            host_dict['username'] = user[x]
            host_dict['password'] = password[x]
            host_list.append(host_dict)

            trust = TrustHost(ip=host[x], port=port[x], user=user[x])
            trust.save()

        pkey = PushKey(host_list)
        meg = pkey.push_key('root', '/root/.ssh/id_rsa.pub')
        loginfo.info(meg)

    return my_render('upauto/trust_host.html', locals(), request)


@auth_login()
def install_soft(request):
    page_name = u'软件安装'
    host_all = TrustHost.objects.all()
    objects, page_range = pagination(request, host_all)
    if request.method == "POST":
        host_id = request.POST.getlist('host', False)
        softname = request.POST.get('soft', False)
        checkbox = request.POST.getlist('checkbox', False)
        if host_id and softname:
            if checkbox:
                for id in host_id:
                    for name in checkbox:
                        pass
                        if not AutoProject.objects.get(project_name=name):
                            project = AutoProject(project_name=name)
                            project.save()
                        project = AutoProject.objects.get(project_name=name)
                        trust = TrustHost.objects.get(id=host_id)
                        trust.autoproject_set.add(project)
        else:
            pass
    return my_render('upauto/install_soft.html', locals(), request)


@auth_login()
def install_tomcat(request):
    page_name = u'部署Tomcat'
    host_all = TrustHost.objects.all()
    objects, page_range = pagination(request, host_all)
    if request.method == "POST":
        host_id = request.POST.getlist('host', False)
        tomcat_name = request.POST.get('name', False)
        webapps_path = request.POST.get('webapp', False)
        logs_path = request.POST.get('log', False)
        web_port = request.POST.get('web_port', False)
        shutdown_port = request.POST.get('shutdown_port', False)
        redirect_port = request.POST.get('redirect_port', False)

        if AutoProject.objects.get(project_name=tomcat_name):
            pass
        else:
            project = AutoProject(project_name=tomcat_name)
            project.save()

        for trust_host_id in host_id:
            try:
                project = AutoProject.objects.get(project_name=tomcat_name)
                trust = TrustHost.objects.get(id=trust_host_id)
                trust.autoproject_set.add(project)
            except Exception, e:
                logerror.error(e)
    return my_render('upauto/install_tomcat.html', locals(), request)

