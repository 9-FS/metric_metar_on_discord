#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import datetime as dt
from KFSfstr import KFSfstr
import re
from Server import Server


def change_format_met_report_DT(info: str, met_report_DT: dt.datetime, now_DT: dt.datetime, server: Server) -> str|None:
    re_match: re.Match|None
    
    
    #met report time
    re_match=re.search("^(?P<day>[0-3][0-9])(?P<hour>[0-2][0-9])(?P<minute>[0-5][0-9])Z$", info)
    if re_match!=None:
        event_DT: dt.datetime   #datetime of THIS info; should be same as met_report_DT because group should only exist once, but you never know. That's why not just using already parsed met_report_DT
        info_new: str
        timespan_published: dt.timedelta

        event_DT=dt.datetime(met_report_DT.year, met_report_DT.month, met_report_DT.day, 0, 0, 0, 0, dt.timezone.utc)   #event date, initialised with met report datetime
        while event_DT.day!=int(re_match.groupdict()["day"]):                                                           #as long as days not matching:
            event_DT+=dt.timedelta(days=1)                                                                              #event must be after met report datetime, increment day until same
        event_DT+=dt.timedelta(hours=int(re_match.groupdict()["hour"]), minutes=int(re_match.groupdict()["minute"]))    #correct day now, add time


        info_new=f"{event_DT.strftime('%Y-%m-%dT%H:%M')}"

        if server.force_print==True:            #if force print because no subscription:
            timespan_published=now_DT-event_DT  #append timespan published
            info_new+=f" ({KFSfstr.notation_tech(timespan_published.total_seconds(), 2)}s ago)"

        return f" {info_new}"