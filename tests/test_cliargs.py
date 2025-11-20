import os
import sys
from   pathlib import Path
import re
import tyro
from   glob import glob
from   itertools import chain

sys.path.append(os.path.normcase(Path(__file__).resolve().parents[1]))
from   calib_move.core.cliargs import CLIArgs


def main_synth(argv=None):
    CLIARGS = tyro.cli(CLIArgs, args=argv)
    CLIARGS.sanitize()
    
    
 
if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")

    argv = [
        "--input-video-path", "H:/code_elias/random_scrips_balgrist/test_videos/",
        "--static-window",    "H:/code_elias/balgrist-calib-move/tests/test_static_window_template.json"
        # "--static-window",    "START-00:00:00",
        # "--static-window",    "00:00:00-END",
        # "--static-window",    "00:00:00-00:01:00",   
    ]
    main_synth(argv=argv)



    print("done")
    
    
    

