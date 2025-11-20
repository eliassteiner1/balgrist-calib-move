import cv2 as cv
import plotly.graph_objects as go
import numpy as np
from   numpy.typing import NDArray


def fig_2_numpy(figure: go.Figure) -> NDArray:
    fig_bytes = figure.to_image(format="png")
    img_bytes = np.frombuffer(fig_bytes, np.uint8)
    img = cv.imdecode(img_bytes, cv.IMREAD_UNCHANGED)
    
    return img