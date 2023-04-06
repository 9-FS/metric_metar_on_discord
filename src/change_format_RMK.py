#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import datetime as dt
import pandas
from change_format_.HGT                  import change_format_HGT
from change_format_.QNH                  import change_format_QNH
from change_format_.temp_dew             import change_format_temp_dew
from change_format_.USA_codes            import change_format_USA_codes
from change_format_.visibility_vertical  import change_format_VV
from change_format_.wind                 import change_format_wind


def change_format_RMK(info_list: list[str], i: int, station: dict, met_report_DT: dt.datetime, RWY_DB: pandas.DataFrame) -> str:
    info_new=change_format_wind     (info_list[i], station, RWY_DB)         #wind
    if info_new!=None:
        return info_new

    info_new=change_format_temp_dew (info_list[i])                          #temperature and dewpoint
    if info_new!=None:
        return info_new

    info_new=change_format_QNH      (info_list[i])                          #QNH in additional unit (ex. RCTP)
    if info_new!=None:
        return info_new

    info_new=change_format_HGT      (info_list[i], station)                 #height, example wind change altitude
    if info_new!=None:
        return info_new

    #in RMK 4 digits can mean different things: time, QNH... that's why forward unchanged

    info_new=change_format_VV       (info_list[i])                          #visibility vertical
    if info_new!=None:
        return info_new

    info_new=change_format_USA_codes(info_list[i], met_report_DT, station, RWY_DB)   #USA weather station machine codes
    if info_new!=None:
        return info_new

    return f" {info_list[i]}"   #if format not found: just forward it