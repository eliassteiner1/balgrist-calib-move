from tqdm.auto import tqdm
import time
import os


def trunc_str(name: str, n: int) -> str:
    if len(name) > n:
        return name[0:n-1] + "…"
    else:
        return name

def pbar(*args, desc=None, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}]", unit_scale=True, **kwargs):
    if desc is not None:
        desc = trunc_str(desc, 32)
        desc = f"{desc:<32}"
    if desc is None:
        desc = ""
        desc = f"{desc:<32}"

    return tqdm(*args, desc=desc, bar_format=bar_format, unit_scale=unit_scale, **kwargs)


    

    
    
    