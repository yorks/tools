#!/usr/bin/env python2
#-*- coding: utf-8 -*-
#
# textnow.py:
#    a script to send sms to google voice
#    for keep google voice No. active
#
#  add this to a cron job like this:
#     python2 textnow.py your_text_now_username your_text_now_password  your_gv_no. msg_you_want_to_send
#

import requests
import json
import urllib
import datetime
import sys


class TextNow(object):
    def __init__(self, username, password):
        self.username = username
        self.email    = username
        self.password = password
        self.session = requests.Session()
        self.headers = {'Host':'www.textnow.com',
                        'Referer':'https://www.textnow.com/login',
                        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Pragma': 'no-cache',
                        'Cache-Control': 'no-cache',
                }
        self.session.headers.update(self.headers)



    def login(self):
        url = 'http://www.textnow.com/api/sessions'
        data = {"username":self.username,"remember":False,"password":self.password}
        data = 'json='+urllib.quote(json.dumps(data).replace(' ',''))
        #print data
        self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
        r = self.session.post(url, data=data)
        print r.headers
        print r.content
        res = json.loads(r.content)
        if self.username.find('@') != -1:
            self.username = res['username']

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
    username = sys.argv[1]
    passwd   = sys.argv[2]
    to       = sys.argv[3]
    msg      = sys.argv[4]

    tn = TextNow(username, passwd)
    tn.login()
    tn.send_msg(to, msg)


