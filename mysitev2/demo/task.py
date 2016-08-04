# -*- coding:utf-8 -*-
from django.http.response import HttpResponse
from django.shortcuts import RequestContext, HttpResponseRedirect, render_to_response
from models import task_info, task_content
from paginator import pagination
from dbsource import random_chars
from views import auth_login
from django.db.models import Q
import os
import time
import logging
logging.basicConfig()

logger = logging.getLogger('ywdemo')


def task_add(request):
    timenow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    onlyid = random_chars(length=8).upper()

    if request.method == 'GET':
        filename = request.GET['taskname']
        taskemial = request.GET['mailuser']
        emailsubject = request.GET['mailsubject']
        emailcontext = request.GET['mailcontext']
        taskcrontab = request.GET['tasktime']
        taskstatus = request.GET.get('checkbox', False)
        top_line_list = request.GET.getlist('toplineformat')
        sql_message_list = request.GET.getlist('sqlmessage')
        if not taskstatus:
            taskstatus = "0"

    n = 0
    for num in range(len(top_line_list)):
        n += 1
        sheetname = "sheet %d" % n
        sql_message = sql_message_list[num]
        task_sql = task_content(only_id=onlyid,
                                sheet_name=sheetname,
                                task_sql=sql_message,
                                top_line=top_line_list[num],
                                create_time=timenow)
        task_sql.save()

        info_context = task_info(only_id=onlyid,
                                 file_name=filename,
                                 task_email=taskemial,
                                 email_subject=emailsubject,
                                 email_context=emailcontext,
                                 email_crontab=taskcrontab,
                                 task_status=taskstatus,
                                 create_time=timenow)
        info_context.save()
    return HttpResponseRedirect('/demo/taskshow/')


@auth_login
def task_show(request):
    on_num = 0
    off_num = 0
    proce = os.system('ps -ef|grep -v "grep" |grep "runtask.py"')
    print proce
    if proce == 0:
        task_status = True
    else:
        task_status = False

    search_content = request.GET.get('search', False)
    if search_content:
        task_list = task_info.objects.filter(Q(file_name=search_content) |
                                             Q(email_crontab=search_content))
        for list in task_list:
            if list.task_status == 1:
                on_num += 1
            else:
                off_num += 1
        status = False
    else:
        task_list = task_info.objects.all()
        status = True
        on_num = len(task_info.objects.filter(task_status=1))
        off_num = len(task_info.objects.filter(task_status=0))

    objects, page_range = pagination(request, task_list)
    context = RequestContext(request,
                             {'objects': objects[::-1],
                              'page_range': page_range,
                              'on_num': on_num,
                              'off_num': off_num,
                              'page_switch': status,
                              'task_status': task_status})
    return render_to_response('task.html', context)


@auth_login
def task_check(request):
    if request.GET['id']:
        onlyid = request.GET['id']

    task_info_context = task_info.objects.get(only_id=onlyid)
    task_sql = task_content.objects.filter(only_id=onlyid)

    if task_info_context.task_status == 1:
        status = True
    else:
        status = False
    c = RequestContext(request, {'task_info': task_info_context, 'task_sql_list': task_sql, 'status': status})
    return render_to_response('taskupdate.html', c)


def task_update(request):
    timenow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    if request.method == 'GET':
        onlyid = request.GET['task_id']
        taskname = request.GET['taskname']
        emailuser = request.GET['mailuser']
        emailsubject = request.GET['mailsubject']
        emailcontext = request.GET['mailcontext']
        taskcrontab = request.GET['tasktime']
        taskstatus = request.GET.get('checkbox', False)
        id_list = request.GET.getlist('crontab_id')
        topline_list = request.GET.getlist('toplineformat')
        sql_message_list = request.GET.getlist('sqlmessage')
        task_info.objects.filter(only_id=onlyid).update(file_name=taskname,
                                                     task_email=emailuser,
                                                     email_subject=emailsubject,
                                                     email_context =emailcontext,
                                                     email_crontab=taskcrontab,
                                                     task_status=taskstatus,
                                                     create_time=timenow)

        for num in range(len(id_list)):
            sql_replace = sql_message_list[num]
            task_content.objects.filter(id=id_list[num]).update(task_sql=sql_replace,
                                                             top_line=topline_list[num],
                                                             create_time=timenow)
    return HttpResponseRedirect('/demo/taskshow/')


def task_del(request):
    if request.GET['id']:
        onlyid = request.GET['id']

    task_info.objects.get(only_id=onlyid).delete()
    task_content.objects.filter(only_id=onlyid).delete()
    return HttpResponseRedirect('/demo/taskshow/')


def task_start(request):
    pid = '/tmp/runtask.pid'
    path = os.path.dirname(__file__)
    if os.path.exists(pid):
        os.system('/usr/bin/python %s/runtask.py restart' % path)
        logger.info('runtask restart...')
    else:
        os.system('/usr/bin/python %s/runtask.py start' % path)
        logger.info('runtask start...')

    return HttpResponseRedirect('/demo/taskshow/')
