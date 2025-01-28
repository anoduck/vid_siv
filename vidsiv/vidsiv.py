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
import logging
from logging import handlers
from warnings import warn
from conf import parser, args
from getter import GetStuff
from vidproc import ProcessVids


class vidsiv:

    def __init__(self):
        self.args = args.options
        self.res_file = os.path.abspath(self.args.results)
        self.valid = self.args.valid
        self.rdict = {'480': 480, '540': 540, '720': 720,
                      '2k': 1920, '4k': 3840}
        self.target_resolution = self.rdict.get(self.quality)
        self.quality = self.args.quality
        self.zero = self.args.zero
        self.min = self.args.min
        self.duration = self.args.duration
        self.exclude = self.args.exclude

    def siv(self, log):
        self.log = log
        gstuff = GetStuff()
        found_list = gstuff.get_flist(dir=self.args.dir, log=self.log)
        print('Processing Videos... (This may take some time...)')
        vproc = ProcessVids()
        proc_result = vproc.proc_vids(tmpfile=found_list, valid=self.valid,
                                      zero=self.zero, results=self.res_file,
                                      target_resolution=self.target_resolution,
                                      exclude=self.args.exclude, min=self.min,
                                      duration=self.duration, log=self.log)
        if proc_result:
            self.log.info('Processing complete.')
            print('Done!', flush=False)


class Finalize:

    def __init__(self) -> None:
        self.args = args.options
        self.res_file = os.path.abspath(self.args.results)

    def remove_selection(self, log):
        with open(self.res_file, 'r') as res:
            for item in res:
                log.info(f'Removing {item} from system')
                os.remove(item)


def get_log(logfile, loglevel) -> logging.Logger:
    if logfile is None:
        logfile = 'vidsiv.log'
    if loglevel is None:
        loglevel = 'DEBUG'
    if not os.path.exists(logfile):
        open(logfile, 'a').close()
    log = logging.getLogger(__name__)
    if log.hasHandlers():
        log.handlers.clear()
    log_levels = {'DEBUG': logging.DEBUG,
                  'INFO': logging.INFO,
                  'WARNING': logging.WARNING,
                  'ERROR': logging.ERROR,
                  'CRITICAL': logging.CRITICAL}
    if loglevel in log_levels.keys():
        set_level = log_levels[loglevel]
        log.setLevel(set_level)
    else:
        warn('Invalid level. Defaulting to debug')
        log.setLevel(logging.DEBUG)
    handler = handlers.RotatingFileHandler(
        filename=logfile,
        mode='a', maxBytes=75 * 1024,
        backupCount=2,
        encoding='utf-8',
        delay=False)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log = log
    log.info('## ========================================= ##')
    log.info('You have now Started VidSiv')
    log.info('## ========================================= ##')
    log.info('Acquired Logger')
    return log


def main():
    action = args.options.action
    log = get_log(args.options.logfile, args.options.loglevel)
    log.info('VidSiv has started')
    match action:
        case "siv":
            vs = vidsiv()
            vs.siv(log)
        case "finalize":
            final = Finalize()
            final.remove_selection(log)
            exit()
        case "help":
            parser.print_help()
            exit()


if __name__ == '__main__':
    main()
