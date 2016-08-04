# -*- coding:utf-8 -*-

import pexpect
import logging

logging.basicConfig()
loginfo = logging.getLogger('upops_info')
logerror = logging.getLogger(('upops_error'))

def copy_keys(username='root', port=22, host='127.0.0.1', password=None):
    cmd = "ssh-copy-id -i /root/.ssh/id_rsa.pub '-p %s %s@%s'" % (port, username, host)
    msg = "Are you sure you want to continue connecting (yes/no)?"
    child = pexpect.spawn(cmd)
    index = child.expect([pexpect.TIMEOUT, msg, 'password:'])
    if index == 0:
       loginfo.info(cmd + " " + "Timeout!!")
       return False
    elif index == 1:
        child.sendline('yes')
        i = child.expect([pexpect.TIMEOUT, 'password:'])
        if i == 0:
            loginfo.info("ssh-copy-id %s@%s input password is timeout" % (username, host))
            return False
        else:
            child.sendline(password)
            loginfo.info("%s@%s copy keys is success" % (username, host))
            return True
    elif index == 2:
        child.sendline(password)
        loginfo.info("%s@%s copy keys is success" % (username, host))
        return True

    child.expect(pexpect.EOF)
    loginfo.info(child.before)
    child.close()



