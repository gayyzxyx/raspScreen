#!/user/bin/python
# -*- coding:utf-8 -*-
import os
import urllib
import urllib2
import json
import time
import getopt
import getpass
from cookielib import CookieJar

def save(filename,content):
    file = open(filename,'wb')
    file.write(content)
    file.close()

def get_music_json():
    url = "http://douban.fm/j/mine/playlist?type=n&channel=1"
    music_json = urllib.urlopen(url)
    base_json = json.load(music_json)
    output = open('tempfje_-83838399wfjefie.txt', 'a')
    for i in base_json['song']:
        title = i['title'].encode('utf8')
        artist = i['artist'].encode('utf8')
        mediaUrl = i['url'].encode('utf8')
        output.write(('%s\t%s\t%s' % (artist,title,mediaUrl))+'\n')
    output.close()

def getPlatList(channel='0',opener = None):
    url = 'http://douban.fm/j/mine/playlist?type=n&channel=' + channel
    if opener == None:
        return json.loads(urllib.urlopen(url).read())
    else:
        return json.loads(opener.open(urllib2.Request(url)).read())

def login(username,password):
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(CookieJar()))
    print 'fetching code...'
    captcha_id = opener.open(urllib2.Request('http://douban.fm/j/new_captcha')).read().strip('"')
    save('code.jpg',opener.open(urllib2.Request('http://douban.fm/misc/captcha?size=m&id=' + captcha_id)).read())
    captcha = raw_input('验证码: ')
    print 'now login..'
    response = json.loads(opener.open(urllib2.Request('http://douban.fm/j/login'),
    urllib.urlencode({
        'source': 'radio',
        'alias': username,
        'form_password': password,
        'captcha_solution': captcha,
        'captcha_id': captcha_id,
        'task': 'sync_channel_list'
    })).read())
    if 'err_msg' in response.keys():
        print response['err_msg']
    else:
        print 'login success'
        return opener
def play(channel='0', opener=None):
    while True:
        if opener == None:
            playlist = getPlatList(channel)
        else:
            playlist = getPlatList(channel,opener)

        if playlist['song'] == []:
            print '获取播放列表失败'
            break
        for song in playlist['song']:
            picture = song['picture'].split('/')[-1]

            save(picture,urllib.urlopen(song['picture']).read())
            print 'now playing'+song['title'].encode('utf8')
            time.sleep(song['length'])
def main():
    for i in range(0,2):
        get_music_json()
        print i
        time.sleep(1)
    print '抓取完成'

if __name__=='__main__':
    #password = getpass.getpass('密码：')
    opener = login('gayyzxyx@126.com','q1w2e3p0o9i8.')
    play('-3',opener)
