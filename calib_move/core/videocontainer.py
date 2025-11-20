from   dataclasses import dataclass, field
import os
from   pathlib import Path
from   numpy.typing import NDArray

from .cliargs import CLIArgs


@dataclass
class VideoContainer:
    # TODO: rename this stuff a bit
    
    path: Path #TODO: make this path object (any anywhere else)
    fpsc: float
    ftot: int
    
    static_window: tuple[float, float] # [start_second, end_second]
    
    ho_arrays: list[NDArray] = field(default_factory=list)
    ho_errors: list[bool] = field(default_factory=list)
    
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
        