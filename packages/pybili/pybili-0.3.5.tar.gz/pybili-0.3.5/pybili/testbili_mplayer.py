#!/usr/bin/python
#coding=utf-8
import bili
import bili_sender
import bili_config
import sys
import thread
import struct
import time
import json
import os
import mplayer
import random
import threading
import subprocess
import logging

import traceback
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

reload(sys)  
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DIVIDER = '--------------------'

class Music(object):

    def __init__(self, n, s, e): 
        self.name, self.sname, self.ename = n, s, e

    def __str__(self): 
        return self.searchKey()

    def __repr__(self): 
        return self.__str__()
    
    def searchKey(self): 
        return '%s %s %s' % (self.name, self.sname, self.ename)

class DBHelper(object):

    def __init__(self):
        try:
            print('start db...')
            self.client = MongoClient()
            self.db = self.client.music
        except:
            print('mongodb service down!\nto install:[brew install mongodb]\nto start:[brew services start mongodb]')
            self.db = None

    def selectFavorite(self, danmaku):
        if self.db:
            cursor = self.db.fav.find({'user': danmaku.user}).sort([('time', pymongo.ASCENDING)])
            return [d['name'] for d in cursor]

    def removeFavorite(self, danmaku, name):
        if self.db:
            cursor = self.db.fav.find({'user': danmaku.user}).sort([('time', pymongo.DESCENDING)])
            i = 0
            for d in cursor:
                i += 1
                if i >= 9:
                    try:
                        self.db.fav.delete_one({'_id': ObjectId(d['_id'])})
                    except:
                        logger.exception('removeFavoriteInDB exception', danmaku)
                        #traceback.print_exc()

    def insertFavorite(self, danmaku, name):
        if self.db:
            favs = self.selectFavorite(danmaku)
            logger.debug(favs)
            if len(favs) >= 9:
                self.removeFavorite(danmaku, name)

            self.db.fav.insert_one({
                'user':danmaku.user,
                'name':name,
                'time':time.strftime('%y%m%d-%H%M%S', danmaku.time)
                })
            return self.selectFavorite(danmaku)

class Player(object):
    p = mplayer.Player()
    home_path = os.path.expanduser("~")
    lib_path = home_path + '/Music/lib/'
    all_music = []
    to_play_lst = []
    state = 'play'
    skip = False
    LOCK = threading.Lock()
    db = DBHelper()

    def __init__(self, ui):
        self.loadMusic()
        self.ui = ui
        self.ui.to_play_list = to_play_lst
        print 'load musics... finish'
        thread.start_new_thread(self.musicThread, ())

    def getCurrentMusic(self):
        return self.p.filename[:-4]

    def loadMusic(self):
        origin_music = [f[:-4] for f in os.listdir(self.lib_path) if f[-4:] == '.mp3']
        with open('%s/.pybili.ti' % self.home_path, 'w') as f:
            f.write('\n'.join(origin_music))
        
        sub = subprocess.Popen('opencc -i %s/.pybili.ti -o %s/.pybili.to -c t2s.json' % (self.home_path, self.home_path), shell=True)
        sub.wait()

        with open('%s/.pybili.to' % self.home_path, 'r') as f:
            lst = f.read().split('\n')
            self.all_music = [Music(n,s,n) for n, s in zip(origin_music, lst)]
           
        logger.debug(self.all_music)

    def getToPlayList(self):
        return self.to_play_lst

    def playMusic(self, name):
        logger.debug('player state:', self.p.is_alive(), '\nself state:', self.state)
        while self.state != 'play': time.sleep(1)
        self.p.stop()
        self.p.loadfile(self.lib_path + name + '.mp3')
        time.sleep(0.5)
        logger.debug('playing', self.p.filename)
        self.ui.playing = self.p.filename[:-4]
        self.ui.update()

        self.p.volume = 8
        length = self.p.length
        self.p.pause()
        logger.debug('length', length)
        for i in xrange(int(length)):
            if self.skip:
                logger.debug('skip play ', name, self.p.filename)
                self.p.stop()
                self.skip = False
                break
            time.sleep(1)
        else:
            logger.debug('finish play ', name, self.p.filename)

    def musicThread(self):
        while 1:
            if self.to_play_lst:
                self.LOCK.acquire()
                u, music = self.to_play_lst.pop(0)
                self.LOCK.release()
                self.playMusic(music.name)
            else:
                music = random.choice(self.all_music)
                self.playMusic(music.name)

    def match(self, key, music):
        if key in music.lower(): return True
        keys = key.split(' ')
        if len(keys) > 1: 
            if all(k in music.lower() for k in keys): return True

    def search(self, key):
        result = []
        for i, m in enumerate(self.all_music):
            if self.match(key, m.searchKey()): result += [(i+1, m.name)]
        if len(result) == 1:
            self.addToPlayList(result[0][0])
        return result

    def addToPlayListByName(self, name):
        to_add = Music(name, name, name)
        self.LOCK.acquire()
        if len(self.to_play_lst) < 10:
            if not any([1 for _, music in self.to_play_lst if music.name == to_add.name]):
                self.to_play_lst += [(self.cur_user, to_add)]
        self.LOCK.release()

    def addToPlayList(self, i):
        to_add = self.all_music[i-1]
        self.addToPlayListByName(to_add.name)

    def getFavList(self, danmaku):
        return self.db.selectFavorite(danmaku)

class ConsoleUI(object):

    def __init__(self):
        self.cur_user
        self.playing = None
        self.to_play_list = None
        self.search_key = None
        self.search_result = None
        self.fav_result = None

    def update(self):
        self.clear()
        self.printToPlay()
        if self.cur_user: 
            print('当前操作者： %s' % self.cur_user)
            print('发送 \'搜索 关键字\' 搜索列表，发送 \'点歌 ID\' 完成点歌。发送 \'退出\' 结束点歌。请在五分钟内完成全部操作哦～')
        if self.search_result: self.printSearch()
        if self.fav_result: self.printFav()

    def printSearch(self)
        print('搜索 %s 的结果列表：' % self.seach_key)
        for i, t in self.search_result: print('%d\t: %s' % (i, t))

    def printToPlay(self):
        print('当前待播放列表：')
        for u, m in self.to_play_list: print('%s 点了\t: %s' % (u, m.name))
    
    def clear(self): 
        print("\033c")
        print('正在播放:  %s' % self.playing)

    def printFav(self):
        print(DIVIDER)
        print('%s的收藏列表: ' % self.cur_user)
        for i, name in enumerate(self.fav_result):
            print('%d, %s' % (i+1, name))
        self.fav_result = None

    def printTimeout(self):
        print('五分钟到了哦～')

class DanmakuHandler(bili.SimpleDanmakuHandler):
    timer = None
    cur_user = None
    config = bili_config.Config()
    sender = bili_sender.Sender(config.cookies)

    def __init__(self, roomid):
        self.roomid = roomid
        self.ui = ConsoleUI()
        self.p = Player(self.ui)

    def localTimerThread(self, user):
        if self.cur_user == user: 
            self.cur_user = None
            self.ui.cur_user = None
            self.ui.update()

    def search(self, key):
        key = key[6:].strip().lower()
        result = []
        for i, m in enumerate(self.all_music):
            if self.match(key, m.searchKey()): result += [(i+1, m.name)]
        if len(result) == 0: 
            self.sender.sendDanmaku(self.roomid, 'Sorry...这里没有对应的歌')
        elif len(result) == 1:
            self.p.addToPlayList(result[0][0])
        else:
            if self.cur_user != 'klikli': self.sender.sendDanmaku(self.roomid, '搜索 %s 中...' % key)
            r = self.p.search(key)
            self.ui.search_key = key
            self.ui.search_result = r
            self.ui.update()
        
    def addToPlayListByName(self, name):
        to_add = Music(name, name, name)
        self.LOCK.acquire()
        if len(self.to_play_lst) < 10:
            if not any([1 for _, music in self.to_play_lst if music.name == to_add.name]):
                self.to_play_lst += [(self.cur_user, to_add)]
        self.LOCK.release()
        self.sender.sendDanmaku(self.roomid, '[%s...]点歌成功' % to_add.name[:15])
        self.ui.update()

    def addToPlayList(self, i):
        to_add = self.all_music[i-1]
        self.addToPlayListByName(to_add.name)

    def handleDanmaku(self, danmaku):
        super(DanmakuHandler, self).handleDanmaku(danmaku)
        if hasattr(danmaku, 'user') and hasattr(danmaku, 'text'):
            user, manager, content = danmaku.user, danmaku.isManager, danmaku.text
            if manager and content in ['切歌']:
                self.p.skip = True
            elif content in ['查看收藏','收藏列表']:
                if (not self.cur_user) or (self.cur_user == user):
                    self.ui.fav_result = self.db.selectFavorite(danmaku)
                    self.ui.update()
            elif content[:6] in ['收藏']:
                try:
                    if len(content) == 6: to_add = self.p.getCurrentMusic()
                    else: 
                        i = int(content[6:].strip())
                        to_add = self.p.all_music[i-1].name
                    self.p.insertFavorite(danmaku, to_add)
                    self.sender.sendDanmaku(self.roomid, '[%s...]收藏成功' % to_add[:15])
                except Exception, e:
                    #traceback.print_exc()
                    self.sender.sendDanmaku(self.roomid, '请输入正确的指令哦')
            elif content[:6] in ['点歌', '點歌']: 
                if not self.cur_user:
                    self.cur_user = user
                    self.timer = threading.Timer(300, self.localTimerThread, (user, ))
                    self.timer.start()
                    self.sender.sendDanmaku(self.roomid, '%s开始点歌～' % self.cur_user)
                    self.ui.cur_user = user
                    self.ui.update()

                if self.cur_user == user:
                    k = content[6:].strip()
                    if not k: return
                    try:
                        if k[0] == '@': # play from favorite
                            i = int(k[1:])
                            favs = self.p.selectFavorite(danmaku)
                            self.p.addToPlayListByName(favs[i-1])
                            self.ui.update()
                        else:
                            if k.isdigit():  # play by id
                                self.p.addToPlayList(int(k))
                                self.ui.update()
                            else:  # search
                                self.search(k)
                    except Exception, e:
                        logger.warn(e)
                        self.sender.sendDanmaku(self.roomid, '请输入正确的点歌指令哦')
                else:
                    self.sender.sendDanmaku(self.roomid, '%s正在点歌, 请等一下哦' % self.cur_user)
            elif user == self.cur_user and content[:6] in ['搜索']:
                self.search(key)
            elif user == self.cur_user and content.lower() in ['退出', 'exit', '结束', 'quit']: 
                self.sender.sendDanmaku(self.roomid, '欢迎再来点歌哦～')
                self.cur_user = None
                if self.timer: self.timer.cancel()
                self.update(None)
            #elif user == 'klikli' and content == 'reload':
            #    self.p.loadMusic()
            #    print('重新加载歌曲库...')

def main():
    argv = sys.argv
    roomid = 90012
    if len(argv) == 2:
        roomid = int(argv[1])

    danmakuHandler = DanmakuHandler(roomid)
    py = bili.BiliHelper(roomid, danmakuHandler)
    while 1:
        cmd = raw_input().strip()
        if cmd == 'p':
            pass
            #danmakuHandler.p.pause()
            #if danmakuHandler.state == 'pause': 
            #    danmakuHandler.state = 'play'
            #    print 'play'
            #elif danmakuHandler.state == 'play': 
            #    danmakuHandler.state = 'pause'
            #    print 'pause'
        elif cmd == 'r':
            danmakuHandler.p.loadMusic()
        else:
            danmakuHandler.p.search(cmd)

                        
if __name__ == '__main__':
    main()
