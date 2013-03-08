#!/usr/bin/env python
# -*- coding: utf-8 -*-

import irclib
import time

from google.appengine.ext import db


network = 'chat.freenode.net'
port = 8001
channels = ['#ninja-ide', '#botters', '#bot-testing']

name = 'pyIRC Logger Bot - https://github.com/YatharthROCK/pyIRC/'
nick = 'ninja_logger'
password = 'mndhck'


def channel_key(channel='network'):
    """Constructs a Datastore key for an event entity of given channel"""
    return db.Key.from_path('Channel', channel)


class Handler(object):
    """Contains handlers for IRC events"""

    @staticmethod
    def join(connection, trigger):
        user = trigger.source().split()('!')[0]
        channel = channel_key(trigger.target())

        event = Event.Join(parent=channel)
        event.user = user
        event.put()

    @staticmethod
    def part(connection, trigger):
        user = trigger.source().split()('!')[0]
        channel = channel_key(trigger.target())

        event = Event.Part(parent=channel)
        event.user = user
        event.put()

    @staticmethod
    def pubMessage(connection, trigger):
        user = trigger.source().split('!')[0]
        message = trigger.arguments()[0]
        channel = channel_key(trigger.target())

        event = Event.PubMessage(parent=channel)
        event.user = user
        event.message = message
        event.put()

    @staticmethod
    def topic(connection, trigger):
        user = trigger.source().split('!')[0]
        topic = trigger.arguments()[0]
        channel = channel_key(trigger.target())

        event = Event.Topic(parent=channel)
        event.user = user
        event.topic = topic
        event.put()

    @staticmethod
    def kick(connection, trigger):
        user = trigger.arguments()[0]
        doer = trigger.source()
        channel = trigger.target()

        # if we have been kicked, join again
        if user == nick:
            server.join(channel)

        event = Event.kick(parent=channel)
        event.user = user
        event.doer = doer
        event.put()

    @staticmethod
    def mode(connection, trigger):
        # common stuff
        doer = trigger.source().split('!')[0]
        mode = trigger.arguments()[0]
        channel = channel_key(trigger.target())

        # channel mode
        if len(trigger.arguments()) < 2:
            event = Event.ChannelMode(parent=channel)

       # user mode
        else:
            event = Event.UserMode(parent=channel)
            user = ' '.join(event.arguments()[1:])
            event.user = user

        # finish stuff
        event.doer = doer
        event.mode = mode
        event.put()

    @staticmethod
    def nick(connection, trigger):
        user = trigger.source().split('!')[0]
        nick_ = trigger.target()
        channel = channel_key()

        event = Event.Nick(parent=channel)
        event.user = user
        event.nick = nick_
        event.put()

    @staticmethod
    def quit(connection, trigger):
        user = trigger.source().split('!')[0]
        reason = trigger.arguments()[0]
        channel = channel_key()

        event = Event.Quit(parent=channel)
        event.user = user
        event.reason = reason
        event.put()


class Event(object):
    """Contains Datastore models for IRC events"""

    class Join(db.Model):
        user = db.StringProperty()
        date = db.DateTimeProperty(auto_now_add=True)

    class Part(db.Model):
        user = db.StringProperty()
        date = db.DateTimeProperty(auto_now_add=True)

    class PubMessage(db.Model):
        user = db.StringProperty()
        message = db.StringProperty(multiline=True)
        date = db.DateTimeProperty(auto_now_add=True)

    class Topic(db.Model):
        user = db.StringProperty()
        topic = db.StringProperty()
        date = db.DateTimeProperty(auto_now_add=True)

    class Kick(db.Model):
        user = db.StringProperty()
        doer = db.StringProperty()
        date = db.DateTimeProperty(auto_now_add=True)

    class ChannelMode(db.Model):
        doer = db.StringProperty()
        mode = db.StringProperty()
        date = db.DateTimeProperty(auto_now_add=True)

    class UserMode(db.Model):
        user = db.StringProperty()
        doer = db.StringProperty()
        mode = db.StringProperty()
        date = db.DateTimeProperty(auto_now_add=True)

    class Nick(db.Model):
        user = db.StringProperty()
        nick = db.StringProperty()
        date = db.DateTimeProperty(auto_now_add=True)

    class Quit(db.Model):
        user = db.StringProperty()
        reason = db.StringProperty
        date = db.DateTimeProperty(auto_now_add=True)


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

# comment the following lines out
# if you don't want them echoing into all your channels'' logs
# as IRCd does not provide a "source" for these events
irc.add_global_handler('nick', Handler.nick)
irc.add_global_handler('quit', Handler.quit)

# create and connect server object
server = irc.server()
server.connect(network, port, nick, ircname=name, ssl=False)

# authenticate with NickServ
if password:
    server.privmsg("nickserv", "identify %s" % password)

# wait for the IRCd to accept your password before joining rooms
time.sleep(10)

# join channels
for channel in channels:
    server.join(channel)

# jump into an infinite loop
main = irc.process_forever
if __name__ == '__main__':
    main()