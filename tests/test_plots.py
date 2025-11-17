import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from   calib_move.core.plotting import plot_results


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    # simulate result of stacked homographies
    n = 10
    hs = np.zeros((n, 3, 3))
    hs[:, 0, 2] = (np.random.rand(n, ) - 0.5)*1800 # x translation part
    hs[:, 1, 2] = (np.random.rand(n, ) - 0.5)*400 # y translation part
    
    plot_img = plot_results(
        hs, 
        ftot=30*36000, fpsc=30, 
        vidname="vid_1234987_qwerbvxqwerbvcxbqwerxqbwverbvq_1234",
        static_window=["01:00:00", "08:55:00"]
    )

    
    
    