# -*- coding:utf-8 -*-

from upops.models import User

SUBJECT = u'欢迎注册UPOPS平台'
CONTEXT = u"""
    %s：您好，
        欢迎注册UPOPS平台，以下为您的个人信息！
        您的登录用户名：%s
        您的登录密码：%s
        您的邮箱：%s
        说明：登录UPOPS平台后，请及时修改密码！
        UPOPS: http://127.0.0.1:8088/
    """

def add_user(access_url, **kwargs):
    user = User(**kwargs)
    user.set_password(kwargs.get('password'))
    user.save()
    for url_id in access_url:
        user.url.add(url_id)
    return user


def del_user(username):
    user = User.objects.get(username=username)
    if user:
        user.delete()
        return True
    else:
        emg = u"%s 不存在" % username
        return False


def update_user(access_url, **kwargs):
    username = kwargs.pop("username", False)
    password = kwargs.pop('password', '')
    if username:
        user = User.objects.filter(username=username)
        if user:
            user.update(**kwargs)
            # user.url.clean()
            user_url = User.objects.get(username=username)
            for i in access_url:
                user_url.url.add(i)
            if password.strip():
                user_get = user[0]
                user_get.set_password(password)
                user_get.save()
            else:
                emg =  u"密码为空"
                pass
        else:
            emg = u"%s 不存在" % user.username
            return False


