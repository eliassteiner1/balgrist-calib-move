import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from calib_move.util.timestring import sec_2_tstr, tstr_2_sec


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    h = 23
    m = 23
    s = 38.2340
    print(sec_2_tstr(h*3600 + m*60 + s))    
    
    
    somestring = "asfölkj ölkölj 01:01:03ölkj ölkjöl kj 00:01:02 ölkj jk_élkjöa2@ 1:01:30 jö lkjölkj 1d:34:04"
    print(tstr_2_sec(somestring))
    


    
    
    


