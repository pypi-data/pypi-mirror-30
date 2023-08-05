#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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

import os
from gevent import sleep
from wishbone.error import ModuleNotReady
from .structured_data_file import StructuredDataFile


class ModuleConnectionMock(object):

    '''
    A class which can be initially assigned to a variable which is going to
    hold a future connection related object/method. If the actual connection
    to the upstream server has not been finished yet, we have at least a
    predictable error.
    '''

    def __init__(self, message="Not connected"):

        self.message = message

    def __getattr__(self, name):

        raise ModuleNotReady(self.message)


class PIDFile():

    '''
    Handles all PIDfile interactions.
    '''

    def __init__(self, location):
        self.location = location

    def alive(self):
        '''Returns True if at least 1 PID in pidfile is alive.'''

        for pid in self.__readPIDFile():
            if self.__isAlive(pid):
                return True
        return False

    def create(self, pids=[]):
        '''Creates the pidfile containing the provided list of pids.'''

        if self.exists():
            if self.valid():
                raise Exception("Pidfile exists and at least one process running.")
            else:
                self.__deletePIDFile()

        self.__writePIDFile(pids)

    def cleanup(self):
        '''Deleted PID file if possible.'''
        if self.exists():
            self.__deletePIDFile()

    def exists(self):
        '''Returns True if file exists.'''

        return os.path.isfile(self.location)

    def read(self):
        '''Returns the content of the pidfile'''

        return self.__readPIDFile()

    def sendSigint(self, pid):
        '''Sends sigint to PID.'''

        try:
            os.kill(int(pid), 2)
        except:
            pass

        while self.__isAlive(pid):
            sleep(1)

    def valid(self):
        '''Returns True at least one PID within pidfile is still alive.'''

        try:
            for pid in self.__readPIDFile():
                if self.__isAlive(pid):
                    return True
            return False
        except Exception:
            return False

    def __isAlive(self, pid):
        '''Verifies whether pid is still alive.'''

        try:
            os.kill(int(pid), 0)
            return True
        except:
            False

    def __writePIDFile(self, pids=[]):
        '''Writes a list pids to the file.'''

        with open(self.location, 'w') as pidfile:
            for pid in pids:
                pidfile.write("%s\n" % (pid))

    def __readPIDFile(self):
        '''Returns a list of pids values the file contains.'''

        with open(self.location, 'r') as pidfile:
            pids = pidfile.readlines()

        return [int(x) for x in pids]

    def __deletePIDFile(self):
        '''Unconditionally deletes the pidfile.'''

        if os.path.isfile(self.location):
            os.remove(self.location)
