#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
import os
import sys
import gst
import threading
import pynotify
import json
import time
import string
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
        self.player = gst.element_factory_make('playbin','player')
        self.event = threading.Event()
        self.playing = False
        self.isLogin = False
        self.onStart = onStart
        self.playerPid = 0
        self.channels = self.getChannels()
        pynotify.init(self.appName)
        self.notify = pynotify.Notification('')
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)
        if email != '' and password != '':
            self.login(email, password)


    def on_message(self, bus, message):
        if message.type == gst.MESSAGE_EOS:
            self.next()

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

    def next(self):
        self.player.set_state(gst.STATE_NULL)
        self.event.set()
        self.childProcess.cancel()

    def mainloop(self):
        while True:
            self.song = self.playlist()['song'][0]
            self.player.set_property('uri', self.song['url'])
            self.player.set_state(gst.STATE_PLAYING)
            self.playing = True
            t = threading.Timer(self.song['length'], self.next)
            t.start()
            self.childProcess = t
            print '%s：%s《%s》' % (
                self.song['title'],
                self.song['artist'],
                self.song['albumtitle'])

            if self.onStart != None:
                self.onStart()

            # 让线程进入等待状态，等待激活信号
            self.event.wait()
            self.event.clear()

    def pause(self):
        if self.playing:
            self.player.set_state(gst.STATE_PAUSED)
            self.playing = False
            print 'paused'
        else:
            self.player.set_state(gst.STATE_PLAYING)
            self.playing = True
            print 'continue playing'

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

def next(player, event):
    player.set_state(gst.STATE_NULL)
    event.set()

class operation(threading.Thread):
    def __init__(self, num, interval, fm):
        threading.Thread.__init__(self)
        self.thread_num = num
        self.interval = interval
        self.thread_stop = False
        self.fm = fm

    def run(self):
        while not self.thread_stop:
            time.sleep(self.interval)
            p = raw_input("command(n:next,p:pause,l:like,r:remove,c:channels):")
            if p == 'n':
                self.fm.childProcess.cancel()
                self.fm.next()
            elif p == 'p':
                self.fm.pause()
            elif p == 'l':
                self.fm.like()
            elif p == 'r':
                self.fm.remove()
            elif p == 'c':
                channels = self.fm.getChannels()
                for channel in channels:
                    print str(channel['channel_id'])+' '+channel['name_en'].encode('utf8')+' '+channel['name'].encode('utf8')
                channel_id = raw_input("choose channel(q to quit):")
                if channel_id != '':
                    for channel in channels:
                        if channel_id == 'q':
                            print 'quit command'
                            break
                        if str(channel['channel_id']) == channel_id:
                            self.fm.setChannel(string.atoi(channel_id))
                            break
            else:
                print 'wrong command'

    def stop(self):
        self.thread_stop = True



if __name__ == '__main__':
    fm = DoubanfmBase()
    thread1 = operation(1, 1, fm)
    fm.login('gayyzxyx@126.com','q1w2e3p0o9i8.')
    thread1.start()
    fm.run()
