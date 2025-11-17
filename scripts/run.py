import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # watch out if this works if you run it like ./scripts/run.py and not just as ./run.py!

import calib_move

if __name__ == "__main__":
    calib_move.main.main_func()