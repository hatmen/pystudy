# -*- coding:utf-8 -*-

from ConfigParser import ConfigParser
from ConfigParser import NoOptionError
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.template import RequestContext
from django.shortcuts import render_to_response, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from random import choice
import string
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import smtplib
import time
import os
import re
import subprocess
from django.contrib.auth import logout

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upops.settings')
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_file = os.path.join(path, 'server.conf')

config = ConfigParser()
config.read(config_file)

# 获取mysql配置信息
DB_HOST = config.get('mysql', 'dbhost')
DB_USER = config.get('mysql', 'dbuser')
DB_PORT = config.get('mysql', 'dbport')
DB_NAME = config.get('mysql', 'dbname')
DB_PASSWD = config.get('mysql', 'passwd')

# 获取mysql_3307配置信息
DB_HOST_3307 = config.get('mysql_3307', 'dbhost')
DB_USER_3307 = config.get('mysql_3307', 'dbuser')
DB_PORT_3307 = config.get('mysql_3307', 'dbport')
DB_NAME_3307 = config.get('mysql_3307', 'dbname')
DB_PASSWD_3307 = config.get('mysql_3307', 'passwd')

# 获取mail信息
MXSMTP = config.get('mail', 'smtp')
MXUSER = config.get('mail', 'user')
MXPASSWORD = config.get('mail', 'password')

# 获取文件保存路径
MAIL_FILE = config.get('file_path', 'mail_file')


# 随机数
def random_chars(length=8):
    chars = string.ascii_letters + string.digits
    return "".join([choice(chars) for i in range(length)])


# 邮件发送,可带附件
def mail_send(subject, user_list, context, excelname=None, file_dir=MAIL_FILE):
    """
    :type subject: 邮件主题
    :type user_list: 收件人列表，多个以","分割
    :type context: 邮件内容
    :type excelname: 附件名称

    """
    timenow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # 创建MIMEMutipart实例
    mail_msg = MIMEMultipart()
    # 创建邮件内容实例
    mail_text = MIMEText(context, _charset="utf-8")
    mail_msg.attach(mail_text)
    # 创建MIMEBase对象作为文本附件
    contype = 'application/octet-stream'
    maintype, subtype = contype.split("/", 1)
    # 以二进制形式将附件添加到邮件中
    if excelname is not None:
        file_data = open(file_dir + excelname, 'rb')
        file_msg = MIMEBase(maintype, subtype)
        file_msg.set_payload(file_data.read())
        file_data.close()
        encoders.encode_base64(file_msg)
        # 附件名
        file_msg.add_header('Content-Disposition', 'attachment', filename=excelname)
        mail_msg.attach(file_msg)
    else:
        pass
    # 发送邮件
    to_list = user_list.split(',')
    mail_msg['Subject'] = subject
    mail_msg['From'] = MXUSER
    mail_msg['To'] = ";".join(to_list)
    fulltext = mail_msg.as_string()

    try:
        smtp = smtplib.SMTP()
        smtp.connect(MXSMTP)
        smtp.login(MXUSER, MXPASSWORD)
        smtp.sendmail(MXUSER, to_list, fulltext)
        smtp.close()
        print "%s send %s messages successfully" % (to_list, excelname)
        return "success"
    except Exception, e:
        print "ERROR: %s" % str(e)
        return "error"


# 分页器
def pagination(request, queryset, display_amount=15, after_range_num=5, bevor_range_num=4):
    # 按参数分页
    paginator = Paginator(queryset, display_amount)
    try:
        # 得到request中的page参数
        page = int(request.GET['page'])
    except:
        # 默认为1
        page = 1
    try:
        # 尝试获得分页列表
        objects = paginator.page(page)
    # 如果页数不存在
    except EmptyPage:
        # 获得最后一页
        objects = paginator.page(paginator.num_pages)
    # 如果不是一个整数
    except:
        # 获得第一页
        objects = paginator.page(1)
    # 根据参数配置导航显示范围
    if page >= after_range_num:
        page_range = paginator.page_range[page-after_range_num:page+bevor_range_num]
    else:
        page_range = paginator.page_range[0:page+bevor_range_num]
    return objects, page_range


def my_render(template, data, request):
    return render_to_response(template, data, context_instance=RequestContext(request))


def auth_login(url_list_num=3):
    def __deco(func):
        def _deco(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('admin_login'))
            username = request.session.get('username')
            if username:
                if username == "admin":
                    ret = func(request, *args, **kwargs)
                    return ret
                else:
                    path_url = ""
                    for i in range(url_list_num):
                        path_url = path_url + request.path.split('/')[i] + "/"
                    access_url = request.session.get('access_url')
                    if path_url in access_url:
                        ret = func(request, *args, **kwargs)
                        return ret
                    else:
                        del request.session['username']
                        logout(request)
                        raise Http404()

        return _deco
    return __deco


class ServerError(Exception):
    """
    self define exception
    自定义异常
    """
    pass


def bash(cmd):
    """
    run a bash shell command
    执行bash命令
    """
    return subprocess.call(cmd, shell=True)

