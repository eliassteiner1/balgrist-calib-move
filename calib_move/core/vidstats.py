from   dataclasses import dataclass
import os


@dataclass
class VidInfo:
    path: str
    fpsc: float
    ftot: int
    
    static_window: tuple[float, float] # [start_second, end_second]
    
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
        