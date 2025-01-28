# Copyright (c) 2025 Anoduck
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

# Copyright (c) 2024 Anoduck
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import logging
import threading
from logging import handlers
from warnings import warn
import os


class SivLog(threading.Thread):

    def __init__(self, log_file=None, level=None):
        super().__init__()
        self.log_file = log_file
        self.level = level
        self.daemon = True
        self.log = None
        self.start()

    def get_log(self) -> logging.Logger:
        if self.log is not None:
            return self.log
        else:
            if self.log_file is None:
                self.log_file = 'vidsiv.log'
            if self.level is None:
                self.level = 'DEBUG'
            if not os.path.exists(self.log_file):
                open(self.log_file, 'a').close()
            log = logging.getLogger(__name__)
            if log.hasHandlers():
                log.handlers.clear()
            log_levels = {'DEBUG': logging.DEBUG,
                          'INFO': logging.INFO,
                          'WARNING': logging.WARNING,
                          'ERROR': logging.ERROR,
                          'CRITICAL': logging.CRITICAL}
            if self.level in log_levels.keys():
                set_level = log_levels[self.level]
                log.setLevel(set_level)
            else:
                warn('Invalid level. Defaulting to debug')
                log.setLevel(logging.DEBUG)
            handler = handlers.RotatingFileHandler(
                filename=self.log_file,
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

