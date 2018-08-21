# Legender

A python application for quick auto-downloading the best subtitles for one or many video files

## Compilation

This script uses py2app and py2exe in order to create 
simple executables for easy distribution

on Windows or Mac
```bash
git clone https://github.com/Megarushing/legender.git
cd legender
python compile
```

py2exe needs python 3.4 or 2.7 in order to compile for now while its not yet updated for newer versions

## Basic Usage

Legender accepts one or more parameters containing video file
paths and/or directory paths, for each directory given it will scan
it for video files and download subtitles for each one of them

For instance: On Windows

```cmd
legender.exe test.avi
```
Or
```cmd
legender.exe testfolder
```
Or
```cmd
legender.exe file.avi file2.avi folder1 folder2 file3.mkv
```

On Mac, an app is built, which can be used by:
```cmd
open legender.app test.avi
```
Or
```cmd
legender.app/Contents/MacOS/legender test.avi
```

On Linux or any platform with Python 2/3
```cmd
python legender.py test.avi
```

## Configurations

On first run Legender generates a config.ini file, which can be
modified for custom options, bellow is the description of what these options do:

### version

The downloader version that is passed to the API, some versions are not accepted
340 is tested and ok for now, in case this changes in the future the script automatically
tries to increment it 1 by 1 until finding a new accepted version

### recursive

When specifying a folder for legender to find subtitles it looks for video files inside that specific folder,
when enabled, recursive tells legender to navigate inside each subfolder in search for subtitles, and on.

It wont go inside symlinks

### replace_existing

If the video already has a subtitle file for it, it wont download a new one unless this option is 1

### languages

This contains a list of languages to download, if no subtitles are found for the specified language it
tries to find for another one

6 = Brazilian Portuguese

36 = Portugal Portuguese

14 = English

### video_extensions

Which extensions are to be considered video files when looking for them

### max_retries

How many times should the subtitle download retry in case of download errors
