#!/usr/bin/env python
# -*- coding: utf-8 -*-
from alive_progress import alive_bar
import glob
import magic
import os


class GetStuff:

    def find_videos(self, dir_path, bar):
        found_files = []
        glob_list = glob.glob(dir_path + '/**/*', recursive=True)
        magik = magic.Magic(mime=True)
        for item in glob_list:
            item_path = os.path.abspath(item)
            if os.path.isfile(item_path):
                try:
                    mt = magik.from_file(item)
                    mt_split = mt.split('/')
                    mime = mt_split[0]
                    self.log.debug('MT Type: {}'.format(str(type(mime))))
                    self.log.debug('MT Value: {}'.format(mime))
                    if mime == 'video':
                        found_files.append(item_path)
                        bar()
                    else:
                        bar()
                        self.log.debug('return item is: {}'.format(item_path))
                except magic.MagicException:
                    self.log.debug('Magic Exception: {}'.format(item_path))
                    bar()
                    pass
                else:
                    bar()
        return set(found_files)

    def get_total(self, dir_path):
        file_list = glob.glob(dir_path + '/**/*', recursive=True)
        total = len(file_list)
        return total

    def get_flist(self, dir, log):
        self.log = log
        self.log.info('Generating file list recursively')
        self.log.info('Generating Current Context')
        dir_path = os.path.abspath(dir)
        self.log.debug('Directory path: {}'.format(dir_path))
        with alive_bar() as bar:
            file_list = self.find_videos(dir_path, bar)
            return file_list
