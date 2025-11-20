import numpy as np
from   numpy.typing import NDArray
import cv2 as cv

from .cliargs import CLIArgs
from .videocontainer import VideoContainer

from ..util.output import pbar


def generate_static_frame(CLIARGS: CLIArgs, video: VideoContainer, fidx: list[int]):
    
    cap = cv.VideoCapture(video.path)
    frame_coll = []
    for fi in pbar(fidx, desc=f"static frame {video.name}"):
        cap.set(cv.CAP_PROP_POS_FRAMES, fi)
        ret, frame = cap.read()
        if ret is False:
            ValueError("could not read frame") #TODO add some info here
        else:
            frame_coll.append(cv.cvtColor(frame, cv.COLOR_BGR2GRAY))
    cap.release()
    static_frame = CLIARGS.init_frame_blending.v(frame_coll)
    
    return static_frame

def calculate_homographies(CLIARGS: CLIArgs, video: VideoContainer, static_frame: NDArray[np.uint8], fidx: list[int]):
    
    detector = CLIARGS.detector.v()
    matcher = CLIARGS.matcher.v()
    
    kps_0, dsc_0 = detector.detectAndCompute(static_frame, None) # keypoints of static reference frame
    
    ho_arrays = []
    ho_errors = []
    
    cap = cv.VideoCapture(video.path)
    for fi in pbar(fidx, desc=f"homographies {video.name}"):
        cap.set(cv.CAP_PROP_POS_FRAMES, fi)
        ret, frame = cap.read()
        if ret is False:
            ValueError("could not read frame") #TODO add some info here
        else: 
            frame_gry = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            
            # keypoint detection on current frame
            kps_f, dsc_f = detector.detectAndCompute(frame_gry, None)
            
            # match with keypoints from static frame
            matches = matcher.match(dsc_0, dsc_f)
            matches = sorted(matches, key=lambda x: x.distance) # sort by descriptor distance (better match first)
            
            # extract only the (x, y) points from the keypoints
            p_0 = np.float32([kps_0[ma.queryIdx].pt for ma in matches]).reshape(-1, 1, 2) # queryIdx -> dumb cv2 syntax
            p_f = np.float32([kps_f[ma.trainIdx].pt for ma in matches]).reshape(-1, 1, 2) # trainIdx -> dumb cv2 syntax
            
            # estimate homography
            HO, mask = cv.findHomography(p_0, p_f, cv.RANSAC, 5) # TODO: maybe route these params to cli config...

            # store 
            # TODO: check if "valid homography"
            # TODO: error handling
            # TODO: maybe also exclude too few matches ... route this out as a cli config param
            ho_arrays.append(HO)
            ho_errors.append(0)
    cap.release()
    
    return ho_arrays, ho_errors

def process_video_ho(CLIARGS: CLIArgs, video: VideoContainer) -> None:
    
    fidx_init = (np.linspace(*video.static_window, CLIARGS.n_init_steps) * video.fpsc).astype(np.int64)
    fidx_main = np.linspace(0, video.ftot, CLIARGS.n_main_steps).astype(np.int64)

    static_frame = generate_static_frame(CLIARGS, video, fidx_init)

    ho_arrays, ho_errors = calculate_homographies(CLIARGS, video, static_frame, fidx_main)
    video.ho_arrays = ho_arrays
    video.ho_errors = ho_errors