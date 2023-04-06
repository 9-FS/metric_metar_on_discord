import KFS
import re
from weather_minimums import WEATHER_MIN


def change_format_clouds(info: str, station: dict) -> str|None:
    re_match: re.Match|None


    #clouds
    re_match=re.search("^(?P<cloud_coverage>FEW|SCT|BKN|OVC)(?P<cloud_HGT>[0-9]{3})(?P<cloud_type>([A-Z/])*?)?$", info)
    if re_match!=None:
        cloud_ALT: float                                                                            #altitude [m]
        cloud_coverage: str=re_match.groupdict()["cloud_coverage"]                                  #cloud coverage [1/8]
        cloud_HGT: float=int(re_match.groupdict()["cloud_HGT"])*100*KFS.convert_to_SI.length["ft"]  #height [m]
        cloud_type: str=re_match.groupdict()["cloud_type"]                                          #append cloud type, usually TCU or CB
        info_new: str

        if station["elev"]==None:               #if aerodrome elevation unknown:
            cloud_ALT=cloud_HGT                 #assume elevation=0m
        else:                                   #if aerodrome elevation known:
            cloud_ALT=cloud_HGT+station["elev"] #calculate altitude normally


        info_new=cloud_coverage
        if cloud_HGT==0:                                                                                                        #if HGT==0m:
            info_new+=f"{KFS.fstr.notation_abs(cloud_ALT, 0, round_static=True)}m"                                              #cloud touches ground, ALT==elevation, round altitude and height to 1m
            if KFS.fstr.notation_abs(cloud_ALT, 0, round_static=True)!=KFS.fstr.notation_abs(cloud_HGT, 0, round_static=True):  #if height!=altitude:
                info_new+=f"|{KFS.fstr.notation_abs(cloud_HGT, 0, round_static=True)}m"                                         #append height
        else:                                                                               #if HGT!=0:
            info_new+=f"{KFS.fstr.notation_abs(cloud_ALT, 2)}m"                             #round altitude to 2 signifcant digits
            if KFS.fstr.notation_abs(cloud_ALT, 2)!=KFS.fstr.notation_abs(cloud_HGT, 2):    #if height!=altitude:
                info_new+=f"|{KFS.fstr.notation_abs(cloud_HGT, 2)}m"                        #append height

        if cloud_type!="":  #if cloud type given: append
            info_new+=f"|{cloud_type}"
        
        if cloud_type=="CB":    #if CB: mark
            info_new=f"**{info_new}**"
        elif "ceiling" in WEATHER_MIN and cloud_HGT<WEATHER_MIN["ceiling"] and re.search("^(BKN|OVC)$", cloud_coverage)!=None:  #if ceiling below minimum: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"