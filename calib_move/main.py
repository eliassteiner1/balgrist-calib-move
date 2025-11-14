from   dataclasses import dataclass
import numpy as np
import tyro
from   numpy.typing import NDArray
from   tqdm import tqdm as tqdm_bar
import cv2 as cv
import scipy.stats

import plotly.graph_objects as go
import matplotlib.pyplot as plt
from   plotly.subplots import make_subplots



@dataclass
class CLIArgs:
    """
    controls the cli of tyro and directly stores the input arguments (sys.argv)
    
    Attributes:
        input_video_path: path to the video that should be analyzed
        static_sequence: either START / END / maybe also something like(00:00:10 - 00:00:20)

    """
    input_video_path: str
    static_sequence: str


def calc_median_image(img_list: list[NDArray]) -> NDArray:
    
    img_stack = np.array(img_list)
    median_image = np.median(img_stack, axis=0).astype(np.uint8)
    return median_image

def calc_mode_image(img_list: list[NDArray]) -> NDArray:
    
    img_stack = np.array(img_list)
    mode_image = scipy.stats.mode(img_stack, axis=0)[0].astype(np.uint8)
    return mode_image

def calc_kde_image(img_list: list[NDArray]) -> NDArray:
    
    desired_n_px_for_kde = 1e6
    bandwidth = 10
    
    # compress image if too large
    H, W = img_list[0].shape # store for reverting compression
    scale_factor = np.sqrt(desired_n_px_for_kde / (H*W)) # compress by this factor to not exceed memory!
    if scale_factor < 1:
        img_list = [cv.resize(img, None, fx=scale_factor, fy=scale_factor) for img in img_list]
    
    img_stack = np.array(img_list)
    img_stack_compr = (img_stack / 2).astype(np.uint8) # compress color channels

    # prepare kde kernels
    gray_vals = np.arange(128, dtype=np.int8) # need singed ints here for computing the kernels
    dist = np.abs(gray_vals[:, None] - gray_vals[None, :])  # (256, 256) pairwise distances between all gray values
    kernel_mtx = np.clip(bandwidth - dist, 0, None).astype(np.uint8) # Apply triangle kernel: (h - |i-j|), clipped at 0

    # do kde
    queried_kernels = kernel_mtx[img_stack_compr, :] # n, H, W, 128
    density = np.sum(queried_kernels, axis=0) # add kernels over the stack dimension -> color density at each pixel
    kde_image = (np.argmax(density, axis=-1) * 2).astype(np.uint8) # find the most "dense" color val for each pixel

    # upscale again if image was too large
    if scale_factor < 1:
        kde_image = cv.resize(kde_image, (W, H), interpolation=cv.INTER_CUBIC)
        
    # slightly smoothen image
    kde_image = cv.GaussianBlur(kde_image, (11, 11), 0)

    return kde_image

def generate_pivot_frame():
    # should grab frames at some interval from the static part of the video (either start end or some window)
    # maybe some params like, how many frames, which type of combination method
    # combines them all into a pivot frame (using specified method)

    pass



def process_one_video(vid_path, detector, matcher):
    
    # get some video information
    cap = cv.VideoCapture(vid_path)
    fpsc = cap.get(cv.CAP_PROP_FPS)
    ftot = cap.get(cv.CAP_PROP_FRAME_COUNT)
    
    # gather and calculate init frame (extract + blend)
    n_init_frames = 10
    l_init_seq = 0.05 # percent of video
    init_frame_idx = np.linspace(0, l_init_seq*ftot, n_init_frames, dtype=np.int64)
    init_frame_list = []

    for fidx in tqdm_bar(init_frame_idx, desc="constructing pivot frame", unit_scale=True):
        cap.set(cv.CAP_PROP_POS_FRAMES, fidx)
        ret, img = cap.read()
        if ret is False:
            raise ValueError("could not read frame") #TODO add some info here
        else:
            init_frame_list.append(cv.cvtColor(img, cv.COLOR_BGR2GRAY))    
    pivot_frame = calc_median_image(init_frame_list)
    
    # do detection on initial frame
    pivot_kps, pivot_dsc = detector.detectAndCompute(pivot_frame, None)
        
    # store homographies
    homographies = []

    # step through main video, for each interval frame
    n_main_steps = 10
    frame_idx = np.linspace(0, ftot-1, n_main_steps, dtype=np.int64)
    for fidx in tqdm_bar(frame_idx, desc="stepping through video  ", unit_scale=True):
    
        # grab frame and do keypoint detection
        cap.set(cv.CAP_PROP_POS_FRAMES, fidx)
        ret, img = cap.read()
        if ret is False:
            raise ValueError("could not read frame") #TODO add some info here
        else:
            img_gry = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            kps_new, dsc_new = detector.detectAndCompute(img_gry, None)
            
            # do keypoint matching
            matches = matcher.match(pivot_dsc, dsc_new)
            matches = sorted(matches, key=lambda x: x.distance)
            
            # get actual coords of keypoints
            pivot_p = np.float32([pivot_kps[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            p_new = np.float32([kps_new[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

            # estimate homography w.r.t. init frame and store
            H, mask = cv.findHomography(pivot_p, p_new, cv.RANSAC, 5)
            homographies.append(H)
            
    # extract homography stats
    hs = np.array(homographies)
    
    return hs

def plot_results(hs):
    
    x_data = np.arange(hs.shape[0])
    y_data = np.abs(hs[:, 0, 2]) + np.abs(hs[:, 1, 2])
    
    TXTCOL = "rgba(20, 20, 20, 1.0)"

    BKGCOL = "rgba(255, 255, 255, 1.0)"
    
    LINCOL = "rgba(255, 0, 0, 0.3)"
    MRKCOL = "rgba(255, 0, 0, 1.0)"
    
    GRDCOL = "rgba(200, 200, 200, 1.0)"
    ZRLCOL = GRDCOL
    GRDWIDTH = 2.0
    ZRLWIDTH = 5.0
    
    
    fig = go.Figure()
    fig.add_trace(go.Scatter( # main plot
        x = x_data,
        y = y_data,
        mode = "lines+markers",
        line = dict(color = LINCOL, width = 3, dash = "dot"),
        marker = dict(color = MRKCOL, symbol = "square", size = 10),
    ))
    fig.add_trace(go.Scatter( # cosmetic bar
        x = [x_data.max(), x_data.max()],
        y = [-0.1*y_data.max(), 1.2*y_data.max()],
        mode = "lines",
        line = dict(color = ZRLCOL, width = ZRLWIDTH),
        zorder = -1
    ))
    
    fig.update_xaxes(
        range = [-0.04*x_data.max(), 1.04*x_data.max()],
        showgrid = True,
        zeroline = True,
        gridcolor = GRDCOL,
        zerolinecolor = ZRLCOL,
        gridwidth = GRDWIDTH,
        zerolinewidth = ZRLWIDTH,
        tickvals = np.linspace(x_data.min(), x_data.max(), 6),
        ticktext = ["00:00:00", "00:01:00", "00:02:00", "00:03:00", "00:04:00", "00:05:00"],
        
    )
    fig.update_yaxes(
        range = [-0.1*y_data.max(), 1.1*y_data.max()],
        showgrid = True,
        zeroline = True,
        gridcolor = GRDCOL,
        zerolinecolor = ZRLCOL,
        gridwidth = GRDWIDTH,
        zerolinewidth = ZRLWIDTH,
        tickformat = ".2~s",
        tickvals = np.linspace(0, y_data.max(), 4),
        
    )
    fig.update_layout(
        title = dict(
            text = "plot for: <b>vid_xxx_asdfasdfdasf_asdfasdfdsa_000092345.mp4</b>", 
            x = 0.015, y = 0.92, xref = "container", yref = "container", xanchor = "left", yanchor="top",
            font_size = 20),
        paper_bgcolor = BKGCOL,
        plot_bgcolor = BKGCOL,
        font = dict(family = "JetBrains Mono", size = 16, color = TXTCOL),
        width = 1200,
        height = 300,
        margin = dict(l = 80+20, r = 20, t = 45+20, b = 20, pad = 5),
        showlegend = False
    )
    fig.add_annotation(
        text = "<b>video movement [px]</b>", font_size = 16, textangle = -90,
        x = -0.08, y = 0.5, xref = "paper", yref = "paper", xanchor = "left", yanchor="middle",
        showarrow = False
        
    )

    fig.show()
    
    
    
def plot_results_multi(hs):
    
    x_steps = np.arange(hs.shape[0])
    abs_data = np.sqrt(hs[:, 0, 2]**2 + hs[:, 1, 2]**2)
    
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
        column_widths = [0.8, 0.2], horizontal_spacing = 0.04,
        shared_xaxes=False, shared_yaxes=False)
    
    fig.add_trace(go.Scatter( # main plot
        x = x_steps,
        y = abs_data,
        mode = "lines+markers",
        line = dict(color = LINCOL, width = 3, dash = "dot"),
        marker = dict(color = MRKCOL, symbol = "square", size = 8),
    ), row = 1, col = 1)
    
    fig.add_trace(go.Scatter( # cosmetic bar
        x = [x_steps.max(), x_steps.max()],
        y = [-0.1*abs_data.max(), 1.2*abs_data.max()],
        mode = "lines",
        line = dict(color = ZRLCOL, width = ZRLWIDTH),
        zorder = -1
    ), row = 1, col = 1)
    
    fig.add_trace(go.Scatter( # point scatter x-y
        x = hs[:, 0, 2],
        y = hs[:, 1, 2],
        mode = "markers",
        marker = dict(color = MRKCOL, symbol = "circle", size = 3),
    ), row = 1, col = 2)
    
    fig.add_shape(row = 1, col = 2,
        type = "circle", 
        x0 = -abs_data.max(), y0 = -abs_data.max(),
        x1 =  abs_data.max(), y1 =  abs_data.max(),
        layer = "below",
        line = dict(color = GRDCOL, width = GRDWIDTH)  
    )
    fig.add_shape(row = 1, col = 2,
        type = "circle", 
        x0 = -abs_data.max()/2, y0 = -abs_data.max()/2,
        x1 =  abs_data.max()/2, y1 =  abs_data.max()/2,
        layer = "below",
        line = dict(color = GRDCOL, width = GRDWIDTH)
        
    )
    
    # subplot 1 ----------------------------------------------------------------
    fig.update_xaxes( row = 1, col = 1,
        range = [-0.04*x_steps.max(), 1.04*x_steps.max()],
        showgrid = True,
        zeroline = True,
        gridcolor = GRDCOL,
        zerolinecolor = ZRLCOL,
        gridwidth = GRDWIDTH,
        zerolinewidth = ZRLWIDTH,
        tickvals = np.linspace(x_steps.min(), x_steps.max(), 6),
        ticktext = ["00:00:00", "00:01:00", "00:02:00", "00:03:00", "00:04:00", "00:05:00"],
    )
    
    fig.update_yaxes(row = 1, col = 1,
        range = [-0.1*abs_data.max(), 1.1*abs_data.max()],
        showgrid = True,
        zeroline = True,
        gridcolor = GRDCOL,
        zerolinecolor = ZRLCOL,
        gridwidth = GRDWIDTH,
        zerolinewidth = ZRLWIDTH,
        tickformat = ".2~s",
        tickvals = np.linspace(0, abs_data.max(), 4), 
    )
    
    # subplot 2 ----------------------------------------------------------------
    fig.update_xaxes(row = 1, col = 2,
        range = [-1.1*abs_data.max(), 1.1*abs_data.max()],
        constrain = "domain",
        scaleanchor = "y2", # watch out, needs the y axis from the second plot as scaleanchor!
        showgrid = False,
        zeroline = True,
        gridcolor = GRDCOL,
        zerolinecolor = ZRLCOL,
        gridwidth = GRDWIDTH,
        zerolinewidth = ZRLWIDTH,
        showticklabels = False,
    )
    
    fig.update_yaxes(row = 1, col = 2,
        range = [-1.1*abs_data.max(), 1.1*abs_data.max()],
        constrain = "domain",
        showgrid = False,
        zeroline = True,
        gridcolor = GRDCOL,
        zerolinecolor = ZRLCOL,
        gridwidth = GRDWIDTH,
        zerolinewidth = ZRLWIDTH,
        showticklabels = False,
    )
    
    
    
    
    # general layout -----------------------------------------------------------
    fig.update_layout(
        title = dict(
            text = "plot for: <b>vid_xxx_asdfasdfdasf_asdfasdfdsa_000092345_éélkjélkjélkj_asdfasfdasf-asdfas.mp4</b>", 
            x = 0.015, y = 0.92, xref = "container", yref = "container", xanchor = "left", yanchor="top",
            font_size = 20),
        paper_bgcolor = BKGCOL,
        plot_bgcolor = BKGCOL,
        font = dict(family = "JetBrains Mono", size = 16, color = TXTCOL),
        width = 1200,
        height = 300,
        margin = dict(l = 80+20, r = 20, t = 45+20, b = 20, pad = 5),
        showlegend = False
    )
    
    fig.add_annotation(
        text = "<b>absolute movem. [px]</b>", font_size = 16, textangle = -90,
        x = -0.08, y = 0.5, xref = "paper", yref = "paper", xanchor = "left", yanchor="middle",
        showarrow = False,
    )

    fig.show()  
    







def main_func(argv=None):
    # parse input
    cli_args = tyro.cli(CLIArgs, args=argv)
    
    # setup detector and maybe matcher (make params and keypoint type congfigurable)
    detector = cv.AKAZE_create()
    matcher = cv.BFMatcher(cv.NORM_L2, crossCheck=True)
    
    # ??? how to handle multiple file input?
    
    # ??? repeat for a whole list of videos? 
    
    # process a video -> get homography at regular intervals
    hs = process_one_video(cli_args.input_video_path, detector, matcher)
    
    # plot
    plot_results_multi(hs)
    
    # save results
    
    
    
    




    
    
