#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import ffmpeg
from alive_progress import alive_it


class ProcessVids:

    def __init__(self):
        self.res_ret = ''
        self.pos = 0

    def zero_sum(self, item, fsize, log):
        if fsize == 0:
            log.info('Deleting {} due to zero size'.format(item))
            self.add_item(item)
            return True

    def check_valid(self, item, log):
        err = (
                ffmpeg
                .input(item)
                .output('/dev/null', format='null')
                .run(capture_stdout=True)
                )
        log.info(f'Return from valid check: {err}')
        if err:
            if item not in self.res_ret:
                log.info('added {} to removal list for corrupt file'.format(item))
                self.add_item(item)
        return True

    def check_size(self, item, fsize, log):
        if self.min_size > fsize:
            if item not in self.res_ret:
                log.info('added {} to removal list for file size'.format(item))
                self.add_item(item)
        return True

    def check_resolution(self, item, vidstream, log):
        if 'width' in vidstream:
            fwidth = vidstream.get('width')
            if self.target_resolution > fwidth:
                if item not in self.res_ret:
                    self.add_item(item)
                    log.info('added {} to removal list for resolution size.'.format(item))
        return True

    def check_duration(self, item, vidstream, log):
        vid_duration = vidstream.get('duration')
        if not vid_duration is None:
            fdur = float(vidstream.get('duration'))
            if self.min_dur > fdur:
                if item not in self.res_ret:
                    log.info('added {} to removal list for duration'.format(item))
                    self.add_item(item)
            return True
        else:
            self.add_item(item)
            return True

    def add_item(self, item):
        self.log.debug(f'File cursor position before opening file is: {self.pos}')
        with open(self.results, mode='a', encoding='utf-8') as writ:
            writ.seek(self.pos)
            writ.write(item)
            writ.write('\n')
            self.pos = writ.tell()
            writ.close()
        self.log.debug(f'File cursor position after write is: {self.pos}')
        self.log.debug(f'Added {item} to removal file')

    def build_exclist(self, found_list):
        if self.exclude_file != "":
            fpath = os.path.abspath(self.exclude_file)
            if os.path.isfile(fpath):
                with open(fpath, 'r') as f:
                    exclude_list = f.readlines()
                    for file in found_list:
                        if file in exclude_list:
                            found_list.remove(file)
                    f.close()
                    return found_list
            else:
                self.log.info('Error opening excluded file.')
                exit(1)
        else:
            return found_list

    def proc_vids(self, found_list, valid, zero, results,
                  target_resolution, exclude, min, duration, log):
        self.target_resolution = target_resolution
        self.results = results
        self.log = log
        self.exclude_file = exclude
        self.min_size = min * 1024
        self.min_dur = float(duration)
        log.info('Started Video Processing.')
        proc_list = self.build_exclist(found_list)
        bar = alive_it(proc_list,
                       finalize=lambda bar: bar.text('Whoo-hoo! Processing Videos is done!'))
        for item in bar:
            processed = False
            while processed is False:
                if processed is True:
                    continue
                log.debug('Item is: {}'.format(item))
                log.debug('Proc_vids function item is type: {}'.format(type(item)))
                fsize = os.path.getsize(item)
                if zero:
                    processed = self.zero_sum(item, fsize, log)
                if valid:
                    processed = self.check_valid(item, log)
                    processed = self.check_size(item, fsize, log)
                try:
                    ffdict = ffmpeg.probe(item)
                except ffmpeg.Error:
                    log.info('Ffmpeg error: {}'.format(
                        ffmpeg.Error(cmd=True, stdout=True, stderr=True)))
                    continue
                try:
                    ffstreams = ffdict.get('streams')
                    vidstream = ffstreams[0]
                    processed = self.check_resolution(item, vidstream, log)
                    processed = self.check_duration(item, vidstream, log)
                except ffmpeg.Error:
                    log.info('Ffmpeg Error: {}'.format(ffmpeg.Error(cmd=True, stdout=True, stderr=True)))
                    continue
                processed = True
                bar.text(f'Processed: {item}')
        return True
