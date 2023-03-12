import re
import KFS


def change_format_HGT(info: str, station: dict) -> str|None:
    re_match: re.Match|None

    
    #RMK height
    re_match=re.search("^(?P<HGT>[0-9]{1,4})FT$", info)
    if re_match!=None:
        HGT=int(re_match.groupdict()["HGT"])*KFS.convert_to_SI.length["ft"] #height [m]; tbh don't really know if it's a height, that's why no elevation used to calculate altitude
        return f" {KFS.fstr.notation_abs(HGT, 2)}m"