import KFS
import re
from weather_minimums import WEATHER_MIN


def change_format_vis(info_list: list, i: int) -> str|None:
    re_match: re.Match|None
    re_match_1: re.Match|None
    re_match_2: re.Match|None

    PLUS_MINUS={
        "P": "+",
        "M": "-",
        "": "",
        None: ""
    }


    #visibility 10km+
    re_match=re.search("^9999$", info_list[i])
    if re_match!=None:
        return f" 10km+"


    #visibility normal
    re_match=re.search("^(?P<plus_minus>[PM]?)(?P<visibility>[0-9]{4})(?P<direction>(N|NE|E|SE|S|SW|W|NW)?)$", info_list[i])
    if re_match!=None:
        direction: str=re_match.groupdict()["direction"]
        info_new: str
        plus_minus: str=PLUS_MINUS[re_match.groupdict()["plus_minus"]]
        visibility: float=int(re_match.groupdict()["visibility"])

        
        if visibility<5e3: #if visbility<5km: round to 2 significant digits
            info_new=f"{KFS.fstr.notation_tech(visibility, 2)}m"
        else:       #if 5km<=visibility: round to whole km
            info_new=f"{KFS.fstr.notation_tech(visibility, -3, round_static=True)}m"
        
        info_new+=plus_minus    #append plus or minus

        if direction!="":   #if direction given: append
            info_new+=f"/{direction}"
        
        if "vis" in WEATHER_MIN and visibility<WEATHER_MIN["vis"]:  #if visibility below minimums: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"


    #military base format
    re_match=re.search("^(?P<visibility>[0-9]{1,2})KM$", info_list[i])
    if re_match!=None:
        info_new: str
        visibility: float=int(re_match.groupdict()["visibility"])*1000


        info_new=f"{KFS.fstr.notation_tech(visibility, -3, round_static=True)}m"
        
        if "vis" in WEATHER_MIN and visibility<WEATHER_MIN["vis"]:  #if visibility below minimums: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"


    #USA: visibility [SM]
    re_match=re.search("^(?P<plus_minus>[PM]?)(?P<visibility>[0-9]{1,2})SM$", info_list[i])
    if re_match!=None:
        info_new: str
        plus_minus: str=PLUS_MINUS[re_match.groupdict()["plus_minus"]]
        visibility: float=int(re_match.groupdict()["visibility"])*KFS.convert_to_SI.length["SM"]
        

        info_new=f"{KFS.fstr.notation_tech(visibility, 2)}m{plus_minus}"
        
        if "USA_vis" in WEATHER_MIN and visibility<WEATHER_MIN["USA_vis"]:  #if visibility below USA minimums: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"
    

    #USA visibility a+b/c [SM]
    re_match_1=re.search("^(?P<vis_A>[0-9])$", info_list[i])    #single digit a as part of compound fraction a+b/c
    try:
       re_match_2=re.search("^(?P<vis_B>[0-9])/(?P<vis_C>[0-9])SM$", info_list[i+1])    #is element next rest of fraction b/c?
    except IndexError:          #if exception because element next does not exist: default none
        re_match_2=None
    if re_match_1!=None and re_match_2!=None:
        vis_A: int=int(re_match_1.groupdict()["vis_A"])
        vis_B: int=int(re_match_2.groupdict()["vis_B"])
        vis_C: int=int(re_match_2.groupdict()["vis_C"])


        info_list[i+1]=f"{vis_A*vis_C+vis_B}/{vis_C}SM" #convert to single fraction a+b/c=(a*c+b)/c
        info_list.pop(i)                                #remove single digit a
        #do not return and convert single fraction (a*c+b)/c in next if statement


    #USA visibility b/c [SM]
    re_match=re.search("^(?P<plus_minus>[PM]?)(?P<vis_B>[0-9]{1,2})/(?P<vis_C>[0-9]{1,2})SM$", info_list[i])
    if re_match!=None:
        info_new: str
        plus_minus: str=PLUS_MINUS[re_match.groupdict()["plus_minus"]]
        visibility: float=int(re_match.groupdict()["vis_B"])/int(re_match.groupdict()["vis_C"])*KFS.convert_to_SI.length["SM"]


        info_new=f"{KFS.fstr.notation_tech(visibility, 2)}m{plus_minus}"
        
        if "USA_vis" in WEATHER_MIN and visibility<WEATHER_MIN["USA_vis"]:  #if visibility below USA minimums: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"