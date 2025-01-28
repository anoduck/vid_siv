#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Playlist:

    # Generate Playlist -----------------------------------------------------------
    async def gen_playlist(self, recvproc, tres, Options, log,
                           task_status=trio.TASK_STATUS_IGNORED):
        task_status.started()
        await trio.sleep(1)
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
                    if strdur is not None:
                        fdur = float(strdur)
                    else:
                        fdur = 0
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
                    if type(fwidth) == 'NoneType':
                        if tres > fwidth:
                            log.info('Item {0} width {1} does not meet minimum of {2}'.format(item, fwidth, tres))
                            if await trio.Path(item).exists():
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
                await trio.sleep(0.1)
        return res_ret
