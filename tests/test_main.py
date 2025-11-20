import os
import sys
from   pathlib import Path

sys.path.append(os.path.normcase(Path(__file__).resolve().parents[1]))
from calib_move.main import main_func


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    argv = [
        "--input-video-path", "H:/code_elias/random_scrips_balgrist/test_videos/",
        # "--static-window", "H:/code_elias/balgrist-calib-move/tests/test_static_window_template.json"
        "--static-window", "START-00:03:00",
        "--n_init-steps", "3",
        "--n_main-steps", "4",
    ]
    main_func(argv=argv)
[]