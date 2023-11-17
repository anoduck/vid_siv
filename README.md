```text
# __     ___     _   ____  _
# \ \   / (_) __| | / ___|(_)_   __
#  \ \ / /| |/ _` | \___ \| \ \ / /
#   \ V / | | (_| |  ___) | |\ V /
#    \_/  |_|\__,_| |____/|_| \_/
#
```

## Vid Siv

Hewo!

This rather simple script does the following:
- It recursively traverses a directory looking for video files.
- When it finds one, it makes sure it is an actual video file.
- It then checks to see if the file has a size less than configured amount.
- If the file does not meet the minimum required file size it removes it.
- If it does, it then checks to see if the file meets the minimum duration requirement.
- Like before, if the file fails, it is removed. If it succeeds, it moves on to the next filter.
- Lastly, it probes the file for the width. The width is often used to designate quality.
- If the video width does not meet the designated minimum amount, it deletes the file.
- The script is used for removing low quality video files from your system.

__Because, the nineties were not the best time for high def video.__

## Install

Use python poetry to install with `poetry install` or use pipenv to install with `pipenv install`. Which ever
is your choice.

## Options

Your options are very basic, so don't get too excited, but I did try to provide the user with as many options
to customize as possible. 

| Option    |  flag   | What it does                    |
| :-------- | :-----: | :-------------                  |
| directory | `--dir` | Directory to search in          |
| quality   | `--qty` | Desired quality (width)         |
| duration  | `--dur` | Enable and set minimum duration |
| remove    | `--rm`  | Enable file removal             |
| no zero   | `--noz` | Disable zero sum deletion       |
| minimum   | `--min` | file size for zero sum          |
| log level | `--lev` | Set log level to DEBUG or INFO  |
| log file  | `--log` | Log file path                   |


### License
https://anoduck.mit-license.org
