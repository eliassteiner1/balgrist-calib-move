import os
import re
import json
from   glob import glob
import einops as eo

import numpy as np
import cv2 as cv
import tyro

from .core.cliargs import CLIArgs
from .core.gather import gather_videos
from .core.process_homographies import process_video_ho
from .core.plotting import plot_video_ho

from .config.plotconfig import PlotConfig
from .config.root import ROOT

from .util.output import pbar


def main_func(argv=None):

    # parse cl args and sanitize -----------------------------------------------
    # if no argv, tyro it will grab from sys.argv, but if argv is passed (run from script) then it will take main argv
    CLIARGS = tyro.cli(CLIArgs, args=argv)
    CLIARGS.sanitize()
    
    # gather data --------------------------------------------------------------
    videos = gather_videos(CLIARGS)
    for vd in videos:
        vd.sanitize()
        
    # process all videos to find homographies ----------------------------------
    for vd in videos:
        process_video_ho(CLIARGS, vd) # stores homography list in each container

    # plot homographies of all videos ------------------------------------------
    plots = []
    for vd in pbar(videos, desc="plot videos (all)"):
        plots += plot_video_ho(CLIARGS, vd, PlotConfig)
    
    # stitch all plots together and save ---------------------------------------
    plots = eo.rearrange(np.array(plots), "B h w c -> (B h) w c")
    cv.imwrite(ROOT/"tests/stitched_plots.png", plots)

 
    

    
    
    




    
    
