# -*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
import os
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from signal import SIGTERM
sys.path.append('/ywdev/django/ywdemo/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ywdemo.settings")
from dbsource import dbConfig
from demo.models import task_info

class Daemon:

    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
          # 需要获取调试信息，改为stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'，以root身份运行。
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile


    def _daemonize(self):
        try:
            pid = os.fork()    # 第一次fork，生成子进程，脱离父进程
            if pid > 0:
                sys.exit(0)      # 退出主进程
        except OSError, e:
            sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")      # 修改工作目录
        os.setsid()        # 设置新的会话连接
        os.umask(0)        # 重新设置文件创建权限

        try:
            pid = os.fork() # 第二次fork，禁止进程打开终端
            if pid > 0:
              sys.exit(0)
        except OSError, e:
            sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        # 重定向文件描述符
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # 注册退出函数，根据文件pid判断是否存在进程
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write('%s\n' % pid)


    def delpid(self):
        os.remove(self.pidfile)


    def start(self):
        # 检查pid文件是否存在以探测是否存在进程
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = 'pidfile %s already exist. Daemon already running!\n'
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # 启动监控
        self._daemonize()
        self._task_function()


    def stop(self):
        # 从pid文件中获取pid
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:   # 重启不报错
            message = 'pidfile %s does not exist. Daemon not running!\n'
            sys.stderr.write(message % self.pidfile)
            return

        # 杀进程
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
        if err.find('No such process') > 0:
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
        else:
            print str(err)
            sys.exit(1)


    def restart(self):
        self.stop()
        self.start()


    def _task_function(self):
        """ run your fun"""
        sched = BackgroundScheduler()
        task = dbConfig()
        task_list = task_info.objects.filter(task_status=1)
        for task_cron in task_list:
            time_quantum = task_cron.email_crontab.split()
            minute = time_quantum[0]
            hour = time_quantum[1]
            day = time_quantum[2]
            month = time_quantum[3]
            day_of_week = time_quantum[4]
            info_id = task_cron.only_id
            sched.add_job(task.task_function, 'cron', minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week, args=[info_id])
        sched.start()
        while True:
            time.sleep(1)


if __name__ == '__main__':
    daemon = Daemon('/tmp/runtask.pid', stdout = '/tmp/ywdemo.log', stderr = '/tmp/ywdemo.log')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print 'unknown command'
            sys.exit(2)
        sys.exit(0)
    else:
        print 'usage: %s start|stop|restart' % sys.argv[0]
        sys.exit(2)
