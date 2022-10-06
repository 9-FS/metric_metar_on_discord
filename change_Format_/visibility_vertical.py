import re   #Regular Expressions
from KFS import KFSmath


def change_format_VV(info):
    #VV
    if re.search("^VV[0-9][0-9][0-9]$", info)!=None:
        info_new=f"VV{KFSmath.round_sig(int(info[2:5])*100*0.3048, 2):,.0f}m".replace(",", ".")
        if int(info[2:5])*100*0.3048<5000:  #Sicht min. 5km
            info_new=f"**{info_new}**"
        return " "+info_new


    #Russland: QBB, Sicht vertikal metrisch
    if re.search("^QBB[0-9][0-9][0-9]$", info)!=None:
        info_new=f"QBB{int(info[3:6]):,.0f}m".replace(",", ".")
        if int(info[3:6])<5e3:  #Sicht min. 5km
            info_new=f"**{info_new}**"
        return " "+info_new