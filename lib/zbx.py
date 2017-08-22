# -*- coding: utf-8 -*-
import urllib2
import json
import logging
import sys

"""
Source: https://github.com/ableev/Zabbix-in-Telegram/
"""

log = logging.getLogger("zbxtg")

class ZabbixAPI():
    def __init__(self, server, username, password):
        self.debug = False
        self.server = server
        self.username = username
        self.password = password
        self.proxies = {}
        self.verify = True
        self.cookie = None

    def authenticate(url, username, password):
        values = {'jsonrpc': '2.0',
                  'method': 'user.login',
                  'params': {
                      'user': username,
                      'password': password
                  },
                  'id': '0'
                  }

        data = json.dumps(values)
        req = urllib2.Request(url, data, {'Content-Type': 'application/json-rpc'})
        response = urllib2.urlopen(req, data)
        output = json.loads(response.read())

        try:
            message = output['result']
        except:
            message = output['error']['data']
            print message
            quit()

        return output['result']