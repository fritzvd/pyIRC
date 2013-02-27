# -*- coding: utf-8 -*-

import os
import irclib
import time

network = 'chat.freenode.net'
port = 8001
channels = ['#ninja-ide', '#botters']

name = 'IRC Log Bot - https://github.com/YatharthROCK/ninja-ide-irc/blob/master/LICENSE.html'
nick = 'ninja_logger'
password = 'mndhck'

if os.name == 'nt':
    LOG_PATH = 'D:/IRC/logs'
else:
    LOG_PATH = './logs/'


class LogFile(object):

    def __init__(self, path, extention='.txt',
    constant_write=False, mode=2, new_folders=True):
        self.path = path
        self.extention = extention
        self.new_folders = new_folders

        # keep file open between writes or open & close it every time
        self.keep_open = constant_write

        # mode can be:-
        #    1: save file name as time.time() value
        #    2: save file as a human readable value
        #    3: save it as `log_file.log`
        self.mode = mode

        # init other vars
        self.file = None
        self.name = ''
        self._total_name = ''

        self._init_file()

    def _init_file(self):
        if self.new_folders:
            self.path += time.strftime('%Y/%m/')
            if not os.path.exists(self.path):
                os.makedirs(self.path)

        if self.mode == 1:
            self.name = str(time.time())
        elif self.mode == 2:
            self.name = time.strftime('%d')
        elif self.mode == 3:
            self.name = 'logfile'
        else:
            raise Exception('invalid value for mode: ' + str(self.mode))

        self._total_name = self.path + self.name + self.extention

        if os.path.isfile(self._total_name):
            self.file = open(self._total_name, 'a+')
        else:
            self.file = open(self._total_name, 'w')

        self.write('[IRC logfile - Started %s]' % time.ctime(), False)

    def write(self, message, prefix=True):
        if self.file is None:
            raise Exception('File has been closed, oh noes!')
        if not self.keep_open:
            self.file = open(self._total_name, 'a+')

        _prefix = '[%s] ' % time.strftime('%H:%M:%S') if prefix else ''
        self.file.write(_prefix + message + '\n')

        if not self.keep_open:
            self.file.close()

    def close(self, message=''):
        if message:
            self.write(message)
        if self.keep_open:
            self.file.close()
        self.keep_open = True
        self.file = None


class LogFileManager(object):

    def __init__(self, values):
        self.values = values
        self.logs = {}

        self.reload_logs()

    def reload_logs(self):
        for value in self.values:
            self.logs[value] = LogFile(LOG_PATH + value[1:] + '/')

    def write(self, log, message):
        self.logs[log.lower()].write(message)

    def write_all(self, message):
        for log in self.logs:
            self.write(log, message)

    def close(self, log):
        self.logs[log.lower()].close()

    def close_all(self):
        for log in self.logs:
            self.close(log)


class Handler(object):

    @staticmethod
    def _real(message, name=None):
        global current_hour, manager
        now_hour = time.strftime('%H')
        if now_hour == current_hour:
            if name:
                manager.write(name, message)
            else:
                manager.write_all(message)
        else:
            current_hour = now_hour
            manager.close_all()
            manager.reload_logs()
            if name:
                manager.write(name, message)
            else:
                manager.write_all(message)

    @staticmethod
    def join(connection, event):
        Handler._real(event.source().split('!')[0] + ' has joined ' + event.target(),
                      name=event.target())

    @staticmethod
    def part(connection, event):
        Handler._real(event.source().split('!')[0] + ' has left ' + event.target(),
                      name=event.target())

    @staticmethod
    def pubMessage(connection, event):
        Handler._real(event.source().split('!')[0] + ': ' + event.arguments()[0],
                      name=event.target())

    @staticmethod
    def topic(connection, event):
        Handler._real(event.source().split('!')[0] + ' has set the topic to "' + event.arguments()[0],
                      name=event.target())

    @staticmethod
    def quit(connection, event):
        Handler._real(event.source().split('!')[0] + ' has quit ' + event.arguments()[0])

    @staticmethod
    def kick(connection, event):
        if nick == event.arguments()[0]:
            server.join(event.target())
        Handler._real(event.arguments()[0] + ' has been kicked by ' + event.source().split('!')[0] + ': ' + event.arguments()[1],
                      name=event.target())

    @staticmethod
    def mode(connection, event):
       # channel mode
        if len(event.arguments()) < 2:
            Handler._real(event.source().split('!')[0] + " has altered the channel's mode: " + event.arguments()[0],
                          name=event.target())
       # user mode
        else:
            Handler._real(event.source().split('!')[0] + ' has altered ' + ' '.join(event.arguments()[1:]) + "'s mode: " + event.arguments()[0],
                          name=event.target())

    @staticmethod
    def nick(connection, event):
        Handler._real(event.source().split('!')[0] + ' changed nick to ' + event.target())


# init vars
manager = LogFileManager(channels)
current_hour = time.strftime('%H')

# create IRC object
irclib.DEBUG = 1
irc = irclib.IRC()

# connect handlers
irc.add_global_handler('join', Handler.join)
irc.add_global_handler('part', Handler.part)
irc.add_global_handler('pubmsg', Handler.pubMessage)
irc.add_global_handler('topic', Handler.topic)
irc.add_global_handler('kick', Handler.kick)
irc.add_global_handler('mode', Handler.mode)

# can't be handled by the bot at this time as there's no "source" for the change ir the ircd
# hence, if you log multiple rooms, a quit or nickname change will echo into the logs for all your rooms, which is not wanted
# irc.add_global_handler('nick', Handler.nick)
# irc.add_global_handler('quit', Handle.quit)

# create server object, connect and join channels
server = irc.server()
server.connect(network, port, nick, ircname=name, ssl=False)
if password:
    server.privmsg("nickserv", "identify %s" % password)
time.sleep(10)  # wait for the IRCd to accept your password before joining rooms
for channel in channels:
    server.join(channel)

# jump into an infinite loop
irc.process_forever()