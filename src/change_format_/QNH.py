import inspect
import KFS
import logging
import re
from weather_minimums import WEATHER_MIN


def change_format_QNH(info: str) -> str|None:
    re_match: re.Match|None


    #QNH [100Pa]
    re_match=re.search("^Q(?P<QNH>[0-9]{4})$", info)
    if re_match!=None:
        info_new: str
        QNH=float(re_match.groupdict()['QNH'])*100
        
        
        info_new=f"Q{KFS.fstr.notation_abs(QNH*1e-3, 1, round_static=True, width=5)}kPa"

        if ("QNH_min" in WEATHER_MIN and QNH<WEATHER_MIN["QNH_min"]) or ("QNH_max" in WEATHER_MIN and WEATHER_MIN["QNH_max"]<QNH):  #QNH unusual, because of possible altimeter settings and possible storms at low pressure
            info_new=f"**{info_new}**"
        return f" {info_new}"
    

    #USA: altimeter setting [inHg]
    re_match=re.search("^A(?P<QNH>[0-9]{4})$", info)
    if re_match!=None:
        info_new: str
        QNH=float(re_match.groupdict()['QNH'])/100*KFS.convert_to_SI.pressure["inHg"]
        
        
        info_new=f"A{KFS.fstr.notation_abs(QNH*1e-3, 1, round_static=True, width=5)}kPa"

        if ("QNH_min" in WEATHER_MIN and QNH<WEATHER_MIN["QNH_min"]) or ("QNH_max" in WEATHER_MIN and WEATHER_MIN["QNH_max"]<QNH):  #QNH unusual, because of possible altimeter settings and possible storms at low pressure
            info_new=f"**{info_new}**"
        return f" {info_new}"


    #weird military base version [inHg]
    re_match=re.search("^QNH(?P<QNH>[0-9]{4})INS$", info)
    if re_match!=None:
        info_new: str
        QNH=float(re_match.groupdict()['QNH'])/100*KFS.convert_to_SI.pressure["inHg"]
       
       
        info_new=f"A{KFS.fstr.notation_abs(QNH*1e-3, 1, round_static=True, width=5)}kPa"

        if ("QNH_min" in WEATHER_MIN and QNH<WEATHER_MIN["QNH_min"]) or ("QNH_max" in WEATHER_MIN and WEATHER_MIN["QNH_max"]<QNH):  #QNH unusual, because of possible altimeter settings and possible storms at low pressure
            info_new=f"**{info_new}**"
        return f" {info_new}"


    #russia: QFE [mmHg]
    re_match=re.search("^QFE(?P<QFE>[0-9]{3}([.][0-9])?)$", info)
    if re_match!=None:
        info_new: str
        QFE=float(re_match.groupdict()['QFE'])*KFS.convert_to_SI.pressure["mmHg"]
        

        info_new=f"QFE{KFS.fstr.notation_abs(QFE*1e-3, 1, round_static=True, width=5)}kPa"

        return f" {info_new}"
    

    #russia: QFE [mmHg] and [100Pa]
    re_match=re.search("^QFE[0-9]{3}/(?P<QFE>[0-9]{4})$", info)
    if re_match!=None:
        info_new: str
        QFE=float(re_match.groupdict()['QFE'])*100
        

        info_new=f"QFE{KFS.fstr.notation_abs(QFE*1e-3, 1, round_static=True, width=5)}kPa"

        return f" {info_new}"


    #USA: SLP [???]
    re_match=re.search("^SLP(?P<SLP>[0-9]{3})$", info)
    if re_match!=None:
        info_new: str
        SLP: float    #SLP [Pa]

        SLP=float(re_match.groupdict()['SLP'])*10
        if 0<=SLP and SLP<5e3:  #if 0kPa<=info<5kPa: +100kPa
            SLP+=100e3
        elif SLP and SLP<10e3:  #if 5kPa<=info<10kPa: +90kPa  
            SLP+=90e3
        else:
            logging.critical(f"SLP info *10 shoud be in [0; 10e3[, but it is {SLP}.")
            raise RuntimeError(f"Error in {change_format_QNH.__name__}{inspect.signature(change_format_QNH)}: SLP info *10 shoud be in [0; 10e3[, but it is {SLP}.")
        

        info_new=f"SLP{KFS.fstr.notation_abs(SLP*1e-3, 2, round_static=True, width=6)}kPa"
        
        return f" {info_new}"