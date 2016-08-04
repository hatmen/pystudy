# -*- coding:utf-8 -*-
#
from django.core.paginator import Paginator

def pagination(request, queryset, display_amount=15, after_range_num=5, bevor_range_num=4):
    # 按参数分页
    paginator = Paginator(queryset, display_amount)
    try:
        # 得到request中的page参数
        page = int(request.GET['page'])
    except:
        # 默认为1
        page = 1
    try:
        # 尝试获得分页列表
        objects = paginator.page(page)
    # 如果页数不存在
    except paginator.EmptyPage:
        # 获得最后一页
        objects = paginator.page(paginator.num_pages)
    # 如果不是一个整数
    except:
        # 获得第一页
        objects = paginator.page(1)
    # 根据参数配置导航显示范围
    if page >= after_range_num:
        page_range = paginator.page_range[page-after_range_num:page+bevor_range_num]
    else:
        page_range = paginator.page_range[0:page+bevor_range_num]
    return objects, page_range

