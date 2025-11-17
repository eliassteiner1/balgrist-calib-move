import numpy as np
from   numpy.typing import NDArray
import cv2 as cv
import plotly.graph_objects as go
from   plotly.subplots import make_subplots

from   ..util.timestring import tstr_2_sec
from   ..util.timestring import sec_2_tstr


def fig_2_numpy(figure: go.Figure) -> NDArray:
    fig_bytes = figure.to_image(format="png")
    img_bytes = np.frombuffer(fig_bytes, np.uint8)
    img = cv.imdecode(img_bytes, cv.IMREAD_UNCHANGED)
    return img

def plot_results(hs, ftot, fpsc, vidname, static_window: tuple[str, str]):
    
    flor_for_max_y_range = 50 # controlling how low the range of the y axis can go when automatically adjusting range
    
    t_steps = np.linspace(0, ftot/fpsc, hs.shape[0]) # x axis is in seconds, assuming hs is at regular intervals + full!
    abs_data = np.sqrt(hs[:, 0, 2]**2 + hs[:, 1, 2]**2)
    abs_max = max(abs_data.max(), flor_for_max_y_range)
    
    TXTCOL = "rgba(20, 20, 20, 1.0)"

    BKGCOL = "rgba(255, 255, 255, 0.0)"
    
    LINCOL = "rgba(255, 0, 0, 0.3)"
    MRKCOL = "rgba(255, 0, 0, 1.0)"
    
    GRDCOL = "rgba(200, 200, 200, 1.0)"
    ZRLCOL = GRDCOL
    GRDWIDTH = 2.0
    ZRLWIDTH = 5.0
    
    fig = make_subplots(
        rows=1, cols=2, 
        column_widths = [0.78, 0.22], horizontal_spacing = 0.12,
        shared_xaxes=False, shared_yaxes=False)
    
    fig.add_trace(go.Scatter( # main plot
        x = t_steps,
        y = abs_data,
        mode = "lines+markers",
        line = dict(color = LINCOL, width = 3, dash = "dot"),
        marker = dict(color = MRKCOL, symbol = "square", size = 8),
    ), row = 1, col = 1)
    
    fig.add_trace(go.Scatter( # cosmetic bar
        x = [t_steps.max(), t_steps.max()],
        y = [-0.1*abs_max, 1.2*abs_max],
        mode = "lines",
        line = dict(color = ZRLCOL, width = ZRLWIDTH),
        zorder = -1
    ), row = 1, col = 1)
    
    fig.add_shape(row = 1, col = 1, # static window box
        type = "rect",
        x0 = tstr_2_sec(static_window[0]), y0 = -0.05*abs_max,
        x1 = tstr_2_sec(static_window[1]), y1 = 1.05*abs_max,
        layer = "below",
        line = dict(width = 0),
        fillcolor = "rgba(144, 213, 255, 0.33)"
        
    )
    
    fig.add_trace(go.Scatter( # point scatter x-y
        x = hs[:, 0, 2],
        y = hs[:, 1, 2],
        mode = "markers",
        marker = dict(color = MRKCOL, symbol = "circle", size = 3),
    ), row = 1, col = 2)
    
    fig.add_shape(row = 1, col = 2, # outer circle
        type = "circle", 
        x0 = -abs_max, y0 = -abs_max,
        x1 =  abs_max, y1 =  abs_max,
        layer = "below",
        line = dict(color = GRDCOL, width = GRDWIDTH)  
    )
    
    fig.add_shape(row = 1, col = 2, # inner circle
        type = "circle", 
        x0 = -abs_max/2, y0 = -abs_max/2,
        x1 =  abs_max/2, y1 =  abs_max/2,
        layer = "below",
        line = dict(color = GRDCOL, width = GRDWIDTH)
        
    )
    
    # subplot 1 ----------------------------------------------------------------
    n_tix = 6
    fig.update_xaxes( row = 1, col = 1,
        range = [-0.04*t_steps.max(), 1.04*t_steps.max()],
        showgrid = True,
        zeroline = True,
        gridcolor = GRDCOL,
        zerolinecolor = ZRLCOL,
        gridwidth = GRDWIDTH,
        zerolinewidth = ZRLWIDTH,
        tickvals = np.linspace(t_steps.min(), t_steps.max(), n_tix),
        ticktext = [sec_2_tstr(s) for s in np.linspace(0, ftot/fpsc, n_tix)],
    )
    
    fig.update_yaxes(row = 1, col = 1,
        range = [-0.1*abs_max, 1.1*abs_max],
        showgrid = True,
        zeroline = True,
        gridcolor = GRDCOL,
        zerolinecolor = ZRLCOL,
        gridwidth = GRDWIDTH,
        zerolinewidth = ZRLWIDTH,
        tickformat = ".1~s",
        tickvals = np.linspace(0, abs_max, 4), 
    )
    
    # subplot 2 ----------------------------------------------------------------
    fig.update_xaxes(row = 1, col = 2,
        range = [-1.1*abs_max, 1.1*abs_max],
        constrain = "domain",
        scaleanchor = "y2", # watch out, needs the y axis from the second plot as scaleanchor!
        showgrid = False,
        zeroline = True,
        gridcolor = GRDCOL,
        zerolinecolor = ZRLCOL,
        gridwidth = GRDWIDTH,
        zerolinewidth = ZRLWIDTH,
        tickformat = ".1~s",
        tickvals = np.linspace(-abs_max, abs_max, 3)
    )
    
    fig.update_yaxes(row = 1, col = 2,
        range = [-1.1*abs_max, 1.1*abs_max],
        constrain = "domain",
        showgrid = False,
        zeroline = True,
        gridcolor = GRDCOL,
        zerolinecolor = ZRLCOL,
        gridwidth = GRDWIDTH,
        zerolinewidth = ZRLWIDTH,
        tickformat = ".1~s",
        tickvals = np.linspace(-abs_max, abs_max, 5)
    )
    
    # general layout -----------------------------------------------------------
    fig.update_layout(
        title = dict(
            text = f"plot for: <b>{vidname}</b>", 
            x = 0.015, y = 0.92, xref = "container", yref = "container", xanchor = "left", yanchor="top",
            font_size = 20),
        paper_bgcolor = BKGCOL,
        plot_bgcolor = BKGCOL,
        font = dict(family = "JetBrains Mono", size = 16, color = TXTCOL),
        width = 1200,
        height = 300,
        margin = dict(l = 70+20, r = 20, t = 45+20, b = 20, pad = 5),
        showlegend = False
    )
    
    fig.add_annotation(
        text = "<b>|x, y| movement [px]</b>", font_size = 16, textangle = -90,
        x = -0.07, y = 0.5, xref = "paper", yref = "paper", xanchor = "left", yanchor="middle",
        showarrow = False,
    )
    
    fig.add_annotation(
        text = "<b> (x, y) movement [px]</b>", font_size = 16, textangle = -90,
        x = 0.74, y = 0.5, xref = "paper", yref = "paper", xanchor = "left", yanchor="middle",
        showarrow = False,
    )
    
    fig.show() # only for debug
    
    return fig_2_numpy(fig) 
 
 
 
 