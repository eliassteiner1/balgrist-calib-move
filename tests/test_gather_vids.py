import os
import sys
from   pathlib import Path

sys.path.append(os.path.normcase(Path(__file__).resolve().parents[1]))
from calib_move.core.gather import gather_videos
from calib_move.core.cliargs import CLIArgs


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    CLIARGS_SYNTH = CLIArgs(
        input_video_path=Path("H:/code_elias/random_scrips_balgrist/test_videos/"),
        
        # static_window="00:03:00-END",
        # static_window="START-00:02:00",
        # static_window="00:01:00-00:03:00",
        static_window="H:/code_elias/balgrist-calib-move/tests/test_static_window_template.json",
    )
    CLIARGS_SYNTH.sanitize()
    
    
    
    videos = gather_videos(CLIARGS_SYNTH)
    for i, vid in enumerate(videos):
        print(f"element nr {i} in videos:")
        print(vid)
    
    print("done")