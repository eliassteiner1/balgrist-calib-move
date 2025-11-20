import os
import re
from   dataclasses import dataclass
from   enum import Enum
import cv2 as cv
from   glob import glob
from   pathlib import Path

from ..util.imgblending import calc_median_image
from ..util.imgblending import calc_mode_image
from ..util.imgblending import calc_kde_image
from ..util.jsonio import json_2_dict

from typing import Annotated
import tyro


ALLOWED_VIDEO_EXT = [".mp4"] # TODO: check what even works with cv2, maybe move to one "param file" / config rather

class KeypointDetector(Enum):
    # TODO: don't instantiate here!
    # TODO move to config
    AKAZE = cv.AKAZE_create()
    SIFT  = cv.SIFT_create()
    ORB   = cv.ORB_create()
    
    @property
    def v(self):
        return self.value

class KeypointMatcher(Enum):
    # TODO: don't instantiate here!
    # TODO: move to config
    BF_NORM_L2 = cv.BFMatcher(cv.NORM_L2, crossCheck=True) # good for SIFT, SURF
    BF_NORM_HAMM = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True) #good for binary desc ORB, AKAZE, BRISK

    @property
    def v(self):
        return self.value
    
class InitFrameBlending(Enum):
    # TODO: move to config
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


@dataclass(frozen=True)
class CLIArgs:
    # TODO: rename this stuff a bit

    input_video_path: Annotated[Path, tyro.conf.arg(metavar="{<single-video-path>,<video-folder-path}")]
    static_window: Annotated[str, tyro.conf.arg(metavar="{START-hh:mm:ss,hh:mm:ss-END,hh:mm:ss-hh:mm:ss,<json-path>}",)]
    
    n_init_steps: int = 5
    init_frame_blending: InitFrameBlending = InitFrameBlending.KDE
    
    n_main_steps: int = 10
    detector: KeypointDetector = KeypointDetector.AKAZE
    matcher: KeypointMatcher   = KeypointMatcher.BF_NORM_HAMM

    def _sanitize_input_video_path(self) -> None:

        # single video path ----------------------------------------------------
        if self.input_video_path.is_file():
            if self.input_video_path.suffix not in ALLOWED_VIDEO_EXT:
                raise ValueError(f"path to single video is not a valid video file! (got {self.input_video_path})")
            else:
                return # OK (found a good single video file)
        
        # video folder path ----------------------------------------------------
        elif self.input_video_path.is_dir():
            vids = [vd for xt in ALLOWED_VIDEO_EXT for vd in self.input_video_path.glob(f"*{xt}")]
            if len(vids) == 0:
                raise ValueError(f"found no valid video files in video folder! (got {self.input_video_path})")
            else:
                return # OK (got a folder with at least one good video file in it)

        # invalid path ---------------------------------------------------------
        else:
            raise ValueError(f"invalid input_video_path, neither file nor folder! (got {self.input_video_path})")

    @staticmethod
    def _validate_window_str(static_window: str) -> bool:
        matches = 0
        
        # START-xx:xx:xx -------------------------------------------------------
        if len(re.findall(r"START-\d\d:\d\d:\d\d", static_window)) == 1:
            matches += 1
        # xx:xx:xx-END ---------------------------------------------------------
        if len(re.findall(r"\d\d:\d\d:\d\d-END", static_window)) == 1:
            matches += 1
        # xx:xx:xx-xx:xx:xx ----------------------------------------------------
        if len(re.findall(r"\d\d:\d\d:\d\d-\d\d:\d\d:\d\d", static_window)) == 1:
            matches += 1
        
        if matches == 1:
            return True
        else:
            return False
        
    def _validate_window_json(self) -> tuple[bool, list, list]:
        
        json_dict = json_2_dict(Path(self.static_window))
        
        # aggregate single or multiple video files to ckeck their names agains the keys in the json file
        if self.input_video_path.is_file():
            videos = [self.input_video_path]
        else: 
            videos = [Path(vd) for xt in ALLOWED_VIDEO_EXT for vd in self.input_video_path.glob(f"*{xt}")]
        
        missing_keys = []
        missing_vals = []
        for vid in videos:
             # check if the json dictionary even has a key for a certain videoNAME
            if vid.name in json_dict:
                # check if the window string for a certain key is also valid
                if self._validate_window_str(json_dict[vid.name]) is True:
                    continue
                else:
                    missing_vals.append(f"{{\"{json_dict[vid.name]}\" (for {vid.name})}}")
            else:
                missing_keys.append(vid.name)
        
        if len(missing_keys) == 0 and len(missing_vals) == 0:
            return True, missing_keys, missing_vals
        else:
            return False, missing_keys, missing_vals
         
    def _sanitize_static_window(self) -> None:
        
        if self._validate_window_str(self.static_window) is True and not Path(self.static_window).is_file():
            return # OK (found a good string arg (and it's not a json file with a matching name haha))
        
        elif Path(self.static_window).is_file() and Path(self.static_window).suffix == ".json":
            json_validate_flag, missing_keys, invalid_vals = self._validate_window_json()
            if json_validate_flag is True:
                return # OK (found a valid json (with all video keys in it and no invalid timewindows))
            else:
                raise ValueError(f"got json file but {missing_keys} keys are missing and {invalid_vals} are invalid")
        else:
            raise ValueError(f"invalid static_window, neither json nor valid window! (got {self.static_window})")

    def sanitize(self) -> None:
        
        if self.n_init_steps <= 1:
            raise ValueError(f"{self.n_init_steps=} too small! (minimum 2)")
        
        if self.n_main_steps <= 1:
            raise ValueError(f"{self.n_main_steps=} too small! (minimum 2)")
        
        self._sanitize_input_video_path()
        self._sanitize_static_window()
        
        





        