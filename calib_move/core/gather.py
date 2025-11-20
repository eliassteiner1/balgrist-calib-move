import os
import re
import cv2 as cv
from   glob import glob
from   pathlib import Path

from ..util.timestring import tstr_2_sec
from ..util.jsonio import json_2_dict
from .videocontainer import VideoContainer
from .cliargs import CLIArgs
from .cliargs import ALLOWED_VIDEO_EXT


# TODO: use pathlib Path EVERYWHERE
def subgather_single(CLIARGS: CLIArgs, vid_path: Path, window: str | dict) -> list[VideoContainer]:

    cap = cv.VideoCapture(vid_path)
    
    if isinstance(window, dict):
        window = window[vid_path.name] # only care about current video timestring

    # from now on, window is alway just a string
    
    # when string START-hh:mm:ss -----------------------------------------------    
    if len(re.findall(r"START-\d\d:\d\d:\d\d", window)) > 0:
        tstr = re.findall(r"START-\d\d:\d\d:\d\d", window)[0]
        t0 = 0
        t1 = tstr_2_sec(tstr.split("-")[1])
        window_sec = [t0, t1]

    # when string hh:mm:ss-END -------------------------------------------------
    elif len(re.findall(r"\d\d:\d\d:\d\d-END", window)) > 0:
        tstr = re.findall(r"\d\d:\d\d:\d\d-END", window)[0]
        t0 = tstr_2_sec(tstr.split("-")[0])
        t1 = cap.get(cv.CAP_PROP_FRAME_COUNT) / cap.get(cv.CAP_PROP_FPS)
        window_sec = [t0, t1]
    
    # when string hh:mm:ss-hh:mm:ss --------------------------------------------  
    elif len(re.findall(r"\d\d:\d\d:\d\d-\d\d:\d\d:\d\d", window)) > 0:
        tstr = re.findall(r"\d\d:\d\d:\d\d-\d\d:\d\d:\d\d", window)[0]
        t0 = tstr_2_sec(tstr.split("-")[0])
        t1 = tstr_2_sec(tstr.split("-")[1])
        window_sec = [t0, t1]
        
    else: # should not occur if sanitization holds
        raise TypeError("got no valid window pattern in string (in subgather_single)")

    vid = VideoContainer(
        path=vid_path,
        fpsc=cap.get(cv.CAP_PROP_FPS),
        ftot=cap.get(cv.CAP_PROP_FRAME_COUNT),
        static_window=window_sec,
    )
    vid.sanitize(CLIARGS) #TODO: fuck, can remove it here, donig already in main hahah
    cap.release()
    
    return [vid]

def subgather_multi(CLIARGS: CLIArgs, window: str | dict) -> list[VideoContainer]:
    
    videos = []
    videos_paths = [Path(vd) for xt in ALLOWED_VIDEO_EXT for vd in CLIARGS.input_video_path.glob(f"*{xt}")]
    for vid_path in videos_paths:
        videos += subgather_single(CLIARGS, vid_path, window)

    return videos

def gather_videos(CLIARGS: CLIArgs) -> list[VideoContainer]:
    
    # single video -----------------------------------------------------------------------------------------------------
    if CLIARGS.input_video_path.is_file():
        # window json ----------------------------------------------------------
        if Path(CLIARGS.static_window).is_file():
            window = json_2_dict(CLIARGS.static_window)
        # window string --------------------------------------------------------
        else:
            window = CLIARGS.static_window
        videos = subgather_single(CLIARGS, CLIARGS.input_video_path, window)      
    
    # video folder -----------------------------------------------------------------------------------------------------
    else:
        # window json ----------------------------------------------------------
        if Path(CLIARGS.static_window).is_file():
            window = json_2_dict(CLIARGS.static_window)
        # window string --------------------------------------------------------
        else:
            window = CLIARGS.static_window
        videos = subgather_multi(CLIARGS, window)

    return videos # always just return a list of VideoContainers, even if it's just one video

