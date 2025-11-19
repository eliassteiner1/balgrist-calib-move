import os
import re
import json
from   glob import glob

import numpy as np
from   numpy.typing import NDArray
import cv2 as cv
import tyro
from   tqdm import tqdm as tqdm_bar
import plotly.graph_objects as go
from   plotly.subplots import make_subplots

from   .core.cliargs import CLIArgs
from   .core.videocontainer import VideoContainer
from   .core.plotting import plot_results
from   .core.cliargs import ALLOWED_VIDEO_EXT
from   .core.gather import gather_videos

from   .util.timestring import tstr_2_sec
from   .util.timestring import sec_2_tstr
from   .util.imgblending import calc_median_image
from   .util.imgblending import calc_mode_image
from   .util.imgblending import calc_kde_image


def process_one_video_DEPR(vid_path: str):
    
    detector = cv.AKAZE_create()
    matcher = cv.BFMatcher(cv.NORM_L2, crossCheck=True)
        
    # get some video information
    cap = cv.VideoCapture(vid_path)
    fpsc = cap.get(cv.CAP_PROP_FPS)
    ftot = cap.get(cv.CAP_PROP_FRAME_COUNT)
    
    # gather and calculate init frame (extract + blend)
    n_init_frames = 10
    l_init_seq = 0.05 # percent of video
    init_frame_idx = np.linspace(0, l_init_seq*ftot, n_init_frames, dtype=np.int64)
    init_frame_list = []

    for fidx in tqdm_bar(init_frame_idx, desc="constructing pivot frame", unit_scale=True):
        cap.set(cv.CAP_PROP_POS_FRAMES, fidx)
        ret, img = cap.read()
        if ret is False:
            raise ValueError("could not read frame") #TODO add some info here
        else:
            init_frame_list.append(cv.cvtColor(img, cv.COLOR_BGR2GRAY))    
    pivot_frame = calc_median_image(init_frame_list)
    
    # do detection on initial frame
    pivot_kps, pivot_dsc = detector.detectAndCompute(pivot_frame, None)
        
    # store homographies
    homographies = []

    # step through main video, for each interval frame
    n_main_steps = 10
    frame_idx = np.linspace(0, ftot-1, n_main_steps, dtype=np.int64)
    
    for fidx in tqdm_bar(frame_idx, desc="stepping through video  ", unit_scale=True):
    
        # grab frame and do keypoint detection
        cap.set(cv.CAP_PROP_POS_FRAMES, fidx)
        ret, img = cap.read()
        if ret is False:
            raise ValueError("could not read frame") #TODO add some info here
        else:
            img_gry = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            kps_new, dsc_new = detector.detectAndCompute(img_gry, None)
            
            # do keypoint matching
            matches = matcher.match(pivot_dsc, dsc_new)
            matches = sorted(matches, key=lambda x: x.distance)
            
            # get actual coords of keypoints
            pivot_p = np.float32([pivot_kps[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            p_new = np.float32([kps_new[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

            # estimate homography w.r.t. init frame and store
            H, mask = cv.findHomography(pivot_p, p_new, cv.RANSAC, 5)
            homographies.append(H)
            
    # extract homography stats
    hs = np.array(homographies)
    
    plot_img = plot_results(
        hs, 
        ftot, fpsc, 
        vidname=os.path.basename(vid_path),
        static_window=[sec_2_tstr(0), sec_2_tstr(l_init_seq*(ftot/fpsc))]
    )
    
    return plot_img


def process_video():
    
    ...

def main_func(argv=None):

    # parse cl args and sanitize -----------------------------------------------
    # if no argv, tyro it will grab from sys.argv, but if argv is passed (run from script) then it will take main argv
    CLIARGS = tyro.cli(CLIArgs, args=argv)
    CLIARGS.sanitize()
    
    # gather data --------------------------------------------------------------
    videos = gather_videos(CLIARGS)
    for vd in videos:
        vd.sanitize()
        
    # process all videos -------------------------------------------------------
    plots = []
    for vd in videos:
        plots += process_video(CLIARGS, vd)
          
        
    # for all vids, process video -> returns plots
    # append plots
    # plot_img = process_one_video(CLIARGS.input_video_path)
    
    # stitch all plots together and save ---------------------------------------
    ...
 
    

    
    
    




    
    
