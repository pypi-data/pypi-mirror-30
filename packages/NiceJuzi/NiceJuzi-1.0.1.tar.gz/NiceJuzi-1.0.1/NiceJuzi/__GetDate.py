#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
"""
@Time : 18/3/19 下午6:26 
@Author : nice、柠檬 
@File : __GetDate.py 
@Software: PyCharm
"""
import calendar
import time
import datetime


class get_day_list(object):
    def __init__(self, day_type=None, data_type=False):
        """
        :param day_type: 需要返回的数据类型，
        上月：last_month
        上周：week
        本月：month
        今天： 可不传
        :param data_type: 需要返回的日期数据，是全部的列表还是，只需要最大和最小；
        列出所有日期：list_all
        只需要最大和最小： 可不传，或者传 min
        """
        self.day_type = day_type
        self.data_type = data_type
        self.return_data = list()
        self.day_now = time.localtime()
        self.time_format_one = '%d-%02d-%02d'
        self.time_format_two = '%Y-%m-%d'

    def list_day(self):
        """
        根据不同的日期选择进行，返回数据
        :return:
        """
        if self.day_type == 'last_month':
            if self.day_now.tm_mon == 1:
                day_year = self.day_now.tm_year - 1
                day_month = 12
            else:
                day_year = self.day_now.tm_year
                day_month = self.day_now.tm_mon - 1
            # 如果是1月则年份减一，月份变成12月
            self.type_month(day_year, day_month)
        elif self.day_type == "last_week":
            self.type_last_week()
        elif self.day_type == "week":
            self.type_week_day()
        elif self.day_type == 'month':
            day_now = time.localtime()
            day_year = day_now.tm_year
            day_month = day_now.tm_mon
            self.type_month(day_year, day_month)
        elif self.day_type == 'yesterday':
            yesterday_time = time.strftime(self.time_format_two, time.localtime(int(time.time())-86400))
            self.return_data.append(yesterday_time)
            self.return_data.append(yesterday_time)
        else:
            today = time.strftime(self.time_format_two)
            self.return_data.append(today)
            self.return_data.append(today)
        return self.return_data

    def get_last_Week_DAY(self, x):
        """
        :param x: 传入获取星期几， 1是周一，7是周日
        """
        one_day = (datetime.datetime.today() - datetime.timedelta(days=time.localtime().tm_wday + x)).strftime(
            self.time_format_two)
        return one_day

    def get_one_day(self, day_year, day_month, x):
        """
        :param day_year: 日期的年份
        :param day_month: 日期的月份
        :param x: 日期的天数
        """
        one_day = self.time_format_one % (day_year, day_month, x)
        return one_day

    def type_month(self, day_year, day_month):
        """
        :param day_year: 传入年份
        :param day_month: 传入月份
        :return: 返回值类型是list_all则返回所有列表，否则返回最大和最小
        """
        weekday, monthRange = calendar.monthrange(day_year, day_month)
        if self.data_type:
            for x in range(1, monthRange + 1):
                self.return_data.append(self.get_one_day(day_year, day_month, x))
        else:
            self.return_data.append(self.get_one_day(day_year, day_month, 1))
            self.return_data.append(self.get_one_day(day_year, day_month, monthRange))

    def type_last_week(self):
        """
        :return: 返回值类型是list_all则返回所有列表，否则返回最大和最小
        """
        if self.data_type:
            for x in range(1, 8)[::-1]:
                self.return_data.append(self.get_last_Week_DAY(x))
        else:
            self.return_data.append(self.get_last_Week_DAY(7))
            self.return_data.append(self.get_last_Week_DAY(1))

    def type_week_day(self):
        now = datetime.datetime.now()
        week_num = now.weekday()
        if self.data_type:
            for x in range(0, week_num + 1):
                date = (now - datetime.timedelta(days=x)).strftime(self.time_format_two)
                self.return_data.append(date)
                if week_num == 0:   # 如果是周一则需要再次添加一个日期
                    self.return_data.append(date)
                self.return_data.sort()
        else:
            self.return_data.append((now - datetime.timedelta(days=week_num)).strftime(self.time_format_two))
            self.return_data.append(now.strftime(self.time_format_two))
