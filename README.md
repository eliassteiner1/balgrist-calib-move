<div align="center">
<h1>calib-move</h1>
</div>

A simple utility package for determining whether a supposedly static camera moved from a video. Can process multiple videos at in one batch and generate plots for each video to quickly overview the results.

## **🔍︎ Contents**
- movement analysis (main): read in a single video or a folder of videos and process each video to analyize whether the camera has moved with respect to a certain static part of the video (has to be specified). A robust reference image is constructed by blending multiple frames form the static window together to remove moving elements. Then a homography to all the other parts of the video is estimate with respect to the reference frame by using commony keypoint detection and matching techniques (SIFT, ORB, AKAZE). The linear part of this homography is used to detect small-scale movement of the static background in the camera image.
- generating template json (helper function): the static window for multiple videos can be specified using a json file. to generate a template for a certain folder containing multiple videos use this function


## **🏗️ Installation**

### **1. clone the repository**
```
mkdir <repo-folder>
cd <repo-folder>
gitclone https://github.com/eliassteiner1/balgrist-calib-move.git
```

### **2.a use locally (from folder)**

go to folder where the repository is cloned
```
cd <repo-folder>
```

install reqirements
```
pip install requirements.txt
```

Run the two main scripts of the package locally (no installation with pip necessary):
```
python <repo-folder>/scripts/run.py
python <repo-folder>/scripts/run_generate_template_json.py
```


### **2.b install with pip**

go to folder where the repository is cloned
```
cd <repo-folder>
```

install with pip. (using `-e` installs in editable mode, so that changes in the source files are immediately updated when running scripts)
```
pip install .
pip install -e .
```

this installs two new console commands to the environment
```
calib-move-run
calib-move-generate-template-json
```

## **🕹️ Using the Package**

### **run movement analysis (main)**
use either `calib-move-run` from the command line (when installed) or directly run `python <repo-folder>/scripts/run.py` (when running from source). In both cases, multiple arguments can be given:

- `-h`: prints a help window with info regarding the command arguments

- `--input-video-path <path>` **(required)**: specify the path to either a single valid video file or a folder containing at least one video file to be processed

- `--static-window <string or path>` **(required)**: specify the timestamps for the static window in the video

  - `<string>` : preferred when processing just one video or when the exact same window is applied to multiple videos (in the same folder). There are three different variants to explicitly specify a static window:

    - `START-hh:mm:ss`: represents a static window from the start of a video up to a certain timestamp.

    - `hh:mm:ss-END`: represents a static window starting at some timestamp up to the end of the video.

    - `hh:mm:ss-hh:mm:ss`: represents a static window starting and ending at specific timestamps

  - `<json path>` when loading multiple videos and a different static window should be used for every one, a json file can be used to specify them. the file is a single dict, containing a key (video name) for each video that is specified in `--input-video-path`. The values of the dict are the same timestamp-strings as before. A template of this file can be gnerated using the helper function from the next section! for example:
    ```
    {
      "video_1.mp4": "00:02:21-00:05:00",
      "video_2.mp4": "START-00:03:28",
      "video_3.mp4": "01:12:04-END",
      ...
    }
    ```
    
- `--n-init-steps`: number of equally spaced steps (in the static window) for which frames are extracted and combined to form one good reference image without moving elements. the homography is estimated relative to this static image for all other parts of the video.

- `--init-frame-blending` {MEDIAN,MODE,KDE}: method for combining multiple frames (from the static window) to ideally remove moving elements. 

- `--n-main-steps`: number of equally spaced steps (in the input video) for which the homography is estimated relative to the static frame.

- `--detector` {AKAZE,SIFT,ORB}: cv2 keypoint detector type. 

- `--matcher` {BF_NORM_L2,BF_NORM_HAMM}: cv2 keypoint matching type. (L2 is good for SIFT or SURF, HAMMING is good for binary descriptors e.g. ORB AKAZE or BRISK). 

### **generate template json (helper function)**
use either `calib-move-generate-template-json` from the command line (when installed) or directly run `python <repo-folder>/scripts/run_generate_template_json.py` (when running from source).

- `-h`: prints a help window with info regarding the command arguments

- `--vid-folder-path`: path to the folder containing the videos that will be processed. The output will be a json file with a key for each video name found in the folder and a placeholder timestamp string. The file can then be edited manually. for example:
    ```
    {
      "video_1.mp4": "hh:mm:ss-hh:mm:ss",
      "video_2.mp4": "hh:mm:ss-hh:mm:ss",
      "video_3.mp4": "hh:mm:ss-hh:mm:ss",
      ...
    }
    ```
  
## **✨ Output**
The main analysis will save a plot for all the specified and processed videos in the `<repo-folder>/outputs` folder. On the left side, this plot shows the absolute linear movement of the image over the entire video-timeline (static reference window in blue). On the right side, a scatterplot shows the individual x-y movement for each timestep. 

<p align="center">
  <img src="outputs/plot_results.png" width="800" alt="example plot output" />
</p>

## **🎫 License**
This project is licensed under the **MIT License**. See the [LICENSE](https://github.com/eliassteiner1/balgrist-calib-move/blob/main/LICENSE) file for details.

## **🤝 Acknowledgements**
ToDo
