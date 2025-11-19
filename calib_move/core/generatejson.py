import os
from   glob import glob
import tyro

from   .cliargs import ALLOWED_VIDEO_EXT


def generate_template_json(vid_folder_path: str):
    # create a template json from a folder with all video of type "ALLOWED_VIDEO_EXT"
    vid_glob = [vd for xt in ALLOWED_VIDEO_EXT for vd in glob(os.path.join(vid_folder_path, f"*{xt}"))]
    vid_dict = {f"{os.path.basename(vid)}": "hh:mm:ss-hh:mm:ss" for vid in vid_glob}
    
    # find longest key name
    max_key_len = max(len(k) for k in vid_dict.keys())
    
    # picece together json
    lines = ["{"]
    for key, value in vid_dict.items():
        space = " "
        # add " characters to key (makes fstring syntax easier)
        key = f"\"{key}\"" 
        # add 4 spaces in the front (indent) padd each key to maximum length on the right with spaces, also add values
        lines.append(f"{4*space}{key:<{max_key_len+2}}: \"{value}\",")
    # strip last comma to make it a valid json file
    lines[-1] = lines[-1].strip(",")
    lines.append("}")
    
    with open("scripts/static_window_template.json", mode="w", encoding="utf-8") as file:
        file.write("\n".join(lines))
        
def main_generate_json(argv=None):
    CLIARGS_GEN_JSON = tyro.cli(generate_template_json, args=argv) # also calls the function!