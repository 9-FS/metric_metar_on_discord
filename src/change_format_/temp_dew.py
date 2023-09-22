# Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import re
from weather_minimums import WEATHER_MIN


def change_format_temp_dew(info: str) -> str|None:
    re_match: re.Match|None


    # temperature and dewpoint
    re_match=re.search("^(?P<temperature>[M]?[0-9]{2})/(?P<dewpoint>([M]?[0-9]{2})?)$", info)
    if re_match!=None:
        dewpoint: str=re_match.groupdict()["dewpoint"].replace("M", "-")
        info_new: str
        temperature: str=re_match.groupdict()["temperature"].replace("M", "-")  # replace M with proper minus


        if dewpoint=="":
            info_new=f"{temperature}°C"
        else:
            info_new=f"{temperature}°C/{dewpoint}°C"
        
        if ("temp_min" in WEATHER_MIN and int(temperature)<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<int(temperature)):    # if temperature outside limits: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"