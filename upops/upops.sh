#!/bin/bash
#
#
# chkconfig: - 85 12
# description: Open source detecting system
# processname: upops
# Date: 2016-04-20
# Version: 3.0.1
# Site: http://www.czyb360.com

export PAHT=/usr/local/sbin:/usr/local/bin:/bin:/usr/sbin:/usr/bin

. /etc/init.d/functions

lockfile=/var/lock/subsys/upops

function start() {
    upops_start=$"Staring upops service:"
    if [ -f $lockfile ];then
        echo -n "upops is running...."
        success "$upops_start"
        echo
    else
        python ./manage.py crontab add >> /var/log/upops.log
        python ./manage.py runserver 0.0.0.0:8088 >> /var/log/upops.log 2>&1 &
        sleep 1
        echo -n "$upops_start"
        ps aux|grep 'manage.py runserver 0.0.0.0:8088'|grep -v 'grep' &> /dev/null
        if [ $? == '0' ];then
            success "$upops_statr"
            if [ ! -e $lockfile ];then
                lockfile_dir=`dirname $lockfile`
                mkdir -pv $lockfile_dir
            fi
            touch "$lockfile_dir"
            echo
        else
            failure "$upops_start"
            echo
        fi
    fi
}

function stop() {
    echo -n $"Stoping upops service:"
    python ./manage.py crontab remove >> /var/log/upops.log
    ps aux|grep -E "manage.py runserver 0.0.0.0:8088"|grep -v "grep"|awk '{print $2}'|xargs kill -9 &> /dev/null
    ret=$?
    if [ $ret -eq 0 ];then
        echo_success
        echo
        rm -f $"lockfile"
    else
        echo_failure
        echo
        rm -f $"lockfile"
    fi
}

function status() {
    ps aux|grep "manage.py runserver 0.0.0.0:8088"|grep -v "grep" &> /dev/null
    if [ $? == 0 ];then
        echo -n "upops is running...."
        success
        touch "$lockfile"
        echo
    else
        echo -n "upops is not running...."
        failure
        echo
    fi
}

restart() {
    stop
    start
}

case "$1" in
start)
    start
    ;;
stop)
    stop
    ;;
status)
    status
    ;;
restart)
    stop
    start
    ;;
*)
    echo $"Usage: $0 {start|stop|status|restart}"
    exit 2
    ;;
esac
