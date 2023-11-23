#!/usr/bin/env python3

from dataclasses import dataclass
from simple_parsing import parse, choice
from alive_progress import alive_it, alive_bar
import ffmpeg
import magic
import trio
from aioresult import ResultCapture
import os
import logging


@dataclass
class Options:
    """Vidsiv helps you remove zero-sum, low quality, and short videos from folders recursively."""
    dir: str = os.path.expanduser('~/Videos')  # Path of the directory you want sieved.
    tks: int = 2  # NO TOUCH! Unless, you know what your doing! Controls number of channel receiving functions
    qty: str = choice("480", "540", "720", "1080", "2k", "4k", default='720')  # Minimum desired quality (width)
    dur: int = 60  # Enable and set Minimum allowed duration in secs.
    rm: bool = False  # Enable deletion of low quality files.
    zo: bool = True  # Disable removal of zerosum files.
    min: int = 512  # Minimum file size in kilobytes, less than is considered zero sum.
    lev: str = choice('info', 'debug', default='debug')  # Set log level to either INFO or DEBUG
    log: str = os.path.abspath('./vidsiv.log')  # Full path to log file.
    rot: bool = True  # Disable auto rotate log file when > 512Kb


Options = parse(Options, dest="Options")


async def rotate_file(logfile):
    log_size = os.path.getsize(logfile)
    smart_size = log_size % 1024
    if smart_size >= 512:
        os.remove(logfile)


async def get_log(Options):
    if Options.rot:
        await rotate_file(Options.log)
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


async def proc_vids(recvproc, tres, Options, task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    res_ret = []
    log.info('Started Video Processing.')
    async with recvproc:
        async for item in recvproc:
            log.debug('Item is: {}'.format(item))
            log.debug('Proc_vids function item is type: {}'.format(type(item)))
            fsize = os.path.getsize(item)
            min_size = Options.min * 1024
            if min_size > fsize and Options.zo:
                log.info('Removing zero sum file: {}'.format(item))
                if Options.rm:
                    os.remove(item)
                    log.info('Zero sum item {} removed.'.format(item))
                    await trio.sleep(0.1)
                else:
                    res_ret.append(item)
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
                        if Options.rm:
                            os.remove(item)
                            log.info('Deleting file: {}'.format(item))
                            await trio.sleep(0.1)
                        else:
                            res_ret.append(item)
                if fwidth >= 1:
                    if tres > fwidth:
                        log.info('Item {0} width {1} does not meet minimum of {2}'.format(item, fwidth, tres))
                        if Options.rm:
                            os.remove(item)
                            log.info('Deleting {}'.format(item))
                            await trio.sleep(0.1)
                        else:
                            res_ret.append(item)
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
            for i in alive_it(retset, finalize=lambda bar: bar.text('Finished Processing Videos!')):
                nurse_send.start_soon(send_vids, sendproc.clone(), i)


async def find_videos(recvchan, bar, log, task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    eset = list()
    async with recvchan:
        async for item in recvchan:
            if await trio.Path(item).is_file():
                magik = magic.Magic(mime=True)
                try:
                    mt = magik.from_file(item)
                    mt_split = mt.split('/')
                    mime = mt_split[0]
                    log.debug('MT Type: {}'.format(str(type(mime))))
                    log.debug('MT Value: {}'.format(mime))
                    if mime == 'video':
                        eset.append(item)
                        bar()
                    else:
                        bar()
                    log.debug('return item is: {}'.format(item))
                except magic.MagicException:
                    log.debug('Magic Exception: {}'.format(item))
                    bar()
                    pass
            else:
                bar()
    log.debug('Eset Value: {}'.format(eset))
    log.debug('Eset type: {}'.format(type(eset)))
    return eset


async def send_path(sendchan, tg_path, task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    async with sendchan:
        await sendchan.send(tg_path)
        await trio.sleep(0.1)


async def file_juice(dir_path, sendchan, task_status=trio.TASK_STATUS_IGNORED):
    task_status.started()
    log.debug('Juicing the path')
    async with sendchan:
        async with trio.open_nursery() as juicery:
            trio_glob = trio.Path(dir_path).rglob('**/*')
            for file in await trio_glob:
                tg_path = trio.Path(dir_path).joinpath(file)
                if await trio.Path(tg_path).is_file():
                    log.debug('{} is a file.'.format(tg_path))
                    juicery.start_soon(send_path, sendchan.clone(), tg_path)


async def get_fileset(Options, log):
    log.info('Generating file list recursively')
    eset = list()
    dir_path = os.path.abspath(Options.dir)
    for oswald in os.walk(dir_path):
        files = oswald[2]
        total = len(files)
        with alive_bar(total) as bar:
            for file in files:
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path):
                    magik = magic.Magic(mime=True)
                    try:
                        mime_type = magik.from_file(file_path)
                        type_split = mime_type.split('/')
                        mime = type_split[0]
                        log.debug('{0} is a {1} file'.format(file_path, mime))
                        if mime == 'video':
                            eset.append(file_path)
                            bar()
                        else:
                            bar()
                    except magic.MagicException:
                        log.debug('Magic Exception: {}'.format(file_path))
                        bar()
                        pass
    return eset


async def get_flist(Options, log):
    log.info('Generating file list recursively')
    log.info('Generating Current Context')
    dir_path = os.path.abspath(Options.dir)
    log.debug('Directory path: {}'.format(dir_path))
    log.debug('Starting trio Async')
    total_count = len(os.listdir(dir_path))
    start_time = trio.current_time()
    with alive_bar(total_count) as bar:
        async with trio.open_nursery() as nsy:
            sendlst, recvlist = trio.open_memory_channel(1)
            async with sendlst, recvlist:
                nsy.start_soon(file_juice, dir_path, sendlst.clone())
                res = [ResultCapture.start_soon(nsy, find_videos,
                                                recvlist.clone(),
                                                bar, log) for _ in range(Options.tks)]
    retset = [r.result() for r in res]
    end_time = trio.current_time()
    total_time = end_time - start_time
    log.info('Total runtime: {}'.format(total_time))
    log.debug('Nursery return type: {}'.format(type(retset)))
    log.info('The file list has been generated.')
    return retset


async def siv(Options):
    global log
    log = await get_log(Options)
    qty = Options.qty
    rdict = {'480': 480, '540': 540, '720': 720, '2k': 1920, '4k': 3840}
    tres = rdict.get(qty)
    retset = await get_flist(Options, log)
    # retset = await get_fileset(Options, log)
    with alive_bar(len(retset)) as bar:
        await trio.sleep(0.1)
        async with trio.open_nursery() as nursery:
            sendproc, recvproc = trio.open_memory_channel(1)
            async with sendproc, recvproc:
                nursery.start_soon(juicer, sendproc, retset)
                pres = [nursery.start_soon(proc_vids, recvproc.clone(),
                                           tres, Options) for _ in range(Options.tks)]
                if pres:
                    res = []
                    for r in pres:
                        res.extend(r)
        await trio.sleep(0.1)
        if not Options.rm:
            file_path = os.path.abspath('results.txt')
            with open(file_path, mode='w', encoding='utf-8') as writ:
                for item in res:
                    writ.write(item)
                    writ.write('\n')
                    bar()
                writ.close()
                log.info('Results written to file: {}'.format(file_path))
    log.info('Process complete.')
    print('Done!', flush=False)


if __name__ == "__main__":
    trio.run(siv, Options)
