import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import calib_move


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    argv = [
        "--input-video-path", "H:/code_elias/random_scrips_balgrist/test_videos/vid_2.mp4",
        "--static-sequence", "START",
    ]
    calib_move.main.main_func(argv=argv)
