# -*- coding: utf-8 -*-
#Библиотеки, които използват python и Kodi в тази приставка
import re
import sys
import os
import urllib
import urllib2
import cookielib
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import base64
import uuid
from time import localtime, strftime
import json
#Място за дефиниране на константи, които ще се използват няколкократно из отделните модули
__addon_id__= 'plugin.video.mtelnow'
__Addon = xbmcaddon.Addon(__addon_id__)
__settings__ = xbmcaddon.Addon(id='plugin.video.mtelnow')
login = base64.b64decode('aHR0cHM6Ly9tdGVsbm93LmJnL2xvZ2luLmFzcHg=')
loginred = base64.b64decode('aHR0cHM6Ly9tdGVsbm93LmJnL2xvZ2luP3E9dXNlckxvZ2lu')
dns = base64.b64decode('bXRlbG5vdy5iZw==')
baseurl = base64.b64decode('aHR0cHM6Ly93d3cubXRlbG5vdy5iZy9ub3c=')
item = base64.b64decode('aHR0cHM6Ly93d3cubXRlbG5vdy5iZy9Ob3dPblR2LmFzcHgvR2V0SXRlbURldGFpbHM=')
m1 = base64.b64decode('d3d3Lm10ZWxub3cuYmc=')
m2 = base64.b64decode('aHR0cHM6Ly93d3cubXRlbG5vdy5iZw==')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
#UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
username = xbmcaddon.Addon().getSetting('settings_username')
password = xbmcaddon.Addon().getSetting('settings_password')
if not username or not password or not __settings__:
        xbmcaddon.Addon().openSettings()
#Инициализация
req = urllib2.Request(login)
req.add_header('User-Agent', UA)
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
f = opener.open(req)
data = f.read()
match1 = re.compile('id="__VIEWSTATE" value="(.+?)"').findall(data)
match2 = re.compile('id="__VIEWSTATEGENERATOR" value="(.+?)"').findall(data)
for viewstate in match1:
 for vgenerator in match2:
    params = {'__EVENTTARGET':'ctl00$cph$lbLogin',
            '__EVENTARGUMENT=': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': vgenerator,
            'ctl00$hfPluginSerial': str(uuid.uuid5(uuid.NAMESPACE_DNS, dns)),
            'ctl00$hfPluginClientId': '',
            'ctl00$hfPluginVersion': '',
            'ctl00$hfDeviceSerial': str(uuid.uuid5(uuid.NAMESPACE_DNS, dns)),
            'ctl00$hfCustomerTime': strftime("%a %b %d %Y %H:%M:%S GMT+0200", localtime()),
            'ctl00$hfCurrentChannelRefId': '',
            'ctl00$hfCurrentChannelPlayScript': '',
            'ctl00$hfAjaxError': '',
            'ctl00$cph$txtUsername': username,
            'ctl00$cph$txtPassword': password,
            'ctl00$cph$hfTimezoneOffset':'120'
             }
    req = urllib2.Request(loginred, urllib.urlencode(params))
    req.add_header('User-Agent', UA)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    f = opener.open(req)
    data = f.read()

#Меню с директории в приставката
def CATEGORIES():
        addDir('Телевизия', baseurl , 1, 'DefaultFolder.png')
        

#Разлистване видеата на първата подадена страница
def INDEXPAGES(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        f = opener.open(req)
        data = f.read()
        match = re.compile('<img src="(.+?)" />\r\n.*<div class="title"><span>(.+?)</span></div>\r\n.*\r\n.*\r\n.*\r\n.*\r\n.*\r\n.*\r\n.*\r\n.*\r\n.*refid="(.+?)"\r\n.*\r\n.*\r\n.*\r\n.*(https.+?jpg).*\r\n.*\r\n.*<span>(.+?)</span>').findall(data)
        for thumbnail,title,chnum,fanart,vmomenta in match:
          desc = 'В момента:' + vmomenta
          fanart = urllib.unquote(fanart)
          url = item
          addLink(title,url+'@'+chnum,2,desc,thumbnail,fanart)


#Зареждане на видео
def PLAY(url):
         #xbmcgui.Dialog().ok('Търсене на излъчване',name+'Моля натиснете ОК!')
         match0 = re.compile('(.+?)@(.*)').findall(url)
         for url1, chnum in match0:
          #print url1
          #print chnum
          pd = '{"referenceId":' + '"' + chnum + '"' + ',"type":"live","source":"nowontv, startchannellivestream"}'
          postdata = {"clientAssetData":pd}
          data = json.dumps(postdata)
          #print postdata
          req = urllib2.Request(url1, data)
          #print req
          req.add_header('Host', m1)
          req.add_header('Connection', 'keep-alive')
          req.add_header('Origin', m2)
          req.add_header('X-Requested-With', 'XMLHttpRequest')
          req.add_header('User-Agent', UA)
          req.add_header('Content-Type', 'application/json; charset=UTF-8')
          req.add_header('Accept', '*/*')
          req.add_header('Referer', baseurl)
          req.add_header('Accept-Encoding', 'gzip, deflate, br')
          req.add_header('Accept-Language', 'bg-BG,bg;q=0.9')
          opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
          f = opener.open(req)
          data = f.read()
          #print data
          #dt_custom_data = base64.b64encode(data)
          match = re.compile('streamURL.":.+?(https.+?mpd)').findall(data)
          for ism in match:
           ism = ism.replace('\/','/')
           li = xbmcgui.ListItem(path=ism)
           li.setProperty('inputstreamaddon', 'inputstream.adaptive')
           li.setProperty('inputstream.adaptive.manifest_type', 'mpd')
           li.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
           li.setProperty('inputstream.adaptive.license_key', 'https://vipottvmxdrmwv.vip.hr/?deviceId=aGVsbG8=||R{SSM}|')
           li.setMimeType('application/dash+xml')
           #li.setContentLookup(False)
           try:
              xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
           except:
              xbmc.executebuiltin("Notification('Грешка','Видеото липсва на сървъра!')")





#Модул за добавяне на отделно заглавие и неговите атрибути към съдържанието на показваната в Kodi директория - НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def addLink(name,url,mode,plot,iconimage,fanart):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({ 'thumb': iconimage,'poster': fanart, 'banner' : fanart, 'fanart': fanart })
        liz.setInfo( type="Video", infoLabels={ "Title": name, "plot": plot } )
        liz.setProperty("IsPlayable" , "true")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok


#Модул за добавяне на отделна директория и нейните атрибути към съдържанието на показваната в Kodi директория - НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setArt({ 'thumb': iconimage,'poster': iconimage, 'banner' : iconimage, 'fanart': iconimage })
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok


#НЯМА НУЖДА ДА ПРОМЕНЯТЕ НИЩО ТУК
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param







params=get_params()
url=None
name=None
iconimage=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        name=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass


#Списък на отделните подпрограми/модули в тази приставка - трябва напълно да отговаря на кода отгоре
if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
    
elif mode==1:
        print ""+url
        INDEXPAGES(url)

elif mode==2:
        print ""+url
        PLAY(url)
xbmcplugin.endOfDirectory(int(sys.argv[1]))