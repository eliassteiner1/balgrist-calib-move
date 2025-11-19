import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from calib_move.core.gather import gather_videos
from calib_move.core.cliargs import CLIArgs

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    CLIARGS_SYNTH = CLIArgs(
        input_video_path="H:/code_elias/random_scrips_balgrist/test_videos/vid_1.mp4",
        
        static_window="00:03:00-END",
        # static_window="START-00:02:00",
        # static_window="00:01:00-00:03:00",
        # static_window="H:/code_elias/balgrist-calib-move/tests/test_static_window_template.json",
    )
    CLIARGS_SYNTH.sanitize()
    
    videos = gather_videos(CLIARGS_SYNTH)
    for i, el in enumerate(videos):
        print(f"element nr {i} in videos:")
        print(el)
    
    print("done")