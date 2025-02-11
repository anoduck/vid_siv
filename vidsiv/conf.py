#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2024  Anoduck, The Anonymous Duck
# https://anoduck.mit-license.org
# --------------------------------------------------------------------------------
from dataclasses import dataclass
from pathlib import Path
from typing import *
from simple_parsing import ArgumentParser, subparsers
from simple_parsing.helpers import choice
from vidsiv import VidSiv, FinalizeFiles


@dataclass
class Siv:
    """Siving folder recursively for files that do not meet specifications."""
    dir: Path = Path('~/Videos')  # Path of the directory you want sived.
    quality: str = choice("480", "540", "720", "1080", "2k", "4k", default='720')  # Choose minimum desired quality in width
    duration: int = 360  # Minimum duration in secs, less than this will be flagged.
    zero: bool = True  # Enable/Disable removal of zero-sum files.
    valid: bool = False  # Check videos for Validity. (Exponentially slows processing time by > 8Xs)
    min: int = 512  # Minimum file size in kilobytes, less than this amount will be flagged.
    exclude: Path = Path('')  # Path to file containing list of files to exclude from sieving. One file per line.
    results: Path = Path('./files_to_delete.txt')  # output file containing list of files that match rules for deletion.


@dataclass
class Finalize:
    """Finalizing the siv process with deletion of files from result list."""
    filelist: Path = Path('./files_to_delete.txt')  # File generated with siv action listing files to delete.

    def execute(self):
        .vidsiv.VidSiv.siv()


@dataclass
class Options:
    """Options for VidSiv

    The work flow is mainly in two parts and is as follows:
    1. Run the script with the action set to 'siv' to find files that match the criteria. This will generate a
    file containing the list of files that match the criteria.
    2. Run the script with the action set to 'finalize' to delete the files that match the criteria.

    A bonus feature, not yet fully implemented is to generate playlists for VLC media player, because there
    isn't yet a way to do this from the command line.

    Many of these options should be fairly obvious and self explanatory.
    - Actions control what the script does.
    - dir = directory, and is where you want videos sived from.
    - Quality is the minimum quality you want to keep, and should be one of 480, 540, 720, 2k, or 4k. Anything
        greater than 4k will be considered 4k, and kept.
    - duration = duration, and is the minimum duration in seconds you want to keep.
    - zero = flag files that are zero in size or too small to be a valid video file.
    - valid = check files for validity and flag those files that are not valid. This considerably increases
        processing time.
    - min = minimum acceptable file size, everything smaller than this will be removed.
    - exclude = file containing list of files to exclude from siving. One file per line.
    - results = is the file where a list of flagged files will be written to. It will be later used to remove
        the files.
    - loglevel = log level, set to either 'info' or 'debug'.
    - logfile = full path to log file.

    For redundancy, here is an explanation of the options...again...for the second time...
    """
    # Actions are "siv" and "finalize". Use "(siv or finalize) --help" for more information.
    action: Union[Siv, Finalize] = subparsers(
        {"siv": Siv, "finalize": Finalize}
    )
    loglevel: str = choice('info', 'debug', default='debug')  # Set log level to either INFO or DEBUG
    logfile: Path = Path('./vidsiv.log')  # Full path to log file.

    def execute(self):
        return self.action.execute()


parser = ArgumentParser()
parser.add_arguments(Options, dest="options")
args = parser.parse_args()
options: Options = args.options

