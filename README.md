```text
                 ;                                                   
                 ED.                                                 
                 E#Wi                               .                
             t   E###G.                            ;W t              
             Ej  E#fD#W;                          f#E Ej             
 t      .DD. E#, E#t t##L                       .E#f  E#, t      .DD.
 EK:   ,WK.  E#t E#t  .E#K,                    iWW;   E#t EK:   ,WK. 
 E#t  i#D    E#t E#t    j##f                  L##Lffi E#t E#t  i#D   
 E#t j#f     E#t E#t    :E#K:                tLLG##L  E#t E#t j#f    
 E#tL#i      E#t E#t   t##L                    ,W#i   E#t E#tL#i     
 E#WW,       E#t E#t .D#W;                    j#E.    E#t E#WW,      
 E#K:        E#t E#tiW#G.                   .D#j      E#t E#K:       
 ED.         E#t E#K##i       ,;;;;;;;;;.  ,WK,       E#t ED.        
 t           E#t E##D.        jLLLLLLLLLL, EG.        E#t t          
             ,;. E#t                       ,          ,;.            
                 L:                                              
```

## Vid Siv

__Hewo!__

Vid_Siv is a video sieve for low quality (>480) videos.

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
is your choice. Which would look like so:

```commandline
poetry install
```
or
```commandline
pipenv install
```

## Options

Your options are very basic, so don't get too excited, but I did try to provide the user with as many options
to customize as possible. 

| Option     |   flag   | What it does                     |
|:-----------|:--------:|:---------------------------------|
| directory  | `--dir`  | Directory to search in           |
| quality    | `--qty`  | Desired quality (width)          |
| duration   | `--dur`  | Enable and set minimum duration  |
| remove     |  `--rm`  | Enable file removal              |
| no zero    | `--noz`  | Disable zero sum deletion        |
| minimum    | `--min`  | file size for zero sum           |
| log level  | `--lev`  | Set log level to DEBUG or INFO   |
| log file   | `--log`  | Log file path                    |

### Usage

Using Vid_Siv would look something like so:

```commandline
poetry run python vidsiv.py --dir /dir/path --rm
```
* All options possess a default value.
* If no directory is specified on the command line, the script will default to using `/home/$USER/Videos`.
* If the `--rm` flag is not used, the script will do nothing. This is so to prevent accidental deletion of files.
* As a "bonus" feature, you can use the `--dur` flag and remove files based on minimum size as well.
* If you have files less than 512kb that you want to keep, you can either disable zero sum with `--noz` or change
it with `--min 256`.

### Thanks

A special thanks goes out to [Arthur Tacca](https://github.com/arthur-tacca) for realizing and providing the
missing feature to the trio asynchronous library, i.e. [aioresult](https://github.com/arthur-tacca/aioresult).  

### License
https://anoduck.mit-license.org
