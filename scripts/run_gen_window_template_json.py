import os
import sys

# TODO: watch out if this works if you run it like ./scripts/run.py and not just as ./run.py!
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import calib_move


if __name__ == "__main__":
    calib_move.core.generatejson.generate_template_json()