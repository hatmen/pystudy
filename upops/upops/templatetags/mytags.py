#-*- coding:utf-8 -*-
from django import template
from upops.models import USER_STATUS
from updbm.models import DBM_STATUS
from upurl.models import *
from upasset.models import *
register = template.Library()


@register.filter(name='group_str2')
def groups_str2(group_list):
    """
    将用户组列表转换为str
    """
    if len(group_list) < 3:
        return ','.join([group.name for group in group_list])
    else:
        return '%s ...' % ' '.join([group.name for group in group_list[0:2]])


@register.filter(name='upuser_status')
def upuser_status(id):
    """
    将ASSET_ENV元组id，映射为文字内容
    """
    if id:
        for list in USER_STATUS:
            if id in list:
                return list[1]
    else:
        return ''


@register.filter(name='updbm_status')
def updbm_status(id):
    if id:
        for list in DBM_STATUS:
            if id in list:
                return list[1]
    else:
        return ''


@register.filter(name='url_group_num')
def url_group_num(group_id):
    """统计URL组下成员数量"""
    group_name = UrlGroup.objects.get(id=group_id)
    if group_name:
        return group_name.url_set.count()
    else:
        return 0


@register.filter(name='asset_host_num')
def asset_host_num(group_id):
    """统计URL组下成员数量"""
    idc_name = IDC.objects.get(id=group_id)
    if idc_name:
        return idc_name.asset_set.count()
    else:
        return 0

@register.filter(name='asset_group_num')
def asset_group_num(group_id):
    """统计URL组下成员数量"""
    group_name = AssetGroup.objects.get(id=group_id)
    if group_name:
        return group_name.asset_set.count()
    else:
        return 0


@register.filter(name='map_env')
def map_env(id):
    """
    将ASSET_ENV元组id，映射为文字内容
    """
    if id:
        for list in ASSET_ENV:
            if id in list:
                return list[1]
    else:
        return ''


@register.filter(name='map_type')
def map_type(id):
    """
    将ASSET_TYPE元组id，映射为文字内容
    """
    if id:
        for list in ASSET_TYPE:
            if id in list:
                return list[1]
    else:
        return ''


@register.filter(name='get_null')
def get_null(result):
    """
    如果result为NONE，则显示空
    """
    if result:
        return result
    else:
        return ''
