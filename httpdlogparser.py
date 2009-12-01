#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pyip
import MySQLdb
import time
import datetime
import smtplib
import glob
import os
import os.path
import simplejson as json

IPFILE = os.path.join(os.path.dirname(__file__), 'QQWry.Dat')

class Client:
    """ client infomation """
    
    def __init__(self):
        self.ip = None
        self.city = None
        self.isp = None
        self.datetime = None
        self.loadtime = None
        self.ref = None
        self.domain = None
        self.agent = None

class HttpdLogParser:
    """ parser logs generated by httpd and generate a report. """
    
    def __init__(self, logfile):
        self.logfile = logfile
        self.clients = []
        
    def parseLog(self):
        f = open(self.logfile, 'r')
        for line in f.xreadlines():
            client = Client()
            info = line.split('"')
            client.agent = info[-2]
            ip_datetime = info[0].split(' ')
            client.ip = ip_datetime[0]
            
            i = pyip.IPInfo(IPFILE)
            city, isp = i.getIPAddr(client.ip)
            client.city = city.decode('utf8')
            client.isp = isp.decode('utf8')
            
            dt = ip_datetime[3]
            dt = dt[-(len(dt)-1):]
            
            t = time.strptime(dt, '%d/%b/%Y:%H:%M:%S')
            client.datetime = datetime.datetime(*t[:6])
            
            pattern = re.compile(r't=(?P<time>\d+)&r=(?P<ref>http://(?P<domain>\S+?).360quan.com\S+)')
            m = pattern.search(info[1])
            client.loadtime = None
            client.ref = None
            client.domain = None
            if m:
                client.loadtime = int(m.group('time'))
                client.ref = m.group('ref')
                client.domain = m.group('domain')
                self.clients.append(client)
        return self.clients

def genReport(day, cursor):
    #dir = '/Data/webapps/zx/data'
    report = os.path.join(os.path.dirname(__file__), 'data', day.strftime('%Y-%m-%d'))
    #report = '%s/%s' % (dir, day.strftime('%Y-%m-%d'))
    f_report  = open(report, 'w+')
    chart = {}
    
    chart['title']={}
    chart['title']['text']='Report for response time.'
    chart['title']['style']='{font-size:20px; color:#0000ff; font-family: Verdana; text-align: center;}'
    
    chart['x_legend']={}
    chart['x_legend']['text']='Date: %s' % day.strftime('%Y-%m-%d')
    chart['x_legend']['style']='{color: #736AFF;font-size: 12px;}'
    chart['y_legend']={}
    chart['y_legend']['text']='time(ms)'
    chart['y_legend']['style']='{color:#736AFF; font-size: 12px;}'
    
    chart['x_axis'] = {}
    chart['x_axis']['stroke'] = 1
    chart['x_axis']['labels'] = {}
    chart['x_axis']['labels']['rotate'] = 45
    chart['x_axis']['labels']['labels'] = ["00:00","01: 00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00","08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00","15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00",
"22:00", "23:00"]
    
    chart['y_axis'] = {}
    chart['y_axis']['stroke'] = 1
    chart['y_axis']['visible'] = True
    chart['y_axis']['offset'] = False
    chart['y_axis']['max'] =  50
    
    chart['elements']=[]
    d = datetime.timedelta(days=1)
    #t_tmp = time.strptime(day, '%Y-%m-%d')
    #d_day = datetime.datetime(*t_tmp[:6])
    #nextday = d_day + d
    nextday = day + d
    domains = ['www', 'my', 'www1']
    colors = {'www': '#ffae00', 'my':'#52aa4b', 'www1': '#ff0000'}
    lines = {}
    chart['rows'] = []
    for domain in domains:
        #sql = 'SELECT ip, city, isp, date_c, loadtime, domain, agent FROM log WHERE domain="%s" AND date_c>="%s 00:00:00" AND date_c<"%s 00:00:00"' % (domain, day.strftime('%Y-%m-%d'), nextday.strftime('%Y-%m-%d'))
        sql = 'SELECT ip, city, isp, date_c, loadtime, domain, ref FROM log WHERE domain="%s" AND date_c BETWEEN "%s 00:00:00" AND "%s 00:00:00"' % (domain, day.strftime('%Y-%m-%d'), nextday.strftime('%Y-%m-%d'))
        cursor.execute(sql)
        
        rows = cursor.fetchall()
        lines[domain] = {}
        lines[domain]['type'] = 'line'
        lines[domain]['colour'] = colors[domain]
        lines[domain]['text'] = domain
        lines[domain]['dot-style'] = {}
        lines[domain]['dot-style']['type'] = 'solid-dot'
        lines[domain]['values'] = [0 for _ in range(24)]
       
        chart['total'] = chart.get('total',0) + len(rows)
        
        for row in rows:
            r = {}
            r['domain'] = domain
            r['city'] = row['city']
            r['isp'] = row['isp']
            r['datetime'] = row['date_c'].strftime('%m/%d/%Y %H:%M:%S')
            r['time'] = row['loadtime']
            r['ref'] = row['ref']
            chart['rows'].append(r) 
            
            hour = row['date_c'].hour
            
            lt = lines[domain]['values'][hour]
            if lt:
                lt = (lt + row['loadtime'])/2
            else:
                lt = row['loadtime']
            lines[domain]['values'][hour] = lt
            
            if lt > chart['y_axis']['max']:
                chart['y_axis']['max'] = lt + 10000
            
        chart['elements'].append(lines[domain])
        
    f_report.write(json.dumps(chart))
    f_report.close()

if __name__ == '__main__':
    import sys
    import logging
    
    logger = logging.getLogger('stats')
    logger.setLevel(logging.DEBUG)
    hdlr = logging.FileHandler(os.path.join(os.path.dirname(__file__), '%s.log' %os.path.basename(__file__)))
    hdlr.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s | %(lineno)s | %(message)s')
    hdlr.setFormatter(fmt)
    logger.addHandler(hdlr)
    
    delta_one_day = datetime.timedelta(days=1)
    yesterday = datetime.date.today() - delta_one_day
    tomorrow = datetime.date.today() + delta_one_day

    try:
        #conn = MySQLdb.connect(host='192.168.5.55',
        #                       port=23303,
        conn = MySQLdb.connect(host='10.10.208.59',
                               user='httpdlog',
                               passwd='httpdlog',
                               db='httpdlog',
                               charset='utf8')
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    except MySQLdb.Error, e:
        print 'Connecting MySQL error!'
        sys.exit(1)
        
    logs = glob.glob('/logs/zx_360quan-access_log.%s??' % yesterday.strftime('%Y%m%d'))
    for log in logs:
        logger.info('[log file]%s' % log)
        hlp =  HttpdLogParser(log)
        clients = hlp.parseLog()
        for client in clients: 
            sql = "INSERT INTO log (ip, city, isp, date_c, loadtime, domain, ref, agent) VALUES ('%s', '%s', '%s', '%s', %d, '%s', '%s', '%s');" % (client.ip, client.city, client.isp, client.datetime.strftime('%Y-%m-%d %H:00:00'), client.loadtime, client.domain, client.ref, client.agent)
            cursor.execute(sql)
        
    genReport(yesterday ,cursor)
    cursor.close()
    conn.close()
    
    msg = """
    The average response time report. 
    Date: \t%s
    Link: \t<a href='http://zx.360quan.com/stats.html?ofc=data/%s' target='_blank'>view report</a>
    """ % (yesterday.strftime('%Y-%m-%d'), yesterday.strftime('%Y-%m-%d'))
    f_mail = open('mail.txt', 'w+')
    f_mail.write(msg)
    f_mail.close()
    # r = os.popen('mail -c liusong@360quan.com -s "Average Response Time Report" svn@360quan.com < mail.txt')
    r = os.popen('mail -c fengyue@360quan.com,zhangyuxiang@360quan.com,liusong@360quan.com -s "Average Response Time Report" dan@360quan.com,uzi.refaeli@360quan.com < mail.txt')    
