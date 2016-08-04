# -*- coding:utf-8 -*-

from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from models import map
from django.db.models import Q
from upops.api import pagination, auth_login, my_render
import time
import os
import random
import logging
logging.basicConfig()

logger = logging.getLogger('upops_info')


# nginx配置文件路径
path = '/usr/local/nginx/conf/conf.d/'

# nginx配置文件信息
conf_content = """
    server {
        listen       %s;
        server_name  102.113.44.51;
        charset utf-8; #gbk,utf-8,gb2312,gb18030

    location / {
            proxy_pass %s;
            proxy_set_header Host $host:%s;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
    """

@auth_login()
def add_proxy_url(request):
    timenow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    port = random.randint(1001, 9999)
    username = request.GET['username']
    inner_url = request.GET['url']

    while 1:
        status_code = os.system('netstat -utlpn |grep "\<%s\>"' % str(port))
        if status_code is not '0':
            break
        port = random.randint(1001, 9999)

    ip_port = inner_url.split('/')[2]

    # 外网映射URL
    out_url = 'http://102.113.44.51:%s' % port
    file_name = os.path.join(path, '%s.conf') % (ip_port)
    if os.path.exists(file_name):
        emg = u'%s 已经存在' % os.path.basename(file_name)
        return HttpResponseRedirect(reverse('map_info')+"?emg=%s" % emg)
    else:
        file = open(file_name, 'w+')
        conf = conf_content % (port, inner_url, port)
        file.write(conf)
        file.close()

        conf_info = map(username=username, interior_url=inner_url, external_url=out_url, create_time=timenow)
        conf_info.save()
        msg = os.popen('sudo /usr/local/nginx/sbin/nginx -s reload')
        smg = u'%s 添加成功' % os.path.basename(file_name)
        logger.info(str(msg))
    return HttpResponseRedirect(reverse('map_info')+"?smg=%s" % smg)


@auth_login()
def show_proxy_url(request):
    search_content = request.GET.get('searchname', False)
    emg = request.GET.get('emg', False)
    smg = request.GET.get('smg', False)
    if search_content:
        map_list = map.objects.filter(Q(username=search_content) |
                                           Q(interior_url=search_content) |
                                           Q(external_url=search_content))
        page_switch = False
    else:
        map_list = map.objects.all()
        page_switch = True

    num = len(map_list)
    objects, page_range = pagination(request, map_list[::-1], display_amount=10)
    return my_render('upmap/upmap.html', locals(), request)


@auth_login()
def del_proxy_url(request):
    map_id = request.GET['id']
    inner_url = request.GET['url']
    ip_port = inner_url.split('/')[2]
    file_name = os.path.join(path, '%s.conf') % (ip_port)
    os.remove(file_name)
    map.objects.get(id=map_id).delete()
    msg = os.popen('sudo /usr/local/nginx/sbin/nginx -s reload')
    logger.info(str(msg))
    return HttpResponseRedirect(reverse('map_info'))

