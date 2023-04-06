#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import datetime as dt
import pandas
from change_format_.change               import change_format_change
from change_format_.clouds               import change_format_clouds
from change_format_.QNH                  import change_format_QNH
from change_format_.runway_state_message import change_format_RSM
from change_format_.RVR                  import change_format_RVR
from change_format_.temp_dew             import change_format_temp_dew
from change_format_.met_report_time      import change_format_met_report_DT
from change_format_.TXTN                 import change_format_TXTN
from change_format_.USA_codes            import change_format_USA_codes
from change_format_.validity             import change_format_validity
from change_format_.visibility           import change_format_vis
from change_format_.visibility_vertical  import change_format_VV
from change_format_.weather              import change_format_weather
from change_format_.wind                 import change_format_wind


def change_format(info_list: list[str], i: int, station: dict, met_report_DT: dt.datetime, now_DT: dt.datetime, RWY_DB: pandas.DataFrame, force_print: bool) -> str:
    #just forward station ICAO

    info_new=change_format_met_report_DT(info_list[i], met_report_DT, now_DT, force_print)  #met report time
    if info_new!=None:
        return info_new

    info_new=change_format_wind         (info_list[i], station, RWY_DB)                     #wind
    if info_new!=None:
        return info_new

    info_new=change_format_vis          (info_list, i)                                      #visibility
    if info_new!=None:
        return info_new

    info_new=change_format_RVR          (info_list[i])                                      #RVR
    if info_new!=None:
        return info_new

    info_new=change_format_weather      (info_list, i)                                      #weather, only mark weather dangerous
    if info_new!=None:
        return info_new

    info_new=change_format_clouds       (info_list[i], station)                             #clouds
    if info_new!=None:
        return info_new

    info_new=change_format_VV           (info_list[i])                                      #visibility vertical
    if info_new!=None:
        return info_new

    info_new=change_format_temp_dew     (info_list[i])                                      #temperature and dewpoint
    if info_new!=None:
        return info_new

    info_new=change_format_QNH          (info_list[i])                                      #QNH, altimeter setting
    if info_new!=None:
        return info_new

    info_new=change_format_RSM          (info_list[i])                                      #runway state message
    if info_new!=None:
        return info_new

    info_new=change_format_change       (info_list, i, met_report_DT)                       #trend and TAF: changes in weather
    if info_new!=None:
        return info_new

    info_new=change_format_validity     (info_list[i], met_report_DT)                       #TAF: validity timespan
    if info_new!=None:
        return info_new

    info_new=change_format_TXTN         (info_list[i], met_report_DT)                       #TAF: daily temperature max and min
    if info_new!=None:
        return info_new

    info_new=change_format_USA_codes    (info_list[i], met_report_DT, station, RWY_DB)      #USA weather station machine codes
    if info_new!=None:
        return info_new

    return f" {info_list[i]}"   #if format not found: just forward it