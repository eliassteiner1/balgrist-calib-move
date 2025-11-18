import os
import re
from   dataclasses import dataclass
from   enum import Enum
import cv2 as cv
from   glob import glob

from   ..util.imgblending import calc_median_image
from   ..util.imgblending import calc_mode_image
from   ..util.imgblending import calc_kde_image


from typing import Annotated
import tyro


class KeypointDetector(Enum):
    AKAZE = cv.AKAZE_create()
    SIFT  = cv.SIFT_create()
    ORB   = cv.ORB_create()
    
    @property
    def v(self):
        return self.value

class KeypointMatcher(Enum):
    BF_NORM_L2 = cv.BFMatcher(cv.NORM_L2, crossCheck=True) # good for SIFT, SURF
    BF_NORM_HAMM = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True) #good for binary desc ORB, AKAZE, BRISK

    @property
    def v(self):
        return self.value
    
class InitFrameBlending(Enum):
    MEDIAN = "MEDIAN"
    MODE   = "MODE"
    KDE    = "KDE"
    
    @property
    def v(self):
        # cannot use self.value here -> recursion
        match self.value:
            case "MEDIAN":
                return calc_median_image
            case "MODE":
                return calc_mode_image
            case "KDE":
                return calc_kde_image

ALLOWED_VIDEO_EXT = [".mp4"] # TODO: check what even works with cv2

@dataclass
class CLIArgs:
    """
    controls the cli of tyro and directly stores the input arguments (sys.argv)
    
    Attributes:
        input_video_path: path to the video that should be analyzed
        static_sequence: either START / END / maybe also somethinsg like(00:00:10 - 00:00:20)

    """
    input_video_path: Annotated[str, tyro.conf.arg(metavar="{<single-video-path>,<video-folder-path}")]
    
    static_window: Annotated[str, tyro.conf.arg(metavar="{START-hh:mm:ss,END-hh:mm:ss,hh:mm:ss-hh:mm:ss,<json-path>}",)]
    n_init_steps: int = 5
    init_frame_blending: InitFrameBlending = InitFrameBlending.KDE
    
    n_main_steps: int = 10
    detector: KeypointDetector = KeypointDetector.AKAZE
    matcher: KeypointMatcher   = KeypointMatcher.BF_NORM_HAMM
    
    
    
    def _sanitize_input_video_path(self) -> None:
 
        # single video path ----------------------------------------------------
        if os.path.isfile(self.input_video_path):
            ext = os.path.splitext(self.input_video_path)[1]
            if ext not in ALLOWED_VIDEO_EXT:
                raise ValueError("path to single file is not a valid video file!")
            else:
                return # found a good single video file
        
        # video folder path ----------------------------------------------------
        elif os.path.isdir(self.input_video_path):
            vids = [vn for xt in ALLOWED_VIDEO_EXT for vn in glob(os.path.join(self.input_video_path, f"*{xt}"))]
            if len(vids) == 0:
                raise ValueError("found no valid video files in video folder!")
            else:
                return # got a folder with at least one good video file in it

        # invalid path ---------------------------------------------------------
        else:
            raise ValueError("invalid input_video_path! (neither a file nor a folder)")
        
    def _sanitize_static_window(self) -> None:
        # window json path ---------------------------------------------------------
        if os.path.isfile(self.static_window):
            ext = os.path.splitext(self.static_window)[1]
            if ext != ".json":
                raise ValueError("path to static window json is not a json file")
            else:
                return # found a good json file
        
        # START-xx:xx:xx -----------------------------------------------------------
        elif len(re.findall(r"START-\d\d:\d\d:\d\d", self.static_window)) > 0:
            return # found a good string arg
        
        # END-xx:xx:xx -------------------------------------------------------------
        elif len(re.findall(r"END-\d\d:\d\d:\d\d", self.static_window)) > 0:
            return # found a good string arg

        # xx:xx:xx-xx:xx:xx --------------------------------------------------------
        elif len(re.findall(r"\d\d:\d\d:\d\d-\d\d:\d\d:\d\d", self.static_window)) > 0:
            return # found a good string arg

        # invalid static window argument -------------------------------------------
        else:
            raise ValueError("invalid static_window argument!")

    def _sanitize_json(self) -> None:
        ... # TODO: if a json file specified, read it, verify that it has correct contents

    def sanitize(self) -> None:
        self._sanitize_input_video_path()
        self._sanitize_static_window()
        self._sanitize_json()
        




        