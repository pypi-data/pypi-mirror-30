#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
"""
@Time : 18/3/19 下午6:00 
@Author : nice、柠檬 
@File : common.py 
@Software: PyCharm
"""
import hashlib
import time


# MD5加密
def string_to_md5(string):
    m = hashlib.md5()
    m.update(string)
    string = m.hexdigest()
    return string


# SHA加密
def string_to_sha(string):
    string = hashlib.sha1(string).hexdigest()
    return string


# 今日零点时间戳函数
def today_to_int():
    timestamp = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    timestamp = int(time.mktime(time.strptime(timestamp, '%Y-%m-%d')))
    return timestamp


# 时间戳转详细日期
def string_to_day(int_date):
    day_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int_date))
    return day_date


# 时间转日期
def string_to_ymd(int_date):
    date = time.strftime('%Y-%m-%d', time.localtime(int_date))
    return date


# 时间转时间戳
def int_to_YMDHMS(timestamp):
    timestamp = int(time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')))
    return timestamp


# 日期转时间戳
def int_to_YMD(timestamp):
    timestamp = int(time.mktime(time.strptime(timestamp, '%Y-%m-%d')))
    return timestamp
