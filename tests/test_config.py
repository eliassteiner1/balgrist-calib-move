import os
import sys
import re
import tyro
from   glob import glob

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from   calib_move.core.config import CLIArgs


def main_synth(argv=None):
    cli_args = tyro.cli(CLIArgs, args=argv)
    cli_args.sanitize()
    
 
if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")

    argv = [
        "--input-video-path", "H:/code_elias/random_scrips_balgrist/test_videos/",
        "--static-window",    "START-00:00:00",   
    ]
    main_synth(argv=argv)
    print("done")
    

