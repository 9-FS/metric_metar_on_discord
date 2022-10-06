import re   #Regular Expressions
from weather_minimums import WEATHER_MIN


def change_format_weather(info_list, i):
    if re.search("^([+-]|)([A-Z][A-Z]|)([A-Z][A-Z]|)[A-Z][A-Z]$", info_list[i])!=None:
        bold=False
        info_new=""

        if i==2:                    #wenn Gruppe 2: nicht Wetter, sondern Stationsname
            return " "+info_list[i] #einfach durchleiten, nichts markieren (Bsp Flugplatz EDGS Siegerland würde ständig markiert werden wegen GS)

        j=0
        while j<len(info_list[i]):
            if j==0 and re.search("^[+-]$", info_list[i])!=None:    #wenn Intensitätsvorzeichen: überspringen
                j+=1
                continue
            if "weather_forbidden" in WEATHER_MIN and re.search(WEATHER_MIN["weather_forbidden"], info_list[i][j:j+2])!=None:   #bei dem Wetter nich fliegen, Sicht, Vereisung, Stürme etc
                bold=True
                break
            j+=2

        info_new=info_list[i]
        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new