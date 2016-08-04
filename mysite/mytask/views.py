# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.db import connection
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerAlreadyRunningError
from crontabs import timedTask,TaskPid
from datetime import datetime
from apscheduler import events
import logging
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
LOG_DIR = os.path.join(BASE_DIR,'mytask.log')

sched = BackgroundScheduler()

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a,%d %b %Y %H:%M:%S',
                filename=LOG_DIR,
                filemode='a')

def err_listener(ev):  
    err_logger = logging.getLogger('schedErrJob')  
    if ev.exception:  
        err_logger.exception('%s error.', str(ev.job))  
    else:  
        err_logger.info('%s miss', str(ev.job))

# 创建xls文件,并完成邮件发送
def makexls(tasksql,sheetname,topline,to_list,sub,context):
    crontab = timedTask()
    result = crontab.sqlDB(tasksql)
    auttname = crontab.xlsSheet(result,sheetname,top_line=topline)
    crontab.mailSend(to_list,sub,context,auttname)

# 分割sql结果,并通过apscheduler创建job
def select(djresult):

    lines = len(djresult)
    for line in range(lines):
        xlsname = djresult[line][1] 
        topline = djresult[line][2]
        tasksql = djresult[line][3]
        emailuser = djresult[line][4]
        emailsub = djresult[line][5]
        emailcon = djresult[line][6]
        crontime = djresult[line][7]
        interstat = djresult[line][8]

        cron_time = crontime.split()  
	
        if interstat == 1:
            sched.add_job(makexls,'cron',minute=cron_time[0],hour=cron_time[1],day=cron_time[2],month=cron_time[3],day_of_week=cron_time[4],args=[tasksql,xlsname,topline,emailuser,emailsub,emailcon])
            sched.add_listener(err_listener,events.EVENT_JOB_ERROR | events.EVENT_JOB_MISSED) 

# url触发执行
def taskStart(req):
    djcursor = connection.cursor()
    djcursor.execute("select * from mytask_task")
    djresult = djcursor.fetchall()
    djcursor.close()

    # 判断pid,实现独立进程执行  
    cropid = TaskPid() 
    pid = os.getpid()
    cropid.judPid(pid)    

    if sched.get_jobs():
        sched.remove_all_jobs()
#        print('%s task is restart' % datetime.now())
        select(djresult)
        return HttpResponse("<h1> %s task update is ok! (^-^) </h1>" % datetime.now())
    
    else:
#        print('%s task is start running' % datetime.now())
        select(djresult)
        try:
            sched.start()
        except  SchedulerAlreadyRunningError:
#           print("%s task is running" % datetime.now())
            pass
    return HttpResponse('<h1> %s task is start running (^-^)! </h1>' % datetime.now())
