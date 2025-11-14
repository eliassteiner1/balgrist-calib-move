import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from   calib_move.main import plot_results_multi


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    # simulate result of stacked homographies
    n = 50
    hs = np.zeros((n, 3, 3))
    hs[:, 0, 2] = (np.random.rand(n, ) - 0.5)*400 # x translation part
    hs[:, 1, 2] = (np.random.rand(n, ) - 0.5)*400 # y translation part
    
    plot_results_multi(hs)
    