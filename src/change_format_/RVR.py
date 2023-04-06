#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import re   #Regular Expressions
import KFS.convert_to_SI, KFS.fstr
from weather_minimums import WEATHER_MIN


def change_format_RVR(info: str) -> str|None:
    re_match: re.Match|None
    
    PLUS_MINUS={
        "P": "+",
        "M": "-",
        "": "",
        None: ""
    }

    TREND={
        "U": "↗",
        "N": "→",
        "D": "↘",
        "": "",
        None: ""
    }


    #RVR [m]
    re_match=re.search("^R(?P<runway>[0-3][0-9]([LCR])?)/(?P<plus_minus>[PM]?)(?P<RVR_1>[0-9]{4})(V(?P<RVR_2>[0-9]{4}))?(?P<trend>[UND]?)$", info)
    if re_match!=None:
        info_new: str
        plus_minus: str=PLUS_MINUS[re_match.groupdict()["plus_minus"]]
        runway: str
        RVR_1: float=float(re_match.groupdict()["RVR_1"])
        RVR_2: float    #RVR 2, if no given equal to RVR 1
        trend: str=TREND[re_match.groupdict()["trend"]] #type:ignore

        runway=re_match.groupdict()["runway"]
        if runway=="88":    #if runway 88: all runways
            runway=":ALL"
        if re_match.groupdict()["RVR_2"]==None:
            RVR_2=RVR_1
        else:
            RVR_2=float(re_match.groupdict()["RVR_2"])


        info_new=f"R{runway}/{KFS.fstr.notation_tech(RVR_1, 2)}m{plus_minus}"
        if RVR_1!=RVR_2:
            info_new+=f"V{KFS.fstr.notation_tech(float(RVR_2), 2)}m"
        info_new+=trend

        if "RVR" in WEATHER_MIN and (RVR_1<WEATHER_MIN["RVR"] or RVR_2<WEATHER_MIN["RVR"]): #if a RVR below RVR min.: mark
            info_new=f"**{info_new}**" 
        return f" {info_new}"


    #USA: RVR [ft]
    re_match=re.search("^R(?P<runway>[0-3][0-9]([LCR])?)/(?P<plus_minus>[PM]?)(?P<RVR_1>[0-9]{4})(V(?P<RVR_2>[0-9]{4}))?FT(/(?P<trend>[UND]))?$", info)
    if re_match!=None:
        info_new: str
        plus_minus: str=PLUS_MINUS[re_match.groupdict()["plus_minus"]]
        runway: str
        RVR_1: float=float(re_match.groupdict()["RVR_1"])*KFS.convert_to_SI.length["ft"]
        RVR_2: float    #RVR 2, if no given equal to RVR 1
        trend: str|None

        runway=re_match.groupdict()["runway"]
        if runway=="88":    #if runway 88: all runways
            runway=":ALL"
        if re_match.groupdict()["RVR_2"]==None:
            RVR_2=RVR_1
        else:
            RVR_2=float(re_match.groupdict()["RVR_2"])*KFS.convert_to_SI.length["ft"]

        trend=re_match.groupdict()["trend"]
        if trend==None:
            trend=""
        else:
            trend=TREND[trend]


        info_new=f"R{runway}/{KFS.fstr.notation_tech(RVR_1, 2)}m{plus_minus}"
        if RVR_1!=RVR_2:
            info_new+=f"V{KFS.fstr.notation_tech(float(RVR_2), 2)}m"
        info_new+=trend

        if "RVR" in WEATHER_MIN and (RVR_1<WEATHER_MIN["RVR"] or RVR_2<WEATHER_MIN["RVR"]): #if a RVR below RVR min.: mark
            info_new=f"**{info_new}**" 
        return f" {info_new}"