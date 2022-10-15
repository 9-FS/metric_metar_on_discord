import re   #Regular Expressions
import KFS.math
from weather_minimums import WEATHER_MIN


def change_format_VV(info):
    #VV
    if re.search("^VV[0-9][0-9][0-9]$", info)!=None:
        info_new=f"VV{KFS.math.round_sig(int(info[2:5])*100*0.3048, 2):,.0f}m".replace(",", ".")
        if "vis" in WEATHER_MIN and int(info[2:5])*100*0.3048<WEATHER_MIN["vis"]:   #Sicht min.
            info_new=f"**{info_new}**"
        return " "+info_new


    #Russland: QBB, Sicht vertikal metrisch
    if re.search("^QBB[0-9][0-9][0-9]$", info)!=None:
        info_new=f"QBB{int(info[3:6]):,.0f}m".replace(",", ".")
        if "vis" in WEATHER_MIN and int(info[3:6])<WEATHER_MIN["vis"]:   #Sicht min.
            info_new=f"**{info_new}**"
        return " "+info_new