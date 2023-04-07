#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import re
import KFS.fstr, KFS.convert_to_SI
from Station import Station


def change_format_HGT(info: str, station: Station) -> str|None:
    re_match: re.Match|None

    
    #RMK height
    re_match=re.search("^(?P<HGT>[0-9]{1,4})FT$", info)
    if re_match!=None:
        HGT=int(re_match.groupdict()["HGT"])*KFS.convert_to_SI.length["ft"] #height [m]; tbh don't really know if it's a height, that's why no elevation used to calculate altitude
        return f" {KFS.fstr.notation_abs(HGT, 2)}m"