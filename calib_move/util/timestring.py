import re


def sec_2_tstr(seconds: float) -> str:
    
    hrs = round(seconds // 3600)
    min = round((seconds % 3600) // 60)
    sec = round(seconds % 60)

    return f"{hrs:02d}:{min:02d}:{sec:02d}"
    
def tstr_2_sec(timestr: str) -> int:
    
    substr = re.findall(r"\d\d:\d\d:\d\d", timestr)[0]
    hrs, min, sec = substr.split(":")
    seconds = int(hrs)*3600 + int(min)*60 + int(sec)
    
    return seconds
   