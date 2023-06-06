# -*- coding:utf-8 -*-
############################################################################
'''
# 功能：提供公共功能
'''
#############################################################################
import os
import datetime
import calendar
import time
import random
import math
import traceback
import re
import pymysql
import requests

########### Pub #################################################################
class Pub:
    isproxy = 0  # 如需要使用代理，改为1，并设置代理IP参数 proxy
    proxy = {'http': 'http://110.37.84.147:8080', 'https': 'http://110.37.84.147:8080'} #这里需要替换成可用的代理IP
    sleep_time = 0.1

    def randomHeader():
        '''
        随机生成User-Agent
        :return:
        '''
        head_connection = ['Keep-Alive', 'close']
        head_accept = ['text/html, application/xhtml+xml, */*']
        head_accept_language = ['zh-CN,fr-FR;q=0.5', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']
        head_user_agent = ['Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                           'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                           'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                           'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                           'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
                           'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11',
                           'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                           'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0'
                           ]
        result = {
            'Connection': head_connection[0],
            'Accept': head_accept[0],
            'Accept-Language': head_accept_language[1],
            'User-Agent': head_user_agent[17] #[random.randrange(0, len(head_user_agent))]
            }
        return result

    def getURL(url, retry_count=0, sleep_time=0, time_out=10, max_retry = 5):
            '''
            这里重写get函数，主要是为了实现网络中断后自动重连，同时为了兼容各种网站不同的反爬策略及，通过sleep时间和timeout动态调整来测试合适的网络连接参数；
            通过isproxy 来控制是否使用代理，以支持一些在内网办公的同学
            :param: url
            :param: retry_count  重试次数
            :param: sleep_time 休眠时间
            :param: time_out 连接超时参数
            :param: max_retry 最大重试次数，仅仅是为了递归使用
            :return: response
            '''
            try:
                header = Pub.randomHeader()
                res = requests.Session()
                if Pub.isproxy == 1:
                    res = requests.get(url, headers=header, timeout=time_out, proxies=Pub.proxy)
                else:
                    res = requests.get(url, headers=header, timeout=time_out)
                res.raise_for_status()  # 如果响应状态码不是 200，就主动抛出异常
            except requests.RequestException as e:
                # 设置重试次数、timeout 时间、休眠时间
                retry_count += 1
                sleep_time += 10
                time_out += 10
                if retry_count <= max_retry:
                    time.sleep(sleep_time)
                    print (Pub.getCurrentTime(), '[getURL()] Connection Error: ', url, u'retry: 第', retry_count, '/', max_retry, u'次\n', e)
                    return Pub.getURL(url, retry_count, sleep_time, time_out, max_retry)
            return res

    def getCurrentTime():
        # 获取当前时间
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))

    def getdates():
        # 获取当前时间
        time = datetime.date(2017, 7, 20) #年，月，日

        #求该月第一天
        d1_this_month = datetime.date(time.year, time.month, 1)
        print(u'该月第一天:', d1_this_month)

        #求前一个月的第一天、最后一天
        #前一个月最后一天
        d31_last_month = d1_this_month - datetime.timedelta(days = 1) 
        #前一个月的第一天
        d1_last_month = datetime.date(d31_last_month.year, d31_last_month.month, 1)
        print(u'前一个月的第一天、最后一天:', d1_last_month, d31_last_month)

        #求后一个月的第一天
        days_num = calendar.monthrange(d1_this_month.year, d1_this_month.month)[1] #获取一个月有多少天
        d1_next_month = d1_this_month + datetime.timedelta(days = days_num) #当月的最后一天只需要days_num-1即可
        print(u'后一个月的第一天:', d1_next_month)

########### MySQL #################################################################
class PyMySQL:
   
    ### 数据库初始化
    def __init__(self, host, user, passwd, db, port=3306, charset='utf8'):
        pymysql.install_as_MySQLdb()
        try:
            self.db =pymysql.connect(host=host, user=user, passwd=passwd, db=db, port=3306, charset='utf8')
            self.db.ping(True)  #使用mysql ping来检查连接,实现超时自动重新连接
            print(Pub.getCurrentTime(), u'[PyMySQL/_init_()] Connecting to DB succeeded: %s, %s, %s, /%s' %(host, str(port), user, db))
            self.cur = self.db.cursor()
        except  Exception as e:
            print (Pub.getCurrentTime(), u'[PyMySQL/_init_()] Connecting to DB failed: %d: %s' % (e.args[0], e.args[1]))

    ### 查询数据
    def selectData(self, sql, para):
        try:
            result = self.cur.execute(sql, para)
            return self.cur.fetchall()
        except Exception as e:
            print (Pub.getCurrentTime(), u'[PyMySQL/selectData()] Selecting data failed: %s, SQL: %s' % (e, sql))
            return -1
            
    ### 插入数据
    def insertData(self, table, my_dict):
        try:
            #self.db.set_character_set('utf8')
            cols = ', '.join(my_dict.keys())
            values = '","'.join(my_dict.values())
            sql = 'replace into %s (%s) values (%s)' % (table, cols, '"' + values + '"')
        except Exception as e:
            print (Pub.getCurrentTime(), u'[PyMySQL/insertData()] Error: %s, data: %s' % (e, my_dict))
            return 0

        try:
            result = self.cur.execute(sql)
            insert_id = self.db.insert_id()
            self.db.commit()
            ### 判断是否执行成功
            if result:
                #print (Pub.getCurrentTime(), u'Inserting data succeeded:', insert_id)
                return insert_id
            else:
                return 0
        except Exception as e:
            ### 发生错误时回滚
            self.db.rollback()
            print (Pub.getCurrentTime(), u'[PyMySQL/insertData()] Inserting data failed: %s, SQL: %s' % (e, sql))
            return 0

    ### 修改数据
    def updateData(self, table, set_dict, where_dict):
        try:
            set_list = [k + '="' + set_dict[k] + '"' for k in set_dict]
            set_str = ', '.join(set_list)
            where_list = [k + '="' + where_dict[k] + '"' for k in where_dict]
            where_str = ' and '.join(where_list)

            sql = 'update %s set %s where %s' % (table, set_str, where_str)
        except Exception as e:
            print (Pub.getCurrentTime(), u'[PyMySQL/updateData()] Error: %s, data: %s, %s' % (e, set_dict, where_dict))
            return 0

        try:
            result = self.cur.execute(sql)
            self.db.commit()
            ### 判断是否执行成功
            if result:
                #print (Pub.getCurrentTime(), u'Updating data succeeded')
                return 1
            else:
                return 0
        except Exception as e:
            ### 发生错误时回滚
            self.db.rollback()
            print (Pub.getCurrentTime(), u'[PyMySQL/updateData()] Updating data failed: %s, SQL: %s' % (e, sql))
            return 0


