#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
"""
@Time : 18/3/19 下午5:41 
@Author : nice、柠檬 
@File : __init__.py.py 
@Software: PyCharm
"""

from __util import *
from __GetDate import get_day_list


def Get_last_week_date(list_all=False):
    """
    :param list_all: True 显示所有日期列表， False只显示首尾日期， 默认只显示首尾的
                   : True displays all date lists, False shows only the first and end date,
                    and the default only shows the first and end.
    :return: 上周日期数组
           : last week date list
    """
    return get_day_list('last_week', list_all).list_day()


def Get_month_date(list_all=False):
    """
    :param list_all: True 显示所有日期列表， False只显示首尾日期， 默认只显示首尾的
                   : True displays all date lists, False shows only the first and end date,
                    and the default only shows the first and end.
    :return: 本月日期数组
           : month date list
    """
    return get_day_list('month', list_all).list_day()


def Get_last_month_date(list_all=False):
    """
    :param list_all: True 显示所有日期列表， False只显示首尾日期， 默认只显示首尾的
                   : True displays all date lists, False shows only the first and end date,
                    and the default only shows the first and end.
    :return: 上月日期数组
           : last month date list
    """
    return get_day_list('last_month', list_all).list_day()


def Get_today_date(list_all=False):
    """
    :param list_all: True 显示所有日期列表， False只显示首尾日期， 默认只显示首尾的
                   : True displays all date lists, False shows only the first and end date,
                    and the default only shows the first and end.
    :return: 今日日期数组
           : today date list
    """
    return get_day_list('today', list_all).list_day()


def Get_yesterday_date(list_all=False):
    """
    :param list_all: True 显示所有日期列表， False只显示首尾日期， 默认只显示首尾的
                   : True displays all date lists, False shows only the first and end date,
                    and the default only shows the first and end.
    :return: 昨日日期数组
           : yesterday date list
    """
    return get_day_list('yesterday', list_all).list_day()


def Get_week_date(list_all=False):
    """
    :param list_all: True 显示所有日期列表， False只显示首尾日期， 默认只显示首尾的
                   : True displays all date lists, False shows only the first and end date,
                    and the default only shows the first and end.
    :return: 本周日期数组
           : now week date list
    """
    return get_day_list('week', list_all).list_day()
