# Copyright (c) 2024 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import re
from weather_minimums import WEATHER_MIN


def change_format_weather(info_list: list, i: int) -> str|None:
    re_match: re.Match|None


    # weather
    re_match=re.search("^(?P<plus_minus>[+-]?)(?P<weather>([A-Z]{2})+)$", info_list[i])
    if re_match!=None:
        bold: bool
        info_new: str
        plus_minus: str=re_match.groupdict()["plus_minus"]
        weather: str   =re_match.groupdict()["weather"]

        if i==0:    # if aerodrome identifier: just forward, don't mark; for example EDGS would be marked all the time otherwise because of GS
            return f" {info_list[i]}"


        info_new=f"{plus_minus}{weather}"

        for j in range(0, len(weather), 2):
            if "weather_forbidden" in WEATHER_MIN and re.search(WEATHER_MIN["weather_forbidden"], weather[j:j+2])!=None:    # do not fly during this weather; visibility, icing, storms...
                bold=True
                break
        else:   # no problematic weather found
            bold=False

        if bold==True:
            info_new=f"**{info_new}**"
        return f" {info_new}"
    