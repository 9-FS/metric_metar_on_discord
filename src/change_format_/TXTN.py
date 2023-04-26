#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import datetime as dt
import re
from weather_minimums import WEATHER_MIN


def change_format_TXTN(info: str, met_report_DT: dt.datetime) -> str|None:
    re_match: re.Match|None


    #TX TN
    re_match=re.search("^(?P<temperature_type>T[XN])(?P<temperature>[M]?[0-9]{2})/(?P<day>[0-3][0-9])(?P<hour>[0-2][0-9])Z$", info)
    if re_match!=None:
        event_DT: dt.datetime
        info_new: str
        temperature: str=re_match.groupdict()["temperature"].replace("M", "-") #replace M with proper minus
        temperature_type: str=f"{re_match.groupdict()['temperature_type']}"

        event_DT=dt.datetime(met_report_DT.year, met_report_DT.month, met_report_DT.day, 0, 0, 0, 0, dt.timezone.utc)   #event date, initialised with met report datetime
        while event_DT.day!=int(re_match.groupdict()["day"]):                                                           #as long as days not matching:
            event_DT+=dt.timedelta(days=1)                                                                              #event must be after met report datetime, increment day until same
        event_DT+=dt.timedelta(hours=int(re_match.groupdict()["hour"]))                                                 #correct day now, add time


        info_new=temperature_type

        if   met_report_DT.strftime("%Y-%m")==event_DT.strftime("%Y-%m"):   #if year and month still same:
            info_new+=f"{event_DT.strftime('%dT%H')}"                       #day, hour
        elif met_report_DT.strftime("%Y")==event_DT.strftime("%Y"):         #if year still same:
            info_new+=f"{event_DT.strftime('%m-%dT%H')}"                    #month, day, hour
        else:                                                               #nothing same:
            info_new+=f"{event_DT.strftime('%Y-%m-%dT%H')}"                 #full datetime

        info_new+=f"/{temperature}°C"

        if ("temp_min" in WEATHER_MIN and int(temperature)<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<int(temperature)):    #if temperature outside limits: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"