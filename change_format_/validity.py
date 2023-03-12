import datetime as dt
import re


def change_format_validity(info: str, met_report_DT: dt.datetime) -> str|None:
    re_match: re.Match|None


    #TAF validity
    re_match=re.search("^(?P<start_day>[0-3][0-9])(?P<start_hour>[0-2][0-9])/(?P<end_day>[0-3][0-9])(?P<end_hour>[0-2][0-9])$", info)
    if re_match!=None:
        start_DT: dt.datetime
        end_DT: dt.datetime
        info_new: str

        start_DT=dt.datetime(met_report_DT.year, met_report_DT.month, met_report_DT.day, 0, 0, 0, 0, dt.timezone.utc)   #start datetime, initialised with met report date
        while start_DT.strftime("%d")!=re_match.groupdict()["start_day"]:                                               #as long as days not matching:
            start_DT+=dt.timedelta(days=1)                                                                              #start must be after met report datetime, increment day until same
        start_DT+=dt.timedelta(hours=int(re_match.groupdict()["start_hour"]))                                           #correct day now, add time

        end_DT=dt.datetime(start_DT.year, start_DT.month, start_DT.day, 0, 0, 0, 0, dt.timezone.utc)    #end datetime, initialised with start date
        while end_DT.strftime("%d")!=re_match.groupdict()["end_day"]:                                   #as long as days not matching:
            end_DT+=dt.timedelta(days=1)                                                                #end must be after start datetime, increment day until same
        end_DT+=dt.timedelta(hours=int(re_match.groupdict()["end_hour"]))                               #correct day now, add time


        if   met_report_DT.strftime("%Y-%m")==start_DT.strftime("%Y-%m"):   #if year and month still same:
            info_new=f"{start_DT.strftime('%dT%H')}/"                       #day, hour
        elif met_report_DT.strftime("%Y")==start_DT.strftime("%Y"):         #if year still same:
            info_new=f"{start_DT.strftime('%m-%dT%H')}/"                    #month, day, hour
        else:                                                               #nothing same:
            info_new=f"{start_DT.strftime('%Y-%m-%dT%H')}/"                 #full datetime

        if   start_DT.strftime("%Y-%m-%d")==end_DT.strftime("%Y-%m-%d"):    #if date still same:
            info_new+=f"{end_DT.strftime('%H')}"                            #hour
        elif start_DT.strftime("%Y-%m")==end_DT.strftime("%Y-%m"):          #if year and month still same:
            info_new+=f"{end_DT.strftime('%dT%H')}"                         #day, hour
        elif start_DT.strftime("%Y")==end_DT.strftime("%Y"):                #if year still same:
            info_new+=f"{end_DT.strftime('%m-%dT%H')}"                      #month, day, hour
        else:                                                               #nothing same
            info_new+=f"{end_DT.strftime('%Y-%m-%dT%H')}"                   #full datetime

        return f" {info_new}"