""" Author: Megarushing
    This is a quick and dirty script to automate configuration persistence,
    and accessbility thoughout the system using python default config parser,
    the only thing you need to edit is config.default_values variable for the default
    settings desired, you may do this by editing this script or modifying
    the variable before running load().
    You can also provide a filename though config.config_filename variable for the config ini file if you desire so, instead of
    the standard config.ini, multiple file names are also possible"""
import os
import sys
import json
if sys.version_info >= (3, 0): #Python 3 configparser
    from configparser import ConfigParser
    from configparser import Error as ParserError
else:
    from ConfigParser import ConfigParser
    from ConfigParser import Error as ParserError

# My quick and dirty global config script for configuration persistance and readability
# Here you should set all possible configs, and their default values
# the exact config type will be inferred based on its default values type
# every dict key will become a global variable under this lib for ease of access

# if config name starts with a _(underscore) it will be protected and only
# modifiable through editing the ini file
default_values = {
    "version":340,
    "recursive":0, #recursivelly find subtitles in a dir
    "replace_existing":0, #should replace subtitle if it already exists
    "languages":[6,36,14], #6-ptbr, 36-ptpt, 14-eng. Request subtitles in this order
    "server":"www.getsubtitle.com",
    "list_endpoint":"/webService/downloadManager/get_subtitles_by_hash.php",
    "download_endpoint":"/webService/downloadManager/get_subtitle_files.php",
    "video_extensions":"3g2,3gp,3gp2,3gpp,60d,ajp,asf,asx,avchd,avi,bik,bix,box,\
cam,dat,divx,dmf,dv,dvr-ms,evo,flc,fli,flic,flv,flx,gvi,gvp,h264,m1v,\
m2p,m2ts,m2v,m4e,m4v,mjp,mjpeg,mjpg,mkv,moov,mov,movhd,movie,movx,mp4,\
mpe,mpeg,mpg,mpv,mpv2,mxf,nsv,nut,ogg,ogm,omf,ps,qt,ram,rm,rmvb,swf,ts,\
vfw,vid,video,viv,vivo,vob,vro,wm,wmv,wmx,wrap,wvx,wx,x264,xvid",
    "max_retries":30,
}

# globals
# set this to the desired config file, this can be either a string or a list
# of multiple strings, when multiple config files are detected, settings are
# loaded from all files in order, but saved only in the last
config_filename = "config.ini"
script_dir = os.path.dirname(os.path.realpath(__file__))

# set this function if you need to load additional custom sections
def load_sections():
    """ here you should treat the load of additional sections"""
    pass

def load(filename = config_filename):
    """ loads the configuration file as variables on scripts scope
        filename accepts both a list of config files to load or a single string"""
    global parser,save_parser,script_dir,config_filename

    config_filename = filename #updates config filename
    if type(config_filename) == str:
        config_filename = [config_filename]
    # for saving we use only last file
    save_parser = ConfigParser()
    save_parser.read(os.path.join(script_dir, config_filename[-1]))
    #for loading we use all files
    parser = ConfigParser()
    for filename in config_filename:
        #loads all ini files
        parser.read(os.path.join(script_dir,filename))

    #generates all global variables representing config
    #DEFAULT section
    for key,val in default_values.items():
        usekey = key
        if key.startswith("_"):
            usekey = key.lstrip("_")
            #if there is a config with same name remove it, only protected one stays
            if usekey in parser.items("DEFAULT"):
                parser.remove_option(section="DEFAULT",option=usekey)
            if usekey in save_parser.items("DEFAULT"):
                save_parser.remove_option(section="DEFAULT",option=usekey)
        #cast read string variable to type from default_values
        setting = get(key,section="DEFAULT",default=val)
        if type(val) in [list,dict]: #load as json instead
            globals()[usekey] = json.loads(setting.replace("'",'"'))
        else:
            globals()[usekey] = type(val)(setting)
    save()
    load_sections()

def get(key,section="DEFAULT",default=None):
    """gets config value from global config"""
    global parser,save_parser
    value = default
    try:
        value = parser.get(section,key)
    except ParserError as e:
        #print("Error getting config",key,"from section",
        #      section,":",e,"\nSetting default value:",default)
        save_parser.set(section, key, str(value))
        value = default
    return str(value)

def set(key,value,section="DEFAULT"):
    global save_parser

    if key in dict(parser.items(section)) and not key.startswith("_"):
        save_parser.set(section,key,value)
        save()
        load(config_filename)
        return True
    else:
        return False

def save():
    """saves current configs"""
    global save_parser,script_dir,config_filename
    # Writing to last configuration file
    with open(os.path.join(script_dir, config_filename[-1]), 'w') as configfile:
        save_parser.write(configfile)

def tostring(session="DEFAULT"):
    """
    :return: Returns string representation of section configs
    """
    global parser
    items = dict(parser.items(session))

    out = ""
    for k, v in items.items():
        if not k.startswith("_"):
            out += "{} : {}\n".format(k,v)
    return out

