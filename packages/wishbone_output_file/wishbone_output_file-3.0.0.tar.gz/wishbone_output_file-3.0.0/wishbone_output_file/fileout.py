#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  fileout.py
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

from wishbone.module import OutputModule
from gevent.fileobject import FileObjectThread
from gevent.lock import Semaphore

# TODO(smetj): Implement way to keep files open when writing to improve speed.


class FileOut(OutputModule):
    '''
    Writes events to a file.

    Parameters::

        - directory(str)("./")
           |  The directory to write the files to.

        - filename(str)("wishbone.out")*
           |  The filename to use.

        - native_events(bool)(False)
           |  Submit Wishbone native events.

        - overwrite(bool)(False)

           |  If `True` overwrites each time the content otherwise appends to
           |  the end of the file.

        - parallel_streams(int)(1)
           |  The number of outgoing parallel data streams.

        - payload(str)(None)
           |  The string to submit.
           |  If defined takes precedence over `selection`.

        - selection(str)("data")*
           |  The part of the event to submit externally.
           |  Use an empty string to refer to the complete event.


    Queues::

        - inbox
           |  Incoming messages

    '''

    def __init__(self, actor_config, directory="./", filename="wishbone", native_events=False, parallel_streams=1, payload=None, selection='data', overwrite=False):
        OutputModule.__init__(self, actor_config)
        self.pool.createQueue("inbox")
        self.registerConsumer(self.consume, "inbox")
        self.file_lock = Semaphore()

    def consume(self, event):

        data = self.getDataToSubmit(event)
        data = self.encode(data)

        with self.file_lock:
            # TODO(smetj): Allow to write concurrently to <self.kwargs.parallel_streams> number of files.

            if event.kwargs.overwrite:
                with open("%s/%s" % (event.kwargs.directory, event.kwargs.filename), "w") as f:
                    fo = FileObjectThread(f)
                    fo.write(data)
                    fo.close()

            else:
                with open("%s/%s" % (event.kwargs.directory, event.kwargs.filename), "a") as f:
                    fo = FileObjectThread(f)
                    fo.write(data)
                    fo.close()

            f.close()
