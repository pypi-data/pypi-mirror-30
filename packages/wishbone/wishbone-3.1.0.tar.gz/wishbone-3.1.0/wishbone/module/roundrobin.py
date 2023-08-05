#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
#  roundrobin.py
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

from wishbone.actor import Actor
from wishbone.module import FlowModule
from itertools import cycle
from random import randint


class RoundRobin(FlowModule):

    '''**Round-robins incoming events to all connected queues.**

    Create a "1 to n" relationship between queues.  Events arriving in inbox
    are then submitted in a roundrobin (or randomized) fashion to the
    connected queues.  The outbox queue is non existent.

    Parameters::

        - randomize(bool)(False)
            |  Randomizes the queue selection instead of going round-robin
            |  over all queues.


    Queues::

        - inbox
           |  Incoming events
    '''

    def __init__(self, actor_config, randomize=False):
        Actor.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")

    def preHook(self):

        self.destination_queues = []
        for queue in self.pool.listQueues(names=True):
            if queue not in ["_failed", "_success", "_metrics", "_logs"]:
                self.destination_queues.append(queue)

        if not self.kwargs.randomize:
            self.cycle = cycle(self.destination_queues)
            self.chooseQueue = self.__chooseNextQueue
        else:
            self.chooseQueue = self.__chooseRandomQueue

    def consume(self, event):
        queue = self.chooseQueue()
        self.submit(event, queue)

    def __chooseNextQueue(self):
        return next(self.cycle)

    def __chooseRandomQueue(self):
        index = randint(0, len(self.destination_queues) - 1)
        return self.destination_queues[index]
