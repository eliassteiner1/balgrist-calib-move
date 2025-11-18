import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from calib_move.main import main_func


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    argv = [
        "--input-video-path", "H:/code_elias/random_scrips_balgrist/test_videos/vid_3.mp4",
        "--static-sequence", "START",
    ]
    main_func(argv=argv)
