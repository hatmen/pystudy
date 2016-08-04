# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from datetime import datetime
from email import encoders
from email.MIMEBase import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import xlwt
import MySQLdb
import logging
import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PID_DIR = os.path.join(BASE_DIR,'mytask.pid')
LOG_DIR = os.path.join(BASE_DIR,'mytask.log')
INI_DIR = os.path.join(BASE_DIR,'server.ini')

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a,%d %b %Y %H:%M:%S',
                filename=LOG_DIR,
                filemode='a')


class timedTask(object):
 
    def __init__(self):
        config=ConfigParser()
        config.read(INI_DIR)
        # 获取mysql配置信息
        self.dbhost = config.get('mysql','dbhost')
        self.dbuser = config.get('mysql','dbuser')
        self.dbport = config.get('mysql','dbport')
        self.dbname = config.get('mysql','dbname')
        self.passwd = config.get('mysql','passwd')
        # 获取mail配置信息
        self.mailhost = config.get('mail','mail_host')
        self.mailuser = config.get('mail','mail_user')
        self.mailpass = config.get('mail','mail_pass')
        self.mailautt = config.get('mail','mail_autt')
        
    # 执行sql，返回结果
    def sqlDB(self,sql):      
        resql = sql.replace("\r\n"," ").replace("\r\t"," ")
        try:
            conn = MySQLdb.connect(self.dbhost,self.dbuser,self.passwd,self.dbname,port=int(self.dbport),charset='utf8')
            cursor = conn.cursor()
            cursor.execute(resql)
            result = cursor.fetchall()
            conn.close()
            return result
        except MySQLdb.Error,e:
            try:
                sqlError = "Error %d:%s" % (e.args[0],e.args[1])
            except IndexError:
                print("MySQL Error:%s" % str(e))
    
    # 实例化xls，并填充sql结果
    def xlsSheet(self,result,sheetname,top_line):
        
        xls = xlwt.Workbook(encoding='utf-8')
        sheet = xls.add_sheet("sheet 1")
        if result:
            for row in range(len(result)):
                x = 0
                y = 0
                numcol = len(result[row])
                while x < numcol:
                    sheet.write(row+1,y,result[row][x])
                    x += 1
                    y += 1
        else:
            print("%s %s is NOLL" % (datetime.now(),sheetname.encode('utf-8')))
        
        # 填充xls首行内容
        if top_line:
            topline = top_line.split(',')
            for n in range(len(topline)):
                if n < len(topline):
                    sheet.write(0,n,topline[n])
        else:
            sheet.write(0,0)
            
        # xls保存路径，及命名
        t = datetime.now()
        xlsname = sheetname.encode('utf-8') + "%s.xls" % t.strftime('%Y-%m-%d')
        auttname = self.mailautt + "%s" % xlsname
        xls.save(auttname)
        return xlsname
    
    # 邮件发送
    def mailSend(self,user_list,sub,content,filename):
        # 创建MIMEMultipart实例
        mail_msg = MIMEMultipart()
        # 创建邮件内容实例
        text_msg = MIMEText(content,_charset='utf-8')
        mail_msg.attach(text_msg)
        # 构建MIMEBase对象作为文本附件并附加到邮件中
        contype = 'application/octet-stream'
        maintype,subtype = contype.split('/',1)
        # 读入文件内容并格式化
        data =  open(self.mailautt + filename,"rb")
        file_msg = MIMEBase(maintype,subtype)
        file_msg.set_payload(data.read())
        data.close()
        encoders.encode_base64(file_msg)   
        to_list = user_list.split(',')
        # 附件名
        file_msg.add_header('Content-Disposition','attachment',filename = filename)
        mail_msg.attach(file_msg)
        # 发送邮件
        mail_msg['Subject'] = sub               #主题
        mail_msg['From'] = self.mailuser        #发送人
        mail_msg['To'] = ";".join(to_list)      #收件人    
        fullText = mail_msg.as_string()
        
        #链接mail server
        try:
            smtp = smtplib.SMTP()
            smtp.connect(self.mailhost)
            smtp.login(self.mailuser,self.mailpass)
            smtp.sendmail(self.mailuser,to_list,fullText)
            smtp.close()
            print('%s send mail %s to %s sucess' % (datetime.now(),to_list,filename))
            return True
        except Exception,e:
            print str(e)
            return False

class TaskPid(object):

    def createPID(self,pid):
        pid = str(pid)
        fpid = open(PID_DIR,'w')
        fpid.write(pid)
        fpid.close()

    def judPid(self,pid):

        taskpid = TaskPid()

        if os.path.exists(PID_DIR):
            fpid = open(PID_DIR)
            oldpid = fpid.read()
            if not oldpid == pid:
                os.system('kill -9 %s' % oldpid)
                taskpid.createPID(pid)
            else:
                pass
        else:
            taskpid.createPID(pid)
