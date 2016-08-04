# -*- coding:utf-8 -*-
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import smtplib
import copy
import xlwt
import time
import sys
from random import choice
import string
import MySQLdb
import os
import logging
sys.path.append('/ywdev/django/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ywdemo.settings")
logging.basicConfig()
from demo.models import task_content, task_info
logger = logging.getLogger('ywdemo')

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_file = os.path.join(path, 'server.ini')


class dbConfig(object):
    def __init__(self):
        config = ConfigParser()
        config.read(config_file)
        # 获取mysql配置信息
        try:
            self.dbhost = config.get('mysql', 'dbhost')
            self.dbuser = config.get('mysql', 'dbuser')
            self.port = config.get('mysql', 'dbport')
            self.dbname = config.get('mysql', 'dbname')
            self.passwd = config.get('mysql', 'passwd')

            # 获取mysql_3307配置信息
            self.dbhost_3307 = config.get('mysql_3307', 'dbhost')
            self.dbuser_3307 = config.get('mysql_3307', 'dbuser')
            self.port_3307 = config.get('mysql_3307', 'dbport')
            self.dbname_3307 = config.get('mysql_3307', 'dbname')
            self.passwd_3307 = config.get('mysql_3307', 'passwd')

            # 获取server.ini中mail信息
            self.mxsmtp = config.get('mail', 'smtp')
            self.mxuser = config.get('mail', 'user')
            self.mxpassword = config.get('mail', 'password')
            self.dirfile = config.get('mail', 'dirfile')

        except NoOptionError, e:
            logger.error(str(e))


    def slave_db(self, sql):
        sql_optimize = sql.replace("\r\n", "").replace("\r\t", "")
        try:
            conn = MySQLdb.connect(self.dbhost,
                                   self.dbuser,
                                   self.passwd,
                                   self.dbname,
                                   port=int(self.port),
                                   charset='gbk')
            cursor = conn.cursor()
            cursor.execute(sql_optimize)
            source_result = cursor.fetchall()
            conn.close()
        except MySQLdb.Error, e:
            try:
                sqlerror = "Error %d:%s" % (e.args[0], e.args[1])
                logger.error(sqlerror)
            except IndexError, e:
                logger.error("Mysql Error: %s") % str(e)
            return 'ERROR'
        return source_result

    def dev_db(self, sql):
        try:
            conn = MySQLdb.connect(self.dbhost_3307,
                                   self.dbuser_3307,
                                   self.passwd_3307,
                                   port=int(self.port_3307),
                                   charset='gbk')
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            conn.close()
        except MySQLdb.Error, e:
            try:
                sqlError = "Error %d:%s" % (e.args[0], e.args[1])
            except IndexError:
                print("Mysql Error:%s" % str(sqlError))
            return 'ERROR'
        return result


    def mailsend(self, subject, user_list, context, excelname=None):

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
            file_data = open(self.dirfile + excelname, 'rb')
            file_msg = MIMEBase(maintype, subtype)
            file_msg.set_payload(file_data.read())
            file_data.close()
            encoders.encode_base64(file_msg)
            # 附件名
            file_msg.add_header('Content-Disposition', 'attachment', filename=excelname)
            mail_msg.attach(file_msg)
        else:
            logger.info( "没有附件")
        # 发送邮件
        to_list = user_list.split(',')
        mail_msg['Subject'] = subject
        mail_msg['From'] = self.mxuser
        mail_msg['To'] = ";".join(to_list)
        fulltext = mail_msg.as_string()

        try:
            smtp = smtplib.SMTP()
            smtp.connect(self.mxsmtp)
            smtp.login(self.mxuser, self.mxpassword)
            smtp.sendmail(self.mxuser, to_list, fulltext)
            smtp.close()
            logger.info(("%s send %s messages successfully") % (to_list, excelname))
        except Exception, e:
            logger.error(str(e))


    def customexcel(self, list_dict, filename):
        """
        :param list_dict:
        list_dict: 数据库结构列表，以dict形式调用
        list_dict['result']: excel结果
        list_dict['sheetname']: excel中sheet名称
        list_dict['topline']: excel中sheet首行内容
        :param filename: excel文件名
        """
        timenow = time.strftime("%Y-%m-%d", time.localtime())
        xls = xlwt.Workbook(encoding='utf-8')

        if filename is None:
            logger.info("filename is null")

        for dict_list in list_dict:
            try:
                source_result = dict_list['result']
                excel_sheet_name = dict_list['sheetname']
                sheet_topline = dict_list['topline']
            except KeyError, e:
                logger.error(str(e))

            sheet = xls.add_sheet(excel_sheet_name)

            if source_result:
                row = 0
                text = [i for i in source_result]
                for num in text:
                    row += 1
                    cell = [i for i in num]
                    for col in range(len(cell)):
                        sheet.write(row, col, cell[col])
            else:
                logger.info("%s Database execution result is empty") % timenow

            if sheet_topline:
                cell = sheet_topline.split(',')
                for col in range(len(cell)):
                    sheet.write(0, col, cell[col])
            else:
                sheet.write(0, 0)

        excelname = filename.encode('utf-8') + "_%s.xls" % timenow
        dir_filename = self.dirfile + '%s' % excelname
        try:
            xls.save(dir_filename)
            return excelname
        except IOError, e:
            logger.error(str(e))


    def mail_send_excel(self, mail_info_list, excel_name):
        """
        :param mail_info_list: keyword args containing credentials, either:
            subject：mail的主题
            user_list: mail的用户列表
            context: mail内容
        :param excel_name: excel文件名
        """
        attachment = excel_name
        for info in mail_info_list:
            try:
                subject = info['subject']
                user_list = info['user_list']
                context = info['context']
            except NameError, e:
                logger.error(str(e))
                return False

        # print subject, user_list, context
        assert isinstance(attachment, basestring)
        self.mailsend(subject, user_list, context, excelname=attachment)


    def task_function(self, info_id):
        """
        :type info_id: django db中mytask_info表的唯一id
        """
        _dict_result = {}
        _mail_info_send = {}
        _list_dict = []
        _list_mail_info = []
        mytask_info = task_info.objects.get(only_id=info_id)

        _mail_info_send['filename'] = mytask_info.file_name
        _mail_info_send['user_list'] = mytask_info.task_email
        _mail_info_send['subject'] = mytask_info.email_subject
        _mail_info_send['context'] = mytask_info.email_context
        _mail_info_send['crontab'] = mytask_info.email_crontab
        _list_mail_info.append(copy.deepcopy(_mail_info_send))
        source_result = task_content.objects.filter(only_id=info_id)
        if not source_result:
            return False

        for i in source_result:
            sql = i.task_sql
            result = self.slave_db(sql)
            _dict_result['result'] = result
            _dict_result['sheetname'] = i.sheet_name
            _dict_result['topline'] = i.top_line
            _list_dict.append(copy.deepcopy(_dict_result))
            excel_name = self.customexcel(_list_dict, filename=_mail_info_send['filename'])
        self.mail_send_excel(_list_mail_info, excel_name)


def random_chars(length=8):
    chars = string.ascii_letters + string.digits
    return "".join([choice(chars) for i in range(length)])


#if __name__ == "__main__":
#    test = dbConfig()
#    test.task_function(info_id="RTNESJPE")
