#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import datetime as dt
import KFS.fstr
import re


def change_format_change(info_list: list[str], i: int, met_report_DT: dt.datetime) -> str|None:
    re_match: re.Match|None

    
    #change
    re_match=re.search("^(NOSIG|BECMG|TEMPO)$", info_list[i])
    if re_match!=None:
        info_new: str


        if i==0:                                                    #if info[0]:
            info_new=f"{info_list[i]}"                              #just forward
        elif re.search("^PROB[0-9]{2}$", info_list[i-1])!=None:     #if not info[0] and info previous PROBxx: 
            info_new=f" {info_list[i]}"                             #space then forward
        else:                                                       #else:
            info_new=f"\n{info_list[i]}"                            #change info new, linebreak then forward
        return info_new


    #probability
    re_match=re.search("^PROB(?P<probability>[0-9]{2})$", info_list[i])
    if re_match!=None:
        info_new=f"PROB{KFS.fstr.notation_abs(float(re_match.groupdict()['probability'])/100, 2, round_static=True, trailing_zeros=False)}" #change info new, linebreak then forward
        
        if i==0:                                                #if info[0]:
            info_new=f"{info_new}"                              #just forward
        elif re.search("^PROB[0-9]{2}$", info_list[i-1])!=None: #if not info[0] and info previous PROBxx: 
            info_new=f" {info_new}"                             #space then forward
        else:                                                   #else:
            info_new=f"\n{info_new}"                            #change info new, linebreak then forward
        return info_new


    #from, until, at
    re_match=re.search("^(?P<change_type>FM|TL|AT)(?P<day>([0-3][0-9])?)(?P<hour>[0-2][0-9])(?P<minute>[0-5][0-9])$", info_list[i])
    if re_match!=None:
        event_DT: dt.datetime
        info_new: str

        event_DT=dt.datetime(met_report_DT.year, met_report_DT.month, met_report_DT.day, 0, 0, 0, 0, dt.timezone.utc)                   #event date, initialised with met report datetime
        if re_match.groupdict()["day"]!="":                                                                                             #if event day given:
            while event_DT.strftime("%d")!=re_match.groupdict()["day"]:                                                                 #as long as days not matching:
                event_DT+=dt.timedelta(days=1)                                                                                          #event must be after met report datetime, increment day until same
        if event_DT.strftime("%Y-%m-%d")==met_report_DT.strftime("%Y-%m-%d") and event_DT.strftime("%H")<re_match.groupdict()["hour"]:  #if date same and event hour < met report hour:
            event_DT+=dt.timedelta(days=1)                                                                                              #event must be after met report datetime, must be day next
        event_DT+=dt.timedelta(hours=int(re_match.groupdict()["hour"]), minutes=int(re_match.groupdict()["minute"]))                    #correct day now, add time


        info_new=f"{re_match.groupdict()['change_type']}"                   #change type

        if   met_report_DT.strftime("%Y-%m")==event_DT.strftime("%Y-%m"):   #if year and month still same:
            info_new+=f"{event_DT.strftime('%dT%H:%M')}"                    #day, hour, minute
        elif met_report_DT.strftime("%Y")==event_DT.strftime("%Y"):         #if year still same:
            info_new+=f"{event_DT.strftime('%m-%dT%H:%M')}"                 #month, day, hour, minute
        else:                                                               #nothing same:
            info_new+=f"{event_DT.strftime('%Y-%m-%dT%H:%M')}"              #full datetime

        if i==0:                                                #if info[0]:
            info_new=f"{info_new}"                              #just forward
        elif re.search("^PROB[0-9]{2}$", info_list[i-1])!=None: #if not info[0] and info previous PROBxx: 
            info_new=f" {info_new}"                             #space then forward
        else:                                                   #else:
            info_new=f"\n{info_new}"                            #change info new, linebreak then forward
        return info_new