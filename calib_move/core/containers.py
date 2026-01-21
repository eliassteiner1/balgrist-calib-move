import re
from   dataclasses import dataclass, field
from   pathlib import Path
from   typing import Annotated
from   numpy.typing import NDArray
import tyro

from ..util.util import json_2_dict

from ..config.coreconfig import ALLOWED_VIDEO_EXT
from ..config.coreconfig import InitFrameBlending
from ..config.coreconfig import KeypointDetector
from ..config.coreconfig import KeypointMatcher


@dataclass(frozen=True)
class CLIArgs:
    
    # required ---------------------------------------------------------------------------------------------------------
    input_path: Annotated[
        Path, tyro.conf.arg(metavar="{<single-video-path>,<video-folder-path>}")
    ]
    """ path to one video or a folder containing at least one video which should be analyized. """
    
    output_path: Path
    """ path to the location where the result plots should be saved. """
    
    static_window: Annotated[
        str, tyro.conf.arg(metavar="{<START-hh:mm:ss>,<hh:mm:ss-END>,<hh:mm:ss-hh:mm:ss>,<json-path>}",)
    ]
    """ a certain part of the video (ideally where the camera is known to be static), relative to which the movements are estimated. can be specified explicitly via three string options or via a json file (for specifying different windows for multiple videos). """
    
    # optional ---------------------------------------------------------------------------------------------------------
    plot_name: str = "camera_movement_plot"
    """ base name for the output png file (will be: <plot_name>.png). """
    
    n_init_steps: int = 8
    """ number of equally spaced steps (in the static window) for which frames are extracted and combined to form one good reference image without moving elements. the homography is estimated relative to this static image for all other parts of the video. """
    
    init_frame_blending: InitFrameBlending = InitFrameBlending.KDE
    """ method for combining multiple frames (from the static window) to ideally remove moving elements. """

    n_main_steps: int = 16
    """ number of equally spaced steps (in the input video) for which the homography is estimated relative to the static frame. """
    
    detector: KeypointDetector = KeypointDetector.AKAZE
    """ cv2 keypoint detector type. """
    
    matcher: KeypointMatcher = KeypointMatcher.BF_NORM_HAMM
    """ cv2 keypoint matching type. (L2 is good for SIFT or SURF, HAMMING is good for binary descriptors e.g. ORB AKAZE or BRISK). """

    def _sanitize_input_video_path(self) -> None:

        # single video path ----------------------------------------------------
        if self.input_path.is_file():
            if self.input_path.suffix not in ALLOWED_VIDEO_EXT:
                raise ValueError(f"path to single video is not a valid video file! (got {self.input_path})")
            else:
                return # OK (found a good single video file)
        
        # video folder path ----------------------------------------------------
        elif self.input_path.is_dir():
            vids = [vd for xt in ALLOWED_VIDEO_EXT for vd in self.input_path.glob(f"*{xt}")]
            if len(vids) == 0:
                raise ValueError(f"found no valid video files in video folder! (got {self.input_path})")
            else:
                return # OK (got a folder with at least one good video file in it)

        # invalid path ---------------------------------------------------------
        else:
            raise ValueError(f"invalid input_video_path, neither file nor folder! (got {self.input_path})")

    def _sanitize_output_path(self) -> None:
        
        if self.output_path.is_dir() is False:
            raise ValueError(f"output path is not a directory! (got {self.output_path})")
        
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
        if self.input_path.is_file():
            videos = [self.input_path]
        else: 
            videos = [Path(vd) for xt in ALLOWED_VIDEO_EXT for vd in self.input_path.glob(f"*{xt}")]
        
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

    def _sanitize_steps(self) -> None:
        if self.n_init_steps <= 1:
            raise ValueError(f"{self.n_init_steps=} too small! (minimum 2)")
        
        if self.n_main_steps <= 1:
            raise ValueError(f"{self.n_main_steps=} too small! (minimum 2)")
     
    def _sanitize_detector_matcher(self) -> None:        
        if (self.detector is KeypointDetector.SIFT) and (self.matcher is KeypointMatcher.BF_NORM_HAMM):
            raise ValueError(
                f"BF_NORM_HAMM can only be used with binary descriptors such as ORB or AKAZE! (got {self.detector})"
            )
        if (self.detector is KeypointDetector.ORB or self.detector is KeypointDetector.AKAZE) and (self.matcher is KeypointMatcher.BF_NORM_L2):
            raise ValueError(
                f"With binary descriptors (ORB, AKAZE) it is preferred to use BF_NORM_HAMM! (got {self.detector})"
            )
           
    def sanitize(self) -> None:
        self._sanitize_input_video_path()
        self._sanitize_output_path()
        self._sanitize_static_window()
        self._sanitize_steps()
        self._sanitize_detector_matcher()

@dataclass
class VideoContainer:

    path: Path
    fpsc: float
    ftot: int
    
    H: int
    W: int

    static_window: tuple[float, float] # [start_second, end_second]

    movements: list[float] = field(default_factory=list)
    agreements: list[float] = field(default_factory=list)
    errors: list[bool] = field(default_factory=list)

    detections: list[any] = field(default_factory=list)
    sections: list[NDArray] = field(default_factory=list)

    @property
    def stot(self):
        return self.ftot / self.fpsc

    @property
    def name(self):
        return self.path.name

    def sanitize(self, CLIARGS: CLIArgs):

        # framerate valid?
        if self.fpsc <= 0:
            raise ValueError(f"framerate ({self.fpsc=}) <= 0! ({self.name})")
        # n total frames valid?
        if self.fpsc <= 0:
            raise ValueError(f"total number of frames ({self.ftot=}) <= 0! ({self.name})")

        # window start and end switched
        if self.static_window[0] >= self.static_window[1]:
            raise ValueError(f"window specs invalid, start later than end ({self.static_window=})! ({self.name})")

        # window starts before 0
        if self.static_window[0] < 0:
            raise ValueError(f"window starts too early ({self.static_window=})! {(self.name)}")

        # window ends after video duration
        if self.static_window[1] > self.stot:
            raise ValueError(f"window ends after video end ({self.static_window=})! ({self.name})")

        # video is way too short for the amount of main steps
        if self.ftot < 3*CLIARGS.n_main_steps:
            raise ValueError(f"{CLIARGS.n_main_steps=} too large for video with only {self.ftot=}! ({self.name})")

        if (self.static_window[1] - self.static_window[0]) * self.fpsc < 3*CLIARGS.n_init_steps:
            raise ValueError(f"{CLIARGS.n_init_steps=} too large for window of ({self.static_window=})! ({self.name})")
        
        





        