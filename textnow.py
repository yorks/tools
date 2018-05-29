#!/usr/bin/env python2
#-*- coding: utf-8 -*-
#
# textnow.py:
#    a script to send sms to google voice
#    for keep google voice No. active
#
#  add this to a cron job like this:
#     python2 textnow.py cookie_connect_sid_value  your_gv_no. msg_you_want_to_send
#
# How to get cookie connect_sid
#    login by web browser such as Firefox, and then open Develop, you can see the cookie value.
#

import requests
import pickle
import json
import urllib
import datetime
import sys,os,re

cookie_file='.textnow.cookie'

class TextNow(object):
    def __init__(self, username=None, password=None, connect_sid=None):
        self.username = username
        self.email    = username
        self.password = password
        self.sid      = connect_sid

        self.session = requests.Session()
        self.headers = {'Host':'www.textnow.com',
                        'Referer':'https://www.textnow.com/login',
                        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Pragma': 'no-cache',
                        'Cache-Control': 'no-cache',
                }

        if self.sid:
            self.headers['Cookie'] = "unsupported_browsers_notif=true; connect.sid=%s; language=zh"% self.sid

        self.session.headers.update(self.headers)

    def save_cookie(self):
        with open(cookie_file, 'w') as f:
            pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)

    def load_cookie(self):
        if not os.path.isfile(cookie_file):
            return False
        with open(cookie_file) as f:
            cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
            #self.session = requests.session(cookies=cookies)
            self.session.cookies = cookies
            return True

    def check_login(self):
        url = 'https://www.textnow.com/account'
        r = self.session.get(url)
        #  window.sessionUsername = "stuyorks";
        try:
            return r.text.split('window.sessionUsername')[1].split('"')[1]
        except Exception, e:
            print e
            print "cookie expired?"
        return False

    def _index_page(self):
        ''' request index page get cookie '''
        url = 'https://www.textnow.com/'
        r = self.session.get(url)
        ''' <meta name="csrf-token" content="C4huOo2A-YH8E1frEMB9LZ-1AONaTS9Zg0mc" >
        '''
        try:
            token = re.findall(r'name="csrf-token" content="([^"]+)"', r.text)[0]
        except Exception, e:
            print e
            print 'index page exception, cannot found the csrf-token'
            return False
        self.session.headers['X-CSRF-TOKEN'] = token
        return token

    def login(self):
        # login by cookie files
        tk = self._index_page()
        if self.load_cookie():
            un = self.check_login()
            if un and un != 'undefined':
                self.username = un
                print self.username + " logined by cookiefile"
                return True

        # login by connect_sid cookie commanline
        if not self.sid:
            print "no sid given"
            return False
        un = self.check_login()
        if un and un != 'undefined':
            self.username = un
            print self.username + " logined by cookiefile"
            self.save_cookie()
            return True
        return False


        # username password login TODO
        tk = self._index_page()
        if not tk:
            return False
        url = 'http://www.textnow.com/api/sessions'
        data = {"username":self.username,"remember":True,"password":self.password}
        data = 'json='+urllib.quote(json.dumps(data).replace(' ',''))
        #print data
        print self.session.cookies
        self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        print self.session.headers
        r = self.session.post(url, data=data)
        print r.headers
        print r.content
        res = json.loads(r.content)
        if self.username.find('@') != -1:
            self.username = res['username']
            self.save_cookie()

    def send_msg(self, to, msg):
        url = 'https://www.textnow.com/api/users/%s/messages'% self.username
        date = datetime.datetime.now().strftime('%a+%b+%d+%Y+%T+GMT+0800+(CST)')
        data = '{"contact_value":"%s","contact_type":2,"message":"%s","read":1,"to_name":"%s","message_direction":2,"message_type":1,"date":"%s","from_name":"%s"}'% (to, msg, to, date, self.username)
        data = 'json='+urllib.quote(data)
        #print data
        self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        r = self.session.post(url, data=data)
        print r.headers
        print r.content


if __name__ == "__main__":
    username=''
    passwd=''
    sid=''
    try: # username&password login TODO
        msg = sys.argv[4]
        username = sys.argv[1]
        passwd   = sys.argv[2]
        to       = sys.argv[3]
    except: # cookie login pass the connect_sid cookie value
        try:# python2 textnow.py 's:Kw**/*****'  +1860858**** msg_active_gv
            msg = sys.argv[3]
            to  = sys.argv[2]
            sid = sys.argv[1]
        except: # cookie file login
            msg = sys.argv[2]
            to  = sys.argv[1]

    tn = TextNow(username, passwd, sid)
    if not tn.login():
        print "no login"
        sys.exit(1)
    tn.send_msg(to, msg)
