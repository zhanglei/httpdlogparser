#!/usr/bin/env python

import os
import re
import os.path
import pyip
#import simplejson

IPDATA = os.path.join(os.path.dirname(__file__), 'QQWry.Dat')

class GuestBase:
    
    def set_ip(self, ip):
        self.ip = ip
        self.set_location()
        
    def set_time(self, dt):
        self.datetime = dt
        
    def set_resource(self, resource):
        self.resource  = resource
        
    def set_referer(self, referer):
        self.referer = referer
    
    def set_agent(self, agent):
        self.agent = agent
        
    def set_target_url(self, url):
        self.target_url = url
    
    def set_name(self, name):
        self.name = name
        
    def set_location(self):
        ipinfo = pyip.IPInfo(IPDATA)
        city, isp = ipinfo.getIPAddr(self.ip)
        self.city = city.decode('utf-8')
        self.isp = isp.decode('utf-8')
        
class apachelog:
    """ apache log file class """
    
    def __init__(self, log_filename, guest_class, regex):
        self.log_filename = log_filename
        self.guest_class = guest_class
        self.regex = regex
        self.guest_list = []
        
    def parseFile(self):
        f = open(self.log_filename, 'r')
        for line in f.xreadlines():
            g = self.getGuestInfo(line)
            self.guest_list.append(g)
        f.close()
        return self.guest_list
    
    def getGuestInfo(self, string):
        guest = apply(self.guest_class)
        info = string.split('"')
        # ip and datetime
        ip_datetime = info[0].split(' ')
        guest.set_ip(ip_datetime[0])
        dt = ip_datetime[3]
        dt = dt[-(len(dt)-1):]
        t = time.strptime(dt, '%d/%b/%Y:%H:%M:%S')
        guest.set_time(datetime.datetime(*t[:6]))
        # resource name
        guest.set_resource(info[1])
        guest.set_referer(info[3])
        # agent
        guest.set_agent(info[-2])
        
        # parse more info.
        guest.parseResource(self.regex)
        
        return guest
    
class ReportBase:
    
    def __init__(self, report_filename, chart):
        self.filename = report_filename
        self.chart = chart
        
    def generateReport(self):
        pass