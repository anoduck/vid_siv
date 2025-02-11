#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2024  Anoduck, The Anonymous Duck

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------
# https://anoduck.mit-license.org
# -----------------------------------------------------------------
import os
from getter import GetStuff
from proclog import SivLog
from vidproc import ProcessVids


class VidSiv:

    def __init__(self, args):
        self.args = args.options
        self.res_file = self.args.results
        self.valid = self.args.valid
        self.rdict = {'480': 480, '540': 540, '720': 720,
                      '2k': 1920, '4k': 3840}
        self.quality = self.args.quality
        self.target_resolution = self.rdict.get(self.quality)
        self.zero = self.args.zero
        self.min = self.args.min
        self.duration = self.args.duration
        self.exclude = self.args.exclude
        self.logfile = self.args.logfile
        self.loglevel = self.args.loglevel
        self.sv = SivLog(self.logfile, self.loglevel)
        self.log = self.sv.get_log()

    def siv(self):
        gstuff = GetStuff()
        found_list = gstuff.get_flist(dir=self.args.dir, log=self.log)
        print('Processing Videos... (This may take some time...)')
        vproc = ProcessVids()
        proc_result = vproc.proc_vids(found_list=found_list, valid=self.valid,
                                      zero=self.zero, results=self.res_file,
                                      target_resolution=self.target_resolution,
                                      exclude=self.args.exclude, min=self.min,
                                      duration=self.duration, log=self.log)
        if proc_result:
            self.log.info('Processing complete.')
            print('Done!', flush=False)


class FinalizeFiles:

    def __init__(self, args):
        self.args = args.options
        self.remfile = self.args.filelist
        self.logfile = self.args.logfile
        self.loglevel = self.args.loglevel
        self.sv = SivLog(self.logfile, self.loglevel)
        self.log = self.sv.get_log()

    def remove_selection(self):
        with open(self.remfile, 'r') as res:
            for item in res:
                self.log.info(f'Removing {item} from system')
                os.remove(item)

