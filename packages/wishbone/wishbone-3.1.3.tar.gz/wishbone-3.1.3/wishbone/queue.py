#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  queue.py
#
#  Copyright 2018 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from uuid import uuid4
from gevent.queue import Queue as Gevent_Queue
from wishbone.error import ReservedName, QueueMissing, QueueFull, QueueEmpty
from time import time
from gevent.queue import Empty, Full
from gevent import sleep
from types import SimpleNamespace


class QueuePool():

    RESERVED_QUEUES = [
        '_failed',
        '_success',
        '_logs',
        '_metrics'
    ]

    def __init__(self, size):
        self.__size = size
        self.queue = SimpleNamespace()
        self.queue._metrics = Queue(size)
        self.queue._logs = Queue(size)
        self.queue._success = Queue(size)
        self.queue._failed = Queue(size)

    def listQueues(self, names=False, default=True):
        '''returns the list of queue names from the queuepool.
        '''

        if default:
            blacklist = []
        else:
            blacklist = self.RESERVED_QUEUES

        for m in list(self.queue.__dict__.keys()):
            if m not in blacklist:
                if not names:
                    yield getattr(self.queue, m)
                else:
                    yield m

    def createQueue(self, name):
        '''Creates a Queue.'''

        if name in self.RESERVED_QUEUES or name.startswith("_"):
            raise ReservedName("%s is an invalid queue name." % (name))

        setattr(self.queue, name, Queue(self.__size))

    def createSystemQueue(self, name):
        '''
        Creates a queue starting with _ which is forbidden by users as special
        system queues are prefixed with '_'.

        This method should normally never be used directly because of user
        input.  It's the Wishbone framework itself which should make system
        related queues.

        Args:
            name (str): The name of the queue (should start with _)
        '''

        setattr(self.queue, name, Queue(self.__size))

    def hasQueue(self, name):
        '''Returns <True> when queue with <name> exists.'''

        try:
            getattr(self.queue, name)
            return True
        except:
            return False

    def getQueue(self, name):
        '''Convenience funtion which returns the queue instance.'''

        try:
            return getattr(self.queue, name)
        except:
            raise QueueMissing("Module has no queue %s." % (name))

    def join(self):
        '''Blocks until all queues in the pool are empty.'''
        counter = 0
        for queue in self.listQueues():
            while queue.qsize() != 0:
                sleep(0.2)
                counter += 1
                if counter == 5:
                    break


class Queue():

    '''A queue used to organize communication messaging between Wishbone Actors.

    Parameters:

        - max_size (int):   The max number of elements in the queue.
                            Default: 1

    When a queue is created, it will drop all messages. This is by design.
    When <disableFallThrough()> is called, the queue will keep submitted
    messages.  The motivation for this is that when is queue is not connected
    to any consumer it would just sit there filled and possibly blocking the
    chain.

    The <stats()> function will reveal whether any events have disappeared via
    this queue.

    '''

    def __init__(self, max_size=1):
        self.max_size = max_size
        self.id = str(uuid4())
        self.__q = Gevent_Queue(max_size)
        self.__in = 0
        self.__out = 0
        self.__dropped = 0
        self.__cache = {}

        self.put = self.__fallThrough

    def clean(self):
        '''Deletes the content of the queue.
        '''
        self.__q = Gevent_Queue(self.max_size)

    def disableFallThrough(self):
        self.put = self.__put

    def dump(self):
        '''Dumps the queue as a generator and cleans it when done.
        '''

        while True:
            try:
                yield self.get(block=False)
            except QueueEmpty:
                break

    def empty(self):
        '''Returns True when queue and unacknowledged is empty otherwise False.'''

        return self.__q.empty()

    def enableFallthrough(self):
        self.put = self.__fallThrough

    def get(self, block=True):
        '''Gets an element from the queue.'''

        try:
            e = self.__q.get(block=block)
        except Empty:
            raise QueueEmpty("Queue is empty.")
        self.__out += 1
        return e

    def rescue(self, element):

        self.__q.put(element)

    def size(self):
        '''Returns the length of the queue.'''

        return self.__q.qsize()

    def stats(self):
        '''Returns statistics of the queue.'''

        return {"size": self.__q.qsize(),
                "in_total": self.__in,
                "out_total": self.__out,
                "in_rate": self.__rate("in_rate", self.__in),
                "out_rate": self.__rate("out_rate", self.__out),
                "dropped_total": self.__dropped,
                "dropped_rate": self.__rate("dropped_rate", self.__dropped)
                }

    def __fallThrough(self, element):
        '''Accepts an element but discards it'''

        self.__dropped += 1
        del(element)

    def __put(self, element):
        '''Puts element in queue.'''

        try:
            self.__q.put(element)
            self.__in += 1
        except Full:
            raise QueueFull("Queue full.")

    def __rate(self, name, value):

        if name not in self.__cache:
            self.__cache[name] = {"value": (time(), value), "rate": 0}
            return 0

        (time_then, amount_then) = self.__cache[name]["value"]
        (time_now, amount_now) = time(), value

        if time_now - time_then >= 1:
            self.__cache[name]["value"] = (time_now, amount_now)
            self.__cache[name]["rate"] = (amount_now - amount_then) / (time_now - time_then)

        return self.__cache[name]["rate"]
