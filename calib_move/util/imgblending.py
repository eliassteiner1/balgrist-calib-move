import cv2 as cv
import numpy as np
from   numpy.typing import NDArray
import scipy.stats


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

