from dataclasses import dataclass
import numpy as np
import tyro
import cv2 as cv

@dataclass
class CLIArgs:
    """
    controls the cli of tyro and directly stores the input arguments (sys.argv)
    
    Attributes:
        input_video_path: path to the video that should be analyzed
        static_sequence: either START / END / 00:00:10 - 00:00:20

    """
    input_video_path: str
    static_sequence: str


def calc_median_image():
    pass

def calc_mode_image():
    pass

def calc_kde_image():
    pass

def generate_pivot_frame():
    # should grab frames at some interval from the static part of the video (either start end or some window)
    # maybe some params like, how many frames, which type of combination method
    # combines them all into a pivot frame (using specified method)

    pass






def main_func(argv=None):
    # parse input
    cli_args = tyro.cli(CLIArgs, args=argv)
    
    # get some video information
    cap = cv.VideoCapture(cli_args.input_video_path)
    fpsc = cap.get(cv.CAP_PROP_FPS)
    ftot = cap.get(cv.CAP_PROP_FRAME_COUNT)

    print(f"{fpsc=}, {ftot=}")
    print(f"therefore total length = {ftot / fpsc:.2f}s")
    
    # organize init frame (extract + blend)
    
    # setup detector and maybe matcher
    
    # do detection on initial frame
    
    # step through main video, for each interval frame
    
        # grab frame and do keypoint detection
        
        # do keypoint matching
        
        # estimate homography w.r.t. init frame
        
        # store homography 
        
        # step next
        
    # extract homography stats
    
    # plot
    
    # save results
    
    
    
    # ??? repeat for a whole list of videos?




    
    
