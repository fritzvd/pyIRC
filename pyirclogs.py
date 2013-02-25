#! /usr/bin/env python

import os

network = 'irc.freenode.net'
port = 8001
nick = 'pyIRCBot' ## Change this, of course.
channels = ['#botters','#testing-room'] # LOWERCASE ONLY
name = 'IRC Log Bot - http://code.google.com/p/pyirclogs/'
password = 'nickserv-password'

if os.name == 'nt':
    LOG_PATH = 'C:/logs/'
else:
    LOG_PATH = '/path/to/logs/'


__author__ = "Base code designed by Chris Oliver <excid3@gmail.com>, heavily modified by Harry Strongburg <lolwutaf2@gmail.com>"
__version__ = "1.1 Stable"
__date__ = "October 18 2009"
__copyright__ = "Creative Commons Attribution Non-Commercial Share Alike (BY-NC-SA); by Chris Oliver & Harry Strongburg"
__license__ = "GPL2"

# Imports
from time import strftime
import irclib
import time

class LogFile(object):
    def __init__(self,path,extention='.txt',constant_write=False,mode=3,new_folders=True):
        # path = path to store shit
        # extention = log extention
        # constant_write = keep the file open inbetween writes or
        #                  open & close it every time.
        # mode = 1/2/3
        #        1 = save file name as time.time() value
        #        2 = save file as a human readable value
        #        3 = save it as "log_file.log"
        self.path = path
        self.mode = mode
        self.keep_open = constant_write
        self.extention = extention
        self.file = None
        self.name = ''
        self._total_name = ''
        self.new_folders=new_folders
        self._init_file()

    def close(self,message=''):
        # close the log file
        if message:
            self.write(message)
        if self.keep_open:
            self.file.close()
        self.keep_open = True
        self.file = None        

    def write(self,message,prefix=True):
        if self.file == None:
            raise Exception('File has been closed, oh noes!')
        if not self.keep_open:
            self.file = open(self._total_name,'a+')
        if prefix:
            _prefix = '[%s] '%time.strftime('%H:%M:%S')
        else:
            _prefix = ''

        self.file.write(_prefix+message+'\n')

        if not self.keep_open:
            self.file.close()

    def _init_file(self):
        if self.new_folders:
            self.path = self.path + time.strftime("%Y/%m/")
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            
        # Create our shit
        if self.mode == 1:
            self.name = str(time.time())
        elif self.mode == 2:
            self.name = time.strftime("%d")
        else:
	    self.name = time.strftime("%d")
            ##self.name = time.strftime("%H")

        self._total_name = self.path+self.name+self.extention
        
        if os.path.isfile(self._total_name):
            self.file = open(self._total_name,'a+')
        else:
            self.file = open(self._total_name,'w')
            
        self.write('[IRC logfile - Started %s]'%time.ctime(),False)

class LogFileManager(object):
    def __init__(self,values):
        # Values = list of keys for the LogFiles
        self.value = values
        self.logs = {}
        for value in self.value:
            self.logs[value] = LogFile(LOG_PATH+value[1:]+'/')

    def reload_logs(self):
        for value in self.value:
            self.logs[value] = LogFile(LOG_PATH+value[1:]+'/')

    def write(self,name,text):
        self.logs[name.lower()].write(text)

    def write_all(self,text):
        for log in self.logs:
            self.logs[log].write(text)
    
    def close(self,name):
        self.logs[name.lower()].close()

    def close_all(self):
        for log in self.logs:
            self.logs[log].close()

        
# Connection information

def _real_handler(message,name=None):
    global current_hour,manager
    now_hour = time.strftime('%H')
    if now_hour == current_hour:
        if name:
            manager.write(name,message)
        else:
            manager.write_all(message)
    else:
        current_hour = now_hour
        manager.close_all()
        manager.reload_logs()
        if name:
            manager.write(name,message)
        else:
            manager.write_all(message)

def handleJoin(connection,event): # Join notifications
    _real_handler(event.source().split('!')[0] + ' has joined ' + event.target(),name=event.target())

def handlePart(connection,event): # Join notifications
    _real_handler(event.source().split('!')[0] + ' has left ' + event.target(),name=event.target())

def handlePubMessage(connection, event): # Any public message
    _real_handler(event.source().split ('!')[0] + ': ' + event.arguments()[0], name=event.target())

def handleTopic(connection,event):
    _real_handler(event.source().split( '!' )[0] + ' has set the topic to "' + event.arguments()[0],name=event.target())

def handleQuit(connection,event):
    _real_handler(event.source().split ( '!' ) [ 0 ] + ' has disconnected : ' + event.arguments() [ 0 ])

def handleKick(connection,event):
    if nick == event.arguments() [ 0 ]:
        server.join(event.target())
    _real_handler(event.arguments() [ 0 ] + ' has been kicked by ' +event.source().split ( '!' ) [ 0 ] + ': ' + event.arguments()[ 1 ],name=event.target())

def handleMode ( connection, event ):

   # Channel mode
   if len ( event.arguments() ) < 2:
      _real_handler(event.source().split ( '!' ) [ 0 ] + ' has altered the channel\'s mode: ' + event.arguments() [ 0 ],name=event.target())

   # User mode
   else:
      _real_handler(event.source().split ( '!' ) [ 0 ] + ' has altered '+ ' '.join(event.arguments() [ 1: ]) + '\'s mode: ' + event.arguments()[ 0 ],name=event.target())

def handleNick(connection,event):
    _real_handler(event.source().split('!')[0] +' changed nick to ' + event.target())
    

#(self,path,extention='.log',constant_write=False,mode=2)
manager = LogFileManager(channels)
current_hour = time.strftime('%H')

# Create an IRC object
irclib.DEBUG = 1
irc = irclib.IRC()

irc.add_global_handler('join', handleJoin)
irc.add_global_handler('part',handlePart)
irc.add_global_handler('pubmsg', handlePubMessage)
irc.add_global_handler('topic', handleTopic)########################################################################
#irc.add_global_handler('quit', handleQuit) ## Quits and Nick changes can NOT be handled by the bot at this time, ##
irc.add_global_handler('kick', handleKick)  ## due to the fact there is no "source" for the change in the ircd;   ##
irc.add_global_handler('mode', handleMode)  ## hence if you log multiple rooms, a quit or nickname change will    ##
#irc.add_global_handler('nick',handleNick)  ##  echo into the logs for all your rooms, which is not wanted.       ##
                                            ########################################################################

# Create a server object, connect and join the channel
server = irc.server()
server.connect(network, port, nick, ircname=name,ssl=False)
if password: server.privmsg("nickserv","identify %s"%password)
time.sleep(10) ## Waiting on the IRCd to accept your password before joining rooms
for channel in channels:
    server.join(channel)

# Jump into an infinite loop
irc.process_forever()
