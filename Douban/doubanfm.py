#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
import os
import sys
import threading
import json
import subprocess
class DoubanfmBase:
    def __init__(self, email='', password='', onStart=None):
        self.appName = 'radio_desktop_win'
        self.version = '100'
        self.requests = requests.Session()
        self.projectPath = os.path.realpath(sys.path[0])
        self.picDir = self.projectPath
        self.childProcess = None
        self.params = {
            'app_name': self.appName,
            'version': self.version,
            'user_id': '',
            'expire': '',
            'token': '',
            'channel': 0,
            'type': 'n'
        }
        self.playing = False
        self.isLogin = False
        self.onStart = onStart
        self.playerPid = 0
        self.channels = self.getChannels()
        if email != '' and password != '':
            self.login(email, password)

    def login(self, email, password):
        response = json.loads(self.requests.post(
            'http://www.douban.com/j/app/login',
            data={
                'email': email,
                'password': password,
                'app_name': self.appName,
                'version': self.version}).content)
        if response['err'] == 'ok':
            self.params['user_id'] = response['user_id']
            self.params['expire'] = response['expire']
            self.params['token'] = response['token']
            self.isLogin = True
            print  '“%s”登录成功' % response['user_name']
            return True
        else:
            print 'login failed: %s' % response['err']
            return False

    def setChannel(self, channel):
        self.params['channel'] = channel
        print 'channel:'+str(channel)+'is set'
        self.next()

    def getChannels(self):
        channels = json.loads(requests.get('http://www.douban.com/j/app/radio/channels').content)['channels']
        channels.append({
            'name_en': 'Favorite Radio',
            'seq_id': len(channels),
            'abbr_en': 'Favorite',
            'name': '红心兆赫',
            'channel_id': -3
        })
        return channels

    def playlist(self):
        if hasattr(self, 'song'):
            params = self.params
            params['sid'] = self.song['sid']
            params['type'] = 's'
        list = json.loads(self.requests.get('http://www.douban.com/j/app/radio/people', params=self.params).content)
        return list

    def mainloop(self):
        while True:
            self.song = self.playlist()['song'][0]
            self.songs = ''
            for song in self.playlist()['song']:
                self.songs += song['url']+' '
            print self.songs
            print '%s：%s《%s》' % (
                self.song['title'],
                self.song['artist'],
                self.song['albumtitle'])
            child = subprocess.Popen(['mplayer', self.song['url']])
            self.player = child
            child.wait()

    def like(self):
        params = self.params
        params['sid'] = self.song['sid']
        if self.song['like'] == 0:
            params['type'] = 'r'
            self.song['like'] = 1
            print 'like this one'
        else:
            params['type'] = 'u'
            self.song['like'] = 0
            print 'dislike this one'
        self.requests.get('http://www.douban.com/j/app/radio/people', params=params)

    def remove(self):
        params = self.params
        params['sid'] = self.song['sid']
        params['type'] = 'b'
        self.requests.get('http://www.douban.com/j/app/radio/people', params=params)
        self.next()
        print 'not play any more'

    def run(self):
        self.thread = threading.Thread(target=self.mainloop())
        self.thread.start()

if __name__ == '__main__':
    fm = DoubanfmBase()
    fm.login('gayyzxyx@126.com','q1w2e3p0o9i8.')
    fm.run()
