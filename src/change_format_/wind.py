# Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
from KFSconvert_to_SI import KFSconvert_to_SI
from KFSfstr          import KFSfstr
import numpy    # for crosswind component, numpy functions because of DataFrames input
import pandas
import re
from Station          import Station
from weather_minimums import WEATHER_MIN


def change_format_wind(info: str, station: Station, RWY_DB: pandas.DataFrame) -> str|None:
    re_match: re.Match|None


    # wind VRB
    re_match=re.search("^VRB(?P<wind_speed>[0-9]{2})(G(?P<wind_speed_gust>[0-9]{2}))?(?P<wind_unit>MPS|KT)$", info)
    if re_match!=None:
        info_new: str
        wind_speed: float=float(re_match.groupdict()["wind_speed"])
        wind_speed_gust: float  # wind speed gust, if no given equal to normal wind speed
        wind_unit: str=re_match.groupdict()["wind_unit"]

        
        if re_match.groupdict()["wind_speed_gust"]==None:   # if no gust given:
            wind_speed_gust=wind_speed                      # equal to normal wind speed
        else:
            wind_speed_gust=float(re_match.groupdict()["wind_speed_gust"])

        if wind_unit=="KT": # if kt: convert
            wind_speed     *=KFSconvert_to_SI.SPEED["kt"]
            wind_speed_gust*=KFSconvert_to_SI.SPEED["kt"]


        info_new=f"VRB{KFSfstr.notation_abs(wind_speed, 0, round_static=True, width=2)}"
        if wind_speed!=wind_speed_gust:
            info_new+=f"G{KFSfstr.notation_abs(wind_speed_gust, 0, round_static=True, width=2)}"
        info_new+="m/s"
        
        if WEATHER_MIN["TWC"]<wind_speed_gust:  # if TWC max. exceeded: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"
    

    # wind normal
    re_match=re.search("^(?P<wind_direction>[0-3][0-9]{2})(?P<wind_speed>[0-9]{2})(G(?P<wind_speed_gust>[0-9]{2}))?(?P<wind_unit>MPS|KT)$", info)
    if re_match!=None:
        bold: bool
        CWC: list=[]                                                            # across all runways, crosswind component
        info_new: str
        RWY: pandas.DataFrame=RWY_DB[RWY_DB["airport_ident"]==station.ICAO]     # in aerodrome all runways
        wind_direction: int=int(re_match.groupdict()["wind_direction"])%360     # keep in [0; 360[
        wind_speed: float=float(re_match.groupdict()["wind_speed"])
        wind_speed_gust: float                                                  # wind speed gust, if no given equal to normal wind speed
        wind_unit: str=re_match.groupdict()["wind_unit"]


        if re_match.groupdict()["wind_speed_gust"]==None:   # if no gust given:
            wind_speed_gust=wind_speed                      # equal to normal wind speed
        else:
            wind_speed_gust=float(re_match.groupdict()["wind_speed_gust"])

        if wind_unit=="KT": # if kt: convert
            wind_speed     *=KFSconvert_to_SI.SPEED["kt"]
            wind_speed_gust*=KFSconvert_to_SI.SPEED["kt"]


        info_new=f"{KFSfstr.notation_abs(wind_direction, 0, round_static=True, width=3)}°{KFSfstr.notation_abs(wind_speed, 0, round_static=True, width=2)}"
        if wind_speed!=wind_speed_gust:
            info_new+=f"G{KFSfstr.notation_abs(wind_speed_gust, 0, round_static=True, width=2)}"
        info_new+="m/s"

        if RWY.empty==True:                                                                                             # if no runways found: assume direct crosswind
            CWC.append(wind_speed)
        else:                                                                                                           # if runways found: for each runway calculate crosswind components
            CWC+=abs(numpy.sin(numpy.radians(wind_direction-RWY["le_heading_degT"]))*wind_speed_gust).dropna().tolist() # sin(direction difference)*wind speed, abs, remove NaN, convert to list # type:ignore
        for i in range(len(CWC)):
            if CWC[i]<=WEATHER_MIN["CWC"]:                                                                              # if at least 1 CWC below maximum:
                bold=False                                                                                              # landable
                break
        else:                                                                                                           # if all CWC above maximum:
            bold=True

        if WEATHER_MIN["wind"]<wind_speed_gust: # if despite landable crosswind component overall wind just too strong:
            bold=True
    
        if bold==True:
            info_new=f"**{info_new}**"
        return f" {info_new}"


    # wind too strong
    re_match=re.search("^ABV(49MPS|99KT)$", info)
    if re_match!=None:
        info_new: str="50m/s+"


        if WEATHER_MIN["TWC"]<50:   # if TWC max. definitely exceeded: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"


    # wind direction variable
    re_match=re.search("^(?P<wind_direction_1>[0-3][0-9]{2})V(?P<wind_direction_2>[0-3][0-9]{2})$", info)
    if re_match!=None:
        wind_direction_1: int=int(re_match.groupdict()["wind_direction_1"])%360 # keep in [0; 360[
        wind_direction_2: int=int(re_match.groupdict()["wind_direction_2"])%360 # keep in [0; 360[
        
        
        return f" {KFSfstr.notation_abs(wind_direction_1, 0, round_static=True, width=3)}°V{KFSfstr.notation_abs(wind_direction_2, 0, round_static=True, width=3)}°"