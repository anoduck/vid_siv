#!/usr/bin/env python3

from dataclasses import dataclass
from simple_parsing import parse, choice
from alive_progress import alive_bar, alive_it
import ffmpeg
import magic
import trio
from aioresult import ResultCapture
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


async def get_log(Options):
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


def get_alivelog():
    logging.basicConfig(level=logging.INFO)
    alog = logging.getLogger('alive_progress')
    return alog


async def proc_vids(recvproc, tres, Options, bar, task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    log.info('Started Video Processing.')
    async with recvproc:
        async for item in recvproc:
            log.debug('Item is: {}'.format(item))
            log.debug('Proc_vids function item is type: {}'.format(type(item)))
            fsize = os.path.getsize(item)
            min_size = Options.min * 1024
            if min_size > fsize and not Options.noz:
                log.info('Removing zero sum file: {}'.format(item))
                os.remove(item)
                log.info('Zero sum item {} removed.'.format(item))
                bar()
                # continue
            try:
                ffdict = ffmpeg.probe(item)
                ffstreams = ffdict.get('streams')
                vidstream = ffstreams[0]
                fwidth = vidstream.get('width')
                log.debug('Video quality(width): {}'.format(fwidth))
                strdur = vidstream.get('duration')
                fdur = float(strdur)
                log.debug("fdur type: {}".format(type(fdur)))
                log.debug('Video duration in secs: {}'.format(fdur))
                if Options.dur:
                    log.debug('Duration removal is enabled')
                    flopt = float(Options.dur)
                    if flopt > fdur:
                        log.info('File {0} is below minimum {1} duration'.format(item, fdur))
                        os.remove(item)
                        log.info('Deleting file: {}'.format(item))
                        bar()
                        # continue
                if fwidth >= 1:
                    if tres > fwidth:
                        log.info('Item {0} width {1} does not meet minimum of {2}'.format(item, fwidth, tres))
                        if Options.rm:
                            os.remove(item)
                            log.info('Deleting {}'.format(item))
                            bar()
                            # continue
            except ffmpeg.Error:
                log.debug('Ffmpeg error: {}'.format(ffmpeg.Error(cmd=True,
                                                                 stdout=True,
                                                                 stderr=True)))
                continue


async def send_vids(sendproc, i, task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    log.info('Var(i) Value: {}'.format(i))
    async with sendproc:
        await sendproc.send(i)
        log.debug('Sent item: {}'.format(i))


async def juicer(sendproc, retset, task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    log.info('Feeding list into Juicer')
    log.info('There are {} items'.format(len(retset)))
    async with sendproc:
        async with trio.open_nursery() as nurse_send:
            for i in retset:
                nurse_send.start_soon(send_vids, sendproc.clone(), i)


async def find_videos(recvchan, log, task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    eset = set()
    async with recvchan:
        async for item in recvchan:
            mmag = magic.Magic(mime=True)
            mt = mmag.from_file(item)
            tsplit = mt.split('/')
            mime = tsplit[0]
            log.debug('MT Type: {}'.format(str(type(mime))))
            log.debug('MT Value: {}'.format(mime))
            if mime == 'video':
                eset.add(item)
            log.debug('return item is: {}'.format(item))
    log.debug('Eset Value: {}'.format(eset))
    log.debug('Eset type: {}'.format(type(eset)))
    return eset


async def walk(dir_path, sendchan, task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    count = 0
    log.debug('Walk dir path: {}'.format(dir_path))
    async with sendchan:
        for obj_tup in os.walk(dir_path):
            filelists = obj_tup[2]
            for name in filelists:
                rpath = os.path.join(obj_tup[0], name)
                apath = os.path.abspath(rpath)
                log.debug('Walk file path: {}'.format(apath))
                await sendchan.send(apath)
                count += 1
                log.debug('Send count: {}'.format(count))


async def get_flist(Options, log):
    log.info('Generating file list recursively')
    log.info('Generating Current Context')
    dir_path = os.path.abspath(Options.dir)
    log.debug('Directory path: {}'.format(dir_path))
    log.debug('Starting trio Async')
    async with trio.open_nursery() as nsy:
        sendlst, recvlist = trio.open_memory_channel(0)
        async with sendlst, recvlist:
            nsy.start_soon(walk, dir_path, sendlst.clone())
            nsy.start_soon(walk, dir_path, sendlst.clone())
            res1 = ResultCapture.start_soon(nsy, find_videos, recvlist.clone(), log)
            res2 = ResultCapture.start_soon(nsy, find_videos, recvlist.clone(), log)
    retset = res1.result().union(res2.result())
    log.debug('Nursery return type: {}'.format(type(retset)))
    log.info('The file list has been generated.')
    return retset


async def get_bar(retset):
    total = len(retset)
    log.debug('Return set total: {}'.format(total))
    with alive_bar(total) as bar:
        return bar


async def siv(Options):
    global log
    log = await get_log(Options)
    qty = Options.qty
    rdict = {'480': 480, '720': 720, '2k': 1920, '4k': 3840}
    tres = rdict.get(qty)
    retset = await get_flist(Options, log)
    bar = await get_bar(retset)
    await trio.sleep(1)
    async with trio.open_nursery() as nursery:
        sendproc, recvproc = trio.open_memory_channel(4)
        async with sendproc, recvproc:
            nursery.start_soon(juicer, sendproc, retset)
            [nursery.start_soon(proc_vids, recvproc.clone(),
                                tres, Options, bar) for _ in range(4)]
    await trio.sleep(1)
    log.info('Process complete.')
    print('Done!', flush=False)


if __name__ == "__main__":
    trio.run(siv, Options)
