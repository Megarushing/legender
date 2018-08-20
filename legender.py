from __future__ import print_function
import sys, os
import config
import base64
from xml.dom.minidom import parseString
import zipfile
import time
import struct
import requests
from io import BytesIO

def get_subs_list(hash,language=6):
    #prepare data to get subtitles list
    data = {
        "version":str(config.version),
        "response":"xml",
        "cod_language":language,
        "hash":hash
    }
    headers = {
        "Content-type":"application/x-www-form-urlencoded"
    }

    url = 'http://{}{}'.format(config.server, config.list_endpoint)
    req = requests.post(url,data=data,headers=headers)
    dom = parseString(req.text)

    subtitles = dom.getElementsByTagName('subtitles')[0].childNodes
    if len(subtitles) == 0:
        return False
    else:
        if (dom.getElementsByTagName('id')[0].toxml() == '<id>MA==</id>'):
            config.set("version",config.version + 1)
            raise ConnectionRefusedError("version error, increased to {}, retry".format(config.version))
        else:#return subtitle list
            return dom.getElementsByTagName('subtitle')

def get_subtitle(hash,subtitle,language=6):
    #prepare the headers to get the 1st subtitle
    data = {
        "response" : "multiple",
        "imdb" : "false",
        "poster":"false",
        "version":str(config.version),
        "cod_language":language,
        "hash":hash,
        "subtitles":"<?xml version='1.0'?><subtitles>{}</subtitles>".format(subtitle.toxml())
    }
    headers = {
        "Content-type":"application/x-www-form-urlencoded"
    }

    url="http://{}{}".format(config.server,config.download_endpoint)

    req = requests.post(url, data=data, headers=headers)

    #result comes as a zipfile so we extract it
    result = BytesIO()
    result.write(req.content)
    zfile = zipfile.ZipFile(result)
    subtext = zfile.read(zfile.namelist()[0])
    result.close()
    # return unzipped subtitle
    return subtext

def hashFile(name):
    longlongformat = '<Q' # little-endian long long
    bytesize = struct.calcsize(longlongformat)

    f = open(name, "rb")

    filesize = os.path.getsize(name)
    hash = filesize

    if filesize < 65536 * 2:
        raise Exception("SizeError")

    for x in range(int(65536 / bytesize)):
        buffer = f.read(bytesize)
        (l_value,) = struct.unpack(longlongformat, buffer)
        hash += l_value
        hash = hash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

    f.seek(max(0, filesize - 65536), 0)
    for x in range(int(65536 / bytesize)):
        buffer = f.read(bytesize)
        (l_value,) = struct.unpack(longlongformat, buffer)
        hash += l_value
        hash = hash & 0xFFFFFFFFFFFFFFFF

    f.close()
    asciihash = b"%016x" % hash
    return base64.b64encode(asciihash).decode("utf-8")

def download_best_sub(path):
    """downloads the best subtitle for the configured languages,
    if not found, it tries another language in the order configured"""
    hash = hashFile(path)
    subs = False
    #try all languages in order
    for l in config.languages:
        for i in range(config.max_retries):
            try:
                #print("getting:",path)
                subs = get_subs_list(hash,language=l)
                break
            except ConnectionRefusedError as e:
                if i >= config.max_retries - 1:
                    print("Unable to request subtitles! script version is not being accepted",
                          "try again or modify to right version in config.ini")
                    raise e
                else:
                    time.sleep(1)
        if subs: #if there is any subtitle in the list
            print("Downloading subtitle for:", path)
            subtitle = get_subtitle(hash, subs[0], language=l)
            subfile = open(sub_path(path), 'wb')
            subfile.write(subtitle)
            subfile.close()
            return True #subtitle downloaded successfully, break
    print("Subtitle not found for:", path)
    return False

def sub_path(path):
    return path.replace('*', ' ').rsplit('.', 1)[0] + '.srt'

def download_subs_in_dir(path,recursive = 0):
    dirlist = [os.path.join(os.path.abspath(path),d) for d in os.listdir(path)]
    files = [f for f in dirlist if os.path.isfile(f)]

    for f in files:
        extension = f.rsplit('.', 1)[-1]
        if extension in allowed_extensions:
            if not os.path.exists(sub_path(f)) or config.replace_existing:
                download_best_sub(f)
    if recursive:
        dirs = [d for d in dirlist if os.path.isdir(d)
                and not os.path.islink(d)] #dont follow symlinks
        for d in dirs:
            download_subs_in_dir(d,recursive)

if __name__ == "__main__":
    global allowed_extensions
    config.load()
    allowed_extensions = config.video_extensions.split(',')

    files = [os.path.abspath(i) for i in sys.argv[1:]
             if os.path.isfile(os.path.abspath(i))]
    dirs = [os.path.abspath(i) for i in sys.argv[1:]
            if os.path.isdir(os.path.abspath(i))]

    for f in files:
        extension = f.rsplit('.', 1)[-1]
        if extension in allowed_extensions:
            if not os.path.exists(sub_path(f)) or config.replace_existing:
                download_best_sub(f)

    for d in dirs:
        download_subs_in_dir(d,config.recursive)
