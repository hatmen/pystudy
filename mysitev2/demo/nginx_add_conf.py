# -*- coding:utf-8 -*-
import random
from django.template import RequestContext
from django.shortcuts import render_to_response, HttpResponseRedirect
from models import mapping
from django.db.models import Q
from paginator import pagination
from views import auth_login
import time
import os

path = '/usr/local/nginx/conf/conf.d/'

def add_proxy_url(request):
    time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    port = random.randint(1001, 9999)
    username = request.GET['name']
    inner_url = request.GET['url']

    while 1:
        status_code = os.system("grep '%s' %s*" % (str(port), path))
        if status_code is not '0':
            break
        port = random.randint(1001, 9999)

    ip = inner_url.split('/')[2].split(':')[0]
    src_port = inner_url.split('/')[2].split(':')[1]
    conf_content = """ server {
        listen       %s;
        server_name  101.22.41.44;
        charset utf-8; #gbk,utf-8,gb2312,gb18030

   location / {
            proxy_pass %s;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    } """ % (port, inner_url)
    out_url = 'http://101.22.41.44:%s/' % port
    file_name = os.path.join(path, '%s_%s.conf') % (ip, src_port)
    file = open(file_name, 'w+')
    file.write(conf_content)
    file.close()
    conf_info = mapping(username=username, interior_url=inner_url, external_url=out_url, create_time=time_now)
    conf_info.save()
    os.popen('sudo /usr/local/nginx/sbin/nginx -s reload')
    return HttpResponseRedirect("/demo/urlshow/")


@auth_login
def show_proxy_url(request):
    search_content = request.GET.get('searchname', False)
    if search_content:
        mapping_list = mapping.objects.filter(Q(username=search_content) |
                                           Q(interior_url=search_content) |
                                           Q(external_url=search_content))
        status = False
    else:
        mapping_list = mapping.objects.all()
        status = True
    num = len(mapping_list)
    objects, page_range = pagination(request, mapping_list[::-1], display_amount=10)
    context = RequestContext(request,
                             {'objects': objects,
                              'page_range': page_range,
                              'num': num,
                              'page_switch': status})

    return render_to_response('under.html', context)


def del_proxy_url(request):
    mapping_id = request.GET['id']
    inner_url = request.GET['url']
    ip = inner_url.split('/')[2].split(':')[0]
    port = inner_url.split('/')[2].split(':')[1]
    file_name = os.path.join(path, '%s_%s.conf') % (ip, port)
    os.remove(file_name)
    mapping.objects.get(id=mapping_id).delete()
    os.popen('sudo /usr/local/nginx/sbin/nginx -s realod')
    return HttpResponseRedirect("/demo/urlshow/")

