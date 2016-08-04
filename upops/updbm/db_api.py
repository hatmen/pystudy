# -*- coding:utf-8 -*-

from upops.api import *
from models import *
import MySQLdb
import os
import threading
import logging

logging.basicConfig()
loginfo = logging.getLogger('upops_info')
logerror = logging.getLogger(('upops_error'))


# 测试库导入的数据路径 192.168.1.112下路径
backup_tables_list = '/backup/'

# slave database的数据库
dbname_list = ['czyb', 'czyb_pay', 'czyb_usercenter', 'youcai']

# 选择slave权限视图
def choice_db_views(db_name):
    if db_name == "czyb":
        proxy_user = "xs_v@'%'"
        return proxy_user
    elif db_name == "czyb_pay":
        proxy_user = "pay_v@'%'"
        return proxy_user
    elif db_name == "czyb_usercenter":
        proxy_user = "uc_v@'%'"
        return proxy_user
    elif db_name == "youcai":
        proxy_user = "youcai_v@'%'"
        return proxy_user


class dbSource(object):
    def __init__(self):
        pass

    def slave_db(self, sql):
        sql_optimize = sql.replace("\r\n", "").replace("\r\t", "")
        try:
            conn = MySQLdb.connect(DB_HOST,
                                   DB_USER,
                                   DB_PASSWD,
                                   DB_NAME,
                                   port=int(DB_PORT),
                                   charset='gbk')
            cursor = conn.cursor()
            cursor.execute(sql_optimize)
            source_result = cursor.fetchall()
            conn.close()

        except MySQLdb.Error, e:
            sqlerror = "ssError %d:%s" % (e.args[0], e.args[1])
            loginfo.info(sqlerror)
            return False
        
        return source_result

    def dev_db(self, sql):
        try:
            conn = MySQLdb.connect(DB_HOST_3307,
                                   DB_USER_3307,
                                   DB_PASSWD_3307,
                                   port=int(DB_PORT_3307),
                                   charset='gbk')
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            conn.close()
        except MySQLdb.Error, e:
            try:
                sqlError = "Error %d:%s" % (e.args[0], e.args[1])
                loginfo.info(sqlError)
            except IndexError:
                loginfo.info("Mysql Error:%s" % str(sqlError))
            return False
	return result


# 赋权方法
def db_authorization(username, ip, passwd, db_name):
    db = dbSource()
    #source_sql = "show grants for '%s'@'%s'" % (username, ip)
    source_sql = "select user, host from mysql.user where user='%s' and host='%s'" % (username, ip)
    if db_name in dbname_list:
        result = db.slave_db(source_sql)
    else:
        result = db.dev_db(source_sql)

    # 判断用户是否在数据库存在访问权限
    if result:
        if db_name in dbname_list:
            privilege_sql = "grant select on %s.* to '%s'@'%s'" % (db_name, username, ip)
            # 从库脱敏
            #proxy_user = choice_db_views(db_name)
            #privilege_sql = "grant proxy on %s to '%s'@'%s'" % (proxy_user, username, ip)

            db.slave_db(privilege_sql)
            loginfo.info(u'[ %s@%s ] 数据库授权成功' % (username, ip))
        else:
            privilege_sql = "grant SELECT, " \
                        "INSERT, " \
                        "UPDATE, " \
                        "DELETE, " \
                        "DROP, " \
                        "CREATE, " \
                        "INDEX, " \
                        "ALTER, " \
                        "LOCK TABLES " \
                        "ON %s.* to '%s'@'%s'" % (db_name, username, ip)
            db.dev_db(privilege_sql)

    # 没有访问权限，即添加用户权限
    else:
        if db_name in dbname_list:
            create_user_sql = "create user '%s'@'%s' identified by '%s'" % (username, ip, passwd)
            privilege_sql = "grant select on %s.* to '%s'@'%s'" % (db_name, username, ip)
            result = db.slave_db(create_user_sql)
            if result == ():
                #proxy_user = choice_db_views(db_name)
                #privilege_sql = "grant proxy on %s to '%s'@'%s'" % (proxy_user, username, ip)
                db.slave_db(privilege_sql)
                loginfo.info(u'[ %s@%s ] 数据库授权成功' % (username, ip))
            else:
                loginfo.info(u'[ %s@%s ] 数据库授权失败' % (username, ip))
            return
        else:
            privilege_sql = "grant SELECT, " \
                        "INSERT, " \
                        "UPDATE," \
                        " DELETE, " \
                        "DROP, " \
                        "CREATE, " \
                        "INDEX, " \
                        "ALTER, " \
                        "LOCK TABLES " \
                        "ON %s.* to '%s'@'%s' identified by '%s'" % (db_name, username, ip, passwd)
            db.dev_db(privilege_sql)


def add_db_user(**kwargs):
    # 判断用户是否已存在
    name = kwargs.pop('name').strip()
    email = kwargs.pop('email').strip()
    comment = kwargs.pop('comment')
    status = kwargs.pop('status')
    passwd = random_chars(length=10)
    if name and email:
        try:
            user_info = UpUser.objects.get(name=name)
        except UpUser.DoesNotExist:
            subject = u'恭喜您数据库平台注册成功'
            content = u"""
            %s：您好！
                您的用户名：%s
                您的密码：%s
                您的邮箱：%s
                说明：
                线下数据库从库 服务器：127.0.0.1 数据库端口：3306
                用户名与密码为链接数据库的凭证，请妥善保管！
                """ % (name, name, passwd, email)
            smg = mail_send(subject, email, content, file_dir=None)
            if smg == "success":
                db_user = UpUser(name=name, email=email, password=passwd, comment=comment, role=status)
                db_user.save()
            else:
                smg = "error"
            return smg
        else:
            if user_info.role == 2:
                return "forbidden"
            return 'ok'


class DB_Counter(object):
    def __init__(self, table_sum):
        self.lock = threading.Lock()
        self.value = 0
        self.table_sum = table_sum

    def increment(self, id):
        self.lock.acquire()

        try:
            self.value = self.value + 1
            a = "%d" % int(self.value)
            b = "%d" % int(self.table_sum)
            result = int(a)*100/int(b)
            a = DbImportTest.objects.get(id=id)
            if result == 1:
                a.status = 1
            a.counter = result
            a.save()
            pass
        finally:
            self.lock.release()


def db_import_test(c, **kwargs):
    time.sleep(10)
    username = kwargs['username']
    host = kwargs['host']
    port = kwargs['port']
    dbname = kwargs['dbname']
    tables_list = kwargs['tables']
    id = kwargs['db_id']
    for table in tables_list:
        loginfo.info("gunzip -f < %s | /usr/bin/mysql -h%s -u%s -P%s %s" % (table, host, username, port, dbname))
        bash("ssh -p55555 root@%s '/bin/gunzip -f < %s | /usr/bin/mysql -h127.0.0.1 -uroot -P%s %s'" % (host, table, port, dbname))
        c.increment(id)


def db_cut_tables(tables=[''], num=None):
    tables_num = len(tables)
    new_tables_list = []
    if num > tables_num:
        raise ServerError
    else:
        list_place = range(tables_num)[::5]
        e = list_place[-1::][0]
        s = 0
        for i in list_place:
            new_tables_list.append(tables[s:i])
            s = i
        if e < tables_num:
            new_tables_list.append(tables[e:tables_num])
    return new_tables_list


def db_backup_tables(table_sum=0, host='192.168.1.112', db_id=None, username='root', port="3306", dbname='czyb', tables=None, num=5, date_path=None):
    counter = DB_Counter(table_sum=table_sum,)
    tables_list = db_cut_tables(tables=tables, num=num)
    for t_list in tables_list:
        if t_list:
            t = threading.Thread(target=db_import_test, args=(counter,),
                                 kwargs={"username": username,
                                         "host": host,
                                         "port": port,
                                         "dbname": dbname,
                                         "tables": t_list,
                                         "db_id": db_id})
            t.setDaemon(True)
            t.start()



def db_myloader_tables(host='192.168.1.112', db_id=None, thread_sum=4, username='root', port="3306", dbname='czyb', path=None):
    cmd = '/usr/local/bin/myloader -o --threads %s -B %s -P %s -u %s -h 127.0.0.1 -d %s && echo 0' % (thread_sum, dbname, port, username, path)
    loginfo.info(u"开始导入测试库....") 
    try:
        msg = bash('ssh -p55555 root@%s "%s"' % (host, cmd))
        desction = db_desensitization(dbname=dbname, port=port)
        raise ServerError
    except ServerError:
        a = DbImportTest.objects.get(id=db_id)
        loginfo.info(u"测试数据库导入完成")
        if msg == 0 and desction:
            a.status = 1
        else:
            a.status = 2
            loginfo.info(u'测试数据库导入失败')
        a.save()
        return False

    #if msg == 0:
    #    a.counter = 1
    #    a.save()
    #    return True
    #else:
    #    a.counter = 2
    #    a.save()
    #    return False

def backup_list(path_dir=backup_tables_list):
    msg = []
    cmd = '/usr/bin/ls %s' % path_dir
    a = subprocess.Popen('ssh -p55555 root@192.168.1.112 "%s"' % cmd, stdout=subprocess.PIPE, shell=True)
    b = a.stdout.readlines()
    if b:
        for x in b:
            msg.append(x.strip('\n'))
        loginfo.info('192.168.1.112:%s %s' % (path_dir, msg))
        return msg
    else:
        return False


def db_desensitization(host='192.168.1.112', db_user='upops', port='3306', dbpass='6dMwLZAY', dbname='czyb'):
    sql_user = "update czyb.user set email=concat(id,'@xx.com') where email is not null"
    sql_user_mobile ="update czyb.user set mobile=19000000000+id where mobile is not null"
    sql_user_info = "update czyb.user_info set real_name=user_id,id_card=user_id"
    sql_idcard_info = "update czyb.idcard_info set idno=user_id,name=user_id"
    try:
        conn = MySQLdb.connect(host,
                               db_user,
                               dbpass,
                               dbname,
                               port=int(port),
                               charset='gbk')
        cursor = conn.cursor()
        sql_list = [sql_user, sql_user_mobile, sql_user_info, sql_idcard_info]
        for sql in sql_list:
            cursor.execute(sql)
            #source_result = cursor.fetchall()
        conn.commit()
        conn.close()
    except MySQLdb.Error, e:
        try:
            sqlError = "Error %d:%s" % (e.args[0], e.args[1])
            loginfo.info(sqlError)
        except IndexError:
            loginfo.info('Mysql Error: %s' % str(sqlError))
        return False
    loginfo.info(u'测试库脱敏成功')
    return True

