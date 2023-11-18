#!/usr/bin/env python3

from dataclasses import dataclass
from simple_parsing import parse, choice
from alive_progress import alive_bar
import ffmpeg
import mimetypes
import trio
import os
import logging

# Variables
log_file = os.path.abspath('vidsiv.log')


@dataclass
class Options:
    """Vidsiv helps you remove zero sum, low quality, and short videos from folders recursively."""
    dir: str = os.path.expanduser('~/Videos')  # Path of the directory you want sieved.
    qty: str = choice("480", "720", "1080", "2k", "4k", default='720')  # Minimum desired quality (width)
    dur: int = 60  # Enable and set Minimum allowed duration in secs.
    rm: bool = False  # Enable deletion of low quality files.
    noz: bool = False  # Disable removal of zerosum files.
    min: int = 512  # Minimum file size in kilobytes, less than is considered zero sum.
    lev: str = choice('info', 'debug', default='debug')  # Set log level to either INFO or DEBUG
    log: str = os.path.abspath('./vidsiv.log')  # Full path to log file.


Options = parse(Options, dest="Options")


def get_log(Options):
    log = logging.getLogger(__name__)
    if log.hasHandlers():
        log.handlers.clear()
    if Options.lev == 'info':
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.DEBUG)
    handler = logging.FileHandler(Options.log, mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.info('Starting VidSiv')
    log.info('Started logging...')
    return log


async def find_videos(recv, sendproc):
    async with recv:
        async for item in recv:
            mt = mimetypes.guess_type(item)
            mime_str = str(mt[0])
            tsplit = mime_str('/')
            if tsplit[0] == 'video':
                sendproc.send(item)
            continue


async def proc_vids(recvproc, log, tres, Options, bar):
    async with recvproc:
        async for item in recvproc:
            log.debug('Item is: {}'.format(item))
            fsize = os.path.getsize(item)
            min_size = Options.min * 1024
            if min_size > fsize and not Options.noz:
                log.info('Removing zero sum file: {}'.format(item))
                os.remove(item)
                log.info('Zero sum item {} removed.'.format(item))
                bar()
                continue
            ffdict = ffmpeg.probe(item)
            ffstreams = ffdict.get('streams')
            vidstream = ffstreams[0]
            fwidth = vidstream.get('width')
            log.debug('Video quality(width): {}'.format(fwidth))
            fdur = vidstream.get('duration')
            log.debug('Video duration in secs: {}'.format(fdur))
            if Options.dur:
                log.debug('Duration removal is enabled')
                if Options.dur > fdur:
                    log.info('File {0} is below minimum {1} duration'.format(item, fdur))
                    os.remove(item)
                    log.info('Deleting file: {}'.format(item))
                    bar()
                    continue
            if fwidth is not None:
                if tres > fwidth:
                    log.info('Item {0} width {1} does not meet minimum of {2}'.format(item, fwidth, tres))
                    if Options.rm:
                        os.remove(item)
                        log.info('Deleting {}'.format(item))
                        bar()
                        continue
            continue


async def get_flist(Options, sendproc, log):
    sendflist, recflist = trio.open_memory_channel(0)
    log.info('Generating file list recursively')
    dir_path = os.path.abspath(Options.dir)
    log.debug('Directory path: {}'.format(dir_path))
    entries = await trio.Path(dir_path).rglob('**/*')
    for entry in entries:
        if await trio.Path(entry).is_file():
            await sendflist.send(entry)
    log.info('Raw file list generated')
    log.info('Checking for mimetypes')
    sendproc1 = sendproc
    sendproc2 = sendproc.clone()
    sendproc3 = sendproc.clone()
    recv1 = recflist
    recv2 = recflist.clone()
    recv3 = recflist.clone()
    log.debug('Starting trio Async')
    async with trio.open_nursery() as nsy:
        nsy.start_soon(find_videos(recv=recv1, sendproc=sendproc1))
        nsy.start_soon(find_videos(recv=recv2, sendproc=sendproc2))
        nsy.start_soon(find_videos(recv=recv3, sendproc=sendproc3))
    log.info('File list filtered by mimetype.')
    log.info('The file list has been generated.')


async def main(Options):
    log = get_log(Options)
    qty = Options.qty
    sendproc, recvproc = trio.open_memory_channel(0)
    rdict = {'480': 480, '720': 720, '2k': 1920, '4k': 3840}
    tres = rdict.get(qty)
    await get_flist(Options, sendproc, log)
    total = recvproc.qsize()
    with alive_bar(total) as bar:
        async with trio.open_nursery as nsy0:
            nsy0.start_soon(proc_vids(recvproc=recvproc, log=log,
                                      tres=tres, Options=Options, bar=bar))
            nsy0.start_soon(proc_vids(recvproc=recvproc.clone(), log=log,
                                      tres=tres, Options=Options, bar=bar))
            nsy0.start_soon(proc_vids(recvproc=recvproc.clone(), log=log,
                                      tres=tres, Options=Options, bar=bar))
            nsy0.start_soon(proc_vids(recvproc=recvproc.clone(), log=log,
                                      tres=tres, Options=Options, bar=bar))
    await trio.sleep(0)
    log.info('{} files processed'.format(total))
    log.info('Process complete.')
    print('Done!')


trio.run(main, Options)
