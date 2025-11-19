import os
import re
import cv2 as cv
from   glob import glob

from ..util.timestring import tstr_2_sec
from ..util.jsonio import json_2_dict
from .videocontainer import VideoContainer
from .cliargs import CLIArgs
from .cliargs import ALLOWED_VIDEO_EXT


def subgather_single(input_video_path: str, static_window: str | dict):

    cap = cv.VideoCapture(input_video_path)
    
    # when dict (from read json) -----------------------------------------------
    if isinstance(static_window, dict):
        tstr = static_window[os.path.basename(input_video_path)] # only care about current video timestring
        tstr = re.findall(r"\d\d:\d\d:\d\d-\d\d:\d\d:\d\d", tstr)[0]
        t0 = tstr_2_sec(tstr.split("-")[0])
        t1 = tstr_2_sec(tstr.split("-")[1])
        window_sec = [t0, t1]
    
    # when string START-hh:mm:ss -----------------------------------------------    
    elif isinstance(static_window, str) and len(re.findall(r"START-\d\d:\d\d:\d\d", static_window)) > 0:
        tstr = re.findall(r"START-\d\d:\d\d:\d\d", static_window)[0]
        t0 = 0
        t1 = tstr_2_sec(tstr.split("-")[1])
        window_sec = [t0, t1]

    # when string hh:mm:ss-END -------------------------------------------------
    elif isinstance(static_window, str) and len(re.findall(r"\d\d:\d\d:\d\d-END", static_window)) > 0:
        tstr = re.findall(r"\d\d:\d\d:\d\d-END", static_window)[0]
        t0 = tstr_2_sec(tstr.split("-")[0])
        t1 = cap.get(cv.CAP_PROP_FRAME_COUNT) / cap.get(cv.CAP_PROP_FPS)
        window_sec = [t0, t1]
    
    # when string hh:mm:ss-hh:mm:ss --------------------------------------------  
    elif isinstance(static_window, str) and len(re.findall(r"\d\d:\d\d:\d\d-\d\d:\d\d:\d\d", static_window)) > 0:
        tstr = re.findall(r"\d\d:\d\d:\d\d-\d\d:\d\d:\d\d", static_window)[0]
        t0 = tstr_2_sec(tstr.split("-")[0])
        t1 = tstr_2_sec(tstr.split("-")[1])
        window_sec = [t0, t1]
        
    else: # should not occur if sanitization holds
        raise TypeError("got neither valid string nor dict for static_window in subgather_single")

    vid = VideoContainer(
        path=input_video_path,
        fpsc=cap.get(cv.CAP_PROP_FPS),
        ftot=cap.get(cv.CAP_PROP_FRAME_COUNT),
        static_window=window_sec,
    )
    
    return [vid]

def subgather_multi(input_video_path: str, static_window: str | dict):
    
    videos = []
    videos_paths = [vd for xt in ALLOWED_VIDEO_EXT for vd in glob(os.path.join(input_video_path, f"*{xt}"))]
    for path in videos_paths:
        videos += subgather_single(path, static_window)

    return videos

def gather_videos(CLIARGS: CLIArgs):
    
    # single video -------------------------------------------------------------
    if os.path.isfile(CLIARGS.input_video_path):
        
        if os.path.isfile(CLIARGS.static_window):
            static_window = json_2_dict(CLIARGS.static_window)
        else:
            static_window = CLIARGS.static_window
        videos = subgather_single(CLIARGS.input_video_path, static_window)      
    
    # video folder -------------------------------------------------------------
    else:
        
        if os.path.isfile(CLIARGS.static_window):
            static_window = json_2_dict(CLIARGS.static_window)
        else:
            static_window = CLIARGS.static_window
        videos = subgather_multi(CLIARGS.input_video_path, static_window)

    return videos # always just return a list of VideoContainers, even if it's just one video

