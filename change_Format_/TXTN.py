import datetime
import re   #Regular Expressions
from weather_minimums import WEATHER_MIN


def change_format_TXTN(info, date):
    if re.search("^T[XN][0-9][0-9]/[0-3][0-9][0-2][0-9]Z$", info)!=None:
        DT=datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), 0, 0) #Eventdatum, initialisiert mit Veröffentlichungsdatum
        while DT.strftime("%d")!=info[5:7]:                                         #solange Eventtag nicht stimmt:
            DT+=datetime.timedelta(days=1)                                          #Tag hinzufügen
        DT+=datetime.timedelta(hours=int(info[7:9]))                                #zu Evenntdatum Uhrzeit hinzufügen

        info_new=f"T{info[1]}{DT.strftime('%dT%H')}/{info[2:4]}°C"

        if ("temp_min" in WEATHER_MIN and int(info[2:4])<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<int(info[2:4])):    #wenn Temperatur außerhalb Grenzen, wegen Leistungstabellen und Vereisung
            info_new=f"**{info_new}**"

        return " "+info_new

    if re.search("^T[XN]M[0-9][0-9]/[0-3][0-9][0-2][0-9]Z$", info)!=None:
        DT=datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), 0, 0) #Eventdatum, initialisiert mit Veröffentlichungsdatum
        while DT.strftime("%d")!=info[6:8]:                                         #solange Starttag nicht stimmt:
            DT+=datetime.timedelta(days=1)                                          #Tag hinzufügen
        DT+=datetime.timedelta(hours=int(info[8:10]))                               #zu Evenntdatum Uhrzeit hinzufügen

        info_new=f"T{info[1]}{DT.strftime('%dT%H')}/{info[3:5]}°C"

        if ("temp_min" in WEATHER_MIN and int(info[3:5])<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<int(info[3:5])):    #wenn Temperatur außerhalb Grenzen, wegen Leistungstabellen und Vereisung
            info_new=f"**{info_new}**"
        
        return " "+info_new