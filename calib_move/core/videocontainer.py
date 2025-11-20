from   dataclasses import dataclass, field
import os
from   pathlib import Path
from   numpy.typing import NDArray


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
        return os.path.basename(self.path)
        
    def sanitize(self):
        ...
        # check a few things [window withing total len, nonegative, min length, weird framerate, etc]
        # TODO: sanitize, check if window within video
        # also check if window numbers are not inverted!
        