import os
from   dataclasses import dataclass


@dataclass
class CLIArgs:
    """
    controls the cli of tyro and directly stores the input arguments (sys.argv)
    
    Attributes:
        input_video_path: path to the video that should be analyzed
        static_sequence: either START / END / maybe also something like(00:00:10 - 00:00:20)

    """
    input_video_path: str
    static_sequence: str
    
    def sanitize(self):
        ...
        # check a few things [paths exist, has some files, file contents, window inputs]
    
@dataclass
class VidStats:
    path: str
    fpsc: float
    ftot: int
    
    static_window: tuple[float, float]
    
    @property
    def stot(self):
        return self.ftot / self.fpsc
    
    @property
    def name(self):
        return os.path.basename(self.path)
        
    def sanitize(self):
        ...
        # check a few things [window withing total len, nonegative, min length, weird framerate, etc]