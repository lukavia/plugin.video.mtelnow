# -*- coding: utf-8 -*-
import sys
import xbmc, xbmcaddon, xbmcvfs
import uuid
import datetime, time, pytz
import json
from lib.graphqlclient import GraphQLClient
from lib.six.moves import urllib
import requests
from lib.six.moves.http_cookiejar import LWPCookieJar

def debug(obj):
    xbmc.log(json.dumps(obj, indent=2), xbmc.LOGDEBUG)

__addon__ = xbmcaddon.Addon(id='plugin.video.mtelnow')
if 'translatePath' in dir(xbmcvfs):
    datadir = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
else:
    datadir = xbmc.translatePath(__addon__.getAddonInfo('profile'))

#Място за дефиниране на константи, които ще се използват няколкократно из отделните модули
username = __addon__.getSetting('settings_username')
password = __addon__.getSetting('settings_password')
max_bandwidth = __addon__.getSetting('settings_max_bandwidth')
if __addon__.getSetting('settings_adult') == "false":
    adult_setting = False
else:
    adult_setting = True
args = urllib.parse.parse_qs(sys.argv[2][1:])

session = requests.Session()
cookiejar = datadir + '/cookiejar'
session.cookies = LWPCookieJar(cookiejar)
if xbmcvfs.exists(cookiejar):
    session.cookies.load(ignore_discard=True)
class Data:
    def __init__(self):
        if xbmcvfs.exists(datadir + '/data.json'):
            fp = xbmcvfs.File(datadir + '/data.json')
            self.data = json.load(fp)
            fp.close()
        else:
            self.data = {}
    def getSetting(self, id, default=''):
        if id in self.data:
            return self.data[id]
        else:
            return default
    def setSetting(self, id, value):
        if id not in self.data or value != self.data[id]:
            self.data[id] = value
            fp = xbmcvfs.File(datadir + '/data.json', 'w')
            json.dump(self.data, fp, indent=2)
            fp.close()

data = Data()
user_id = data.getSetting('user_id')
if not user_id:
    data.setSetting('user_id', __addon__.getSetting('settings_user_id'))
    user_id = data.getSetting('user_id')
session_id = data.getSetting('session_id')
if not session_id:
    data.setSetting('session_id', __addon__.getSetting('settings_session_id'))
    session_id = data.getSetting('session_id')

# device_id, ще го мъкнем като параметър, че понякога се взима бавно
#device_id = args.get('device_id',[''])[0]
device_id = data.getSetting('device_id')
if not device_id:
    data.setSetting('device_id', __addon__.getSetting('settings_device_id'))
    device_id = data.getSetting('device_id')
    if not device_id:
        mac = xbmc.getInfoLabel('Network.MacAddress')
        # Мак-а може да се върне като Busy, ако kodi прави нещо друго, затова пробваме докато успеем
        while mac == 'Busy':
            time.sleep(0.5)
            mac = xbmc.getInfoLabel('Network.MacAddress')
        device_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, mac))
        data.setSetting('device_id', device_id)

# Класс за ползване на GraphQL
class my_gqlc(GraphQLClient):
    def __init__(self, headers, session = None):
        self.endpoint = 'https://web.a1xploretv.bg:8443/sdsmiddleware/Mtel/graphql/4.0'
        self.headers = headers
        self.session = session
    def execute(self, query, variables=None):
        debug(self.headers)
        debug(query.partition('\n')[0])
        res = self._send(query, variables, self.headers)
        debug(res)
        self.session.cookies.save(ignore_discard=True)
        if 'errors' in res:
            for error in res['errors']:
                raise Exception(error['message'])
        return res

def to_datetime(instr):
    return datetime.datetime(*(time.strptime(instr, '%Y-%m-%dT%H:%M:%SZ')[0:6])).replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone('Europe/Sofia'))

#изпращане на requst към endpoint
def request(action, params={}, method='POST'):
    endpoint = 'https://web.a1xploretv.bg:8843/ext_dev_facade/auth/'
    data = {}
    data.update(params)
    debug(action)
    debug(data)
    if method == 'POST':
        req = session.post(url = endpoint + action + '?%s' % urllib.parse.urlencode(data), headers = {'Content-Type':'application/json'})
    else:
        req = session.get(url = endpoint + action + '?%s' % urllib.parse.urlencode(data), headers = {'Content-Type':'application/json'})
    json_responce = req.json()
    session.cookies.save(ignore_discard=True)
    debug(json_responce)
    return json_responce
