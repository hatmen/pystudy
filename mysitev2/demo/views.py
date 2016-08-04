# -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, Http404, HttpResponseRedirect
from django.template import RequestContext, Context, loader
from django.contrib.auth import authenticate
from django.contrib.auth import login
# Create your views here.

def index(request):
    return render_to_response('index.html')


def user_login(request):
    if request.method == "GET":
        context = RequestContext(request)
        return render_to_response('login.html', context)
    else:
        if request.method == "POST":
            global username, password
            username = request.POST.get('username')
            password = request.POST.get('password')

    if username and password:
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            request.session['username'] = username
            login(request, user)
            # context = RequestContext(request, {'username': username})
            return HttpResponseRedirect('/demo/commurl/')
        else:
            context = RequestContext(request, {'user_is_wrong': True})
            return render_to_response('login.html', context)
    else:
        context = RequestContext(request)
        return render_to_response('login.html', context)


def user_logout(request):
    del request.session['username']
    context = RequestContext(request)
    return render_to_response('login.html', context)


def auth_login(func):
    def _deco(request, *args, **kwargs):
        global username
        username = request.session.get('username')
        if username:
            print
            ret = func(request, *args, **kwargs)
            return ret
        else:
            raise Http404()
    return _deco


@auth_login
def page(request, page):
    context = RequestContext(request)
    return render_to_response(page, context)

def commonly_url(request):

    url_list = [
        {'url': 'http://www.baidu.com', 'name': u'baidu'},
    ]

    context = RequestContext(request, {'url_list': url_list})
    return render_to_response('views.html', context)

