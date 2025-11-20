import numpy as np
from   numpy.typing import NDArray
import plotly.graph_objects as go
from   plotly.subplots import make_subplots

from   ..util.timestring import sec_2_tstr
from .cliargs import CLIArgs
from .videocontainer import VideoContainer
from ..config.plotconfig import PlotConfig
from ..util.plot import fig_2_numpy


def plot_video_ho(CLIARGS: CLIArgs, video: VideoContainer, CFG: PlotConfig) -> list[NDArray]:
    
    dat_msk = np.array(video.ho_errors) == 1
    dat_ts = np.linspace(0, video.stot, CLIARGS.n_main_steps) # make this not masked, need last element for layout 
    dat_x = np.where(dat_msk, np.nan, np.array(video.ho_arrays)[:, 0, 2])
    dat_y = np.where(dat_msk, np.nan, np.array(video.ho_arrays)[:, 1, 2])
    dat_abs = np.where(dat_msk, np.nan, np.sqrt(dat_x**2 + dat_y**2))
    dat_abs_max = max(np.nanmax(dat_abs), CFG.MIN_YRANGE_AUTOMAX)
    
    fig = make_subplots(
        rows=1, cols=2, 
        column_widths=CFG.SUBPLOT_COLWIDTHS, horizontal_spacing=CFG.SUBPLOT_SPACING,
        shared_xaxes=False, shared_yaxes=False
    )
    
    # plotting ---------------------------------------------------------------------------------------------------------
    
    # plot 1: time series ------------------------------------------------------
    fig.add_trace(go.Scatter( # main timeseries plot
        x=dat_ts, y=dat_abs,
        mode="lines+markers", connectgaps=True,
        line=dict(color=CFG.LINCOL, width=CFG.LINWIDTH, dash="dot"),
        marker=dict(color=CFG.MRKCOL, size=CFG.MRKSIZE, symbol="square"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter( # cosmetic bar right side end
        x=[dat_ts[-1], dat_ts[-1]], y=[-(CFG.PADD_ABS)*dat_abs_max, (1+CFG.PADD_ABS)*dat_abs_max],
        mode="lines",
        line=dict(color=CFG.ZRLCOL, width=CFG.ZRLWIDTH),
        zorder=-1
    ), row=1, col=1)
    fig.add_shape( # static window box
        type="rect",
        x0=video.static_window[0], y0=-(CFG.PADD_ABS/2)*dat_abs_max,
        x1=video.static_window[1], y1=(1+CFG.PADD_ABS/2)*dat_abs_max,
        line=dict(width=0),
        fillcolor=CFG.WDWCOL,
        layer="below",
    row=1, col=1)

    # plot 2: xy scatter -------------------------------------------------------
    fig.add_trace(go.Scatter( # main scatterplot
        x=dat_x, y=dat_y,
        mode="markers",
        marker=dict(color=CFG.MRKCOL, size=CFG.MRKSIZE, symbol="circle", ),
    ), row=1, col=2)
    fig.add_shape(row=1, col=2, # outer circle
        type="circle", 
        x0=-dat_abs_max, y0=-dat_abs_max,
        x1=dat_abs_max, y1=dat_abs_max,
        layer="below",
        line=dict(color=CFG.GRDCOL, width=CFG.GRDWIDTH)  
    )
    fig.add_shape(row=1, col=2, # inner circle
        type="circle", 
        x0=-dat_abs_max/2, y0=-dat_abs_max/2,
        x1=dat_abs_max/2, y1=dat_abs_max/2,
        layer="below",
        line=dict(color=CFG.GRDCOL, width=CFG.GRDWIDTH)
        
    )

    # layouting --------------------------------------------------------------------------------------------------------
    
    # general layout -----------------------------------------------------------
    fig.update_layout( # layout for all plots
        width=CFG.RES_HW[1], height=CFG.RES_HW[0],
        title=dict(
            text=f"plot for: <b>{video.name}</b>", 
            font_size=CFG.FNTSIZE_TITLE,
            x=CFG.TITLE_MAIN_XY[0], y=CFG.TITLE_MAIN_XY[1], 
            xref="container", yref="container", xanchor="left", yanchor="top",
        ),
        paper_bgcolor=CFG.BKGCOL, plot_bgcolor=CFG.BKGCOL,
        font=dict(family="JetBrains Mono", size=CFG.FNTSIZE_PLOT, color=CFG.TXTCOL),
        margin=CFG.MARGIN,
        showlegend=False,
    )
    fig.add_annotation( # artificial axis title for timeseries plot
        text="<b>|x, y| movement [px]</b>", font_size=CFG.FNTSIZE_PLOT, textangle=-90,
        x=CFG.TITLE_P1_XY[0], y=CFG.TITLE_P1_XY[1], xref="paper", yref="paper", xanchor="left", yanchor="middle",
        showarrow=False,
    )
    fig.add_annotation( # artificial axis title for scatterplot
        text="<b> (x, y) movement [px]</b>", font_size=CFG.FNTSIZE_PLOT, textangle=-90,
        x=CFG.TITLE_P2_XY[0], y=CFG.TITLE_P2_XY[1], xref="paper", yref="paper", xanchor="left", yanchor="middle",
        showarrow=False,
    )
    
    # plot 1 layout -----------------------------------------------------------
    fig.update_xaxes( row=1, col=1,
        range=[-(CFG.PADD_TS)*dat_ts[-1], (CFG.PADD_TS+1)*dat_ts[-1]],
        showgrid=True,
        zeroline=True,
        gridcolor=CFG.GRDCOL,
        zerolinecolor=CFG.ZRLCOL,
        gridwidth=CFG.GRDWIDTH,
        zerolinewidth=CFG.ZRLWIDTH,
        tickvals=np.linspace(dat_ts[0], dat_ts[-1], CFG.NTIX_TS),
        ticktext=[sec_2_tstr(sc) for sc in np.linspace(0, video.stot, CFG.NTIX_TS)],
    )
    fig.update_yaxes(row=1, col=1,
        range=[-(CFG.PADD_ABS)*dat_abs_max, (CFG.PADD_ABS+1)*dat_abs_max],
        showgrid=True,
        zeroline=True,
        gridcolor=CFG.GRDCOL,
        zerolinecolor=CFG.ZRLCOL,
        gridwidth=CFG.GRDWIDTH,
        zerolinewidth=CFG.ZRLWIDTH,
        tickformat=".1~s",
        tickvals=np.linspace(0, dat_abs_max, CFG.NTIX_ABS), 
    )
    
    # plot 2 layout -----------------------------------------------------------
    fig.update_xaxes(row=1, col=2,
        range=[-(CFG.PADD_X+1)*dat_abs_max, (CFG.PADD_X+1)*dat_abs_max],
        constrain="domain",
        scaleanchor="y2", # watch out, needs the y axis from the second plot as scaleanchor!
        showgrid=False,
        zeroline=True,
        gridcolor=CFG.GRDCOL,
        zerolinecolor=CFG.ZRLCOL,
        gridwidth=CFG.GRDWIDTH,
        zerolinewidth=CFG.ZRLWIDTH,
        tickformat=".1~s",
        tickvals=np.linspace(-dat_abs_max, dat_abs_max, CFG.NTIX_X)
    )
    fig.update_yaxes(row=1, col=2,
        range=[-(CFG.PADD_Y+1)*dat_abs_max, (CFG.PADD_Y+1)*dat_abs_max],
        constrain="domain",
        showgrid=False,
        zeroline=True,
        gridcolor=CFG.GRDCOL,
        zerolinecolor=CFG.ZRLCOL,
        gridwidth=CFG.GRDWIDTH,
        zerolinewidth=CFG.ZRLWIDTH,
        tickformat=".1~s",
        tickvals=np.linspace(-dat_abs_max, dat_abs_max, CFG.NTIX_Y)
    )

    return [fig_2_numpy(fig)]

 