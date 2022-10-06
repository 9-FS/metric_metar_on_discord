import re
import tempfile   #Regular Expressions
from weather_minimums import WEATHER_MIN


def change_format_temp_dew(info):
    #Temperatur und Taupunkt
    if re.search("^(M|)[0-9][0-9]/(((M|)[0-9][0-9])|)$", info)!=None:
        bold=False
        temp_dew=""   #Temperatur oder Taupunkt, Hilfsvariabel
        info_new=""
        for i in range(len(info)):
            if info[i]=="M":                        #wenn M:
                temp_dew+="-"                       #Temperaturvorzeichen
            elif re.search("[0-9]", info[i])!=None: #wenn Zahl:
                temp_dew+=info[i]                   #Zahl Teil
            
            elif info[i]=="/":                              #wenn /:
                if len(temp_dew)==0:                        #wenn nichts im Puffer: ignorieren, ansonsten Temperatur
                    continue
                if 0<=int(temp_dew):                        #wenn 0°C<=T:
                    info_new+=f"{int(temp_dew):02.0f}°C/"   #konvertieren, weiterleiten
                else:                                       #wenn T<0°C:
                    info_new+=f"{int(temp_dew):03.0f}°C/"   #konvertieren immer mit 2 Stellen aufgefüllt mit Nullen, weiterleiten

                if ("temp_min" in WEATHER_MIN and int(temp_dew)<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<int(temp_dew)):  #wenn Temperatur außerhalb Grenzen, wegen Leistungstabellen und Vereisung
                    bold=True
                temp_dew=""
            
            if i==len(info)-1:                              #wenn Durchgang letzter:
                if len(temp_dew)==0:                        #wenn nichts im Puffer: ignorieren, ansonsten Taupunkt
                    continue
                if 0<=int(temp_dew):                        #wenn 0°C<=T:
                    info_new+=f"{int(temp_dew):02.0f}°C"    #konvertieren, weiterleiten
                else:                                       #wenn T<0°C:
                    info_new+=f"{int(temp_dew):03.0f}°C"    #konvertieren, weiterleiten
                temp_dew=""

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new


    #USA: Temperatur und Taupunkt
    if re.search("^T[01][0-9][0-9][0-9][01][0-9][0-9][0-9]$", info)!=None:
        bold=False
        info_new=""
        temp_dew=""  #Temperatur oder Taupunkt, Hilfsvariabel

        
        if info[1]=="1":                            #wenn Vorzeichen negativ:
            temp_dew+="-"
        temp_dew+=f"{int(info[2:5])/10:04.1f}"
        info_new+=f"{temp_dew}°C/".replace(".", ",")
        
        if ("temp_min" in WEATHER_MIN and float(temp_dew)<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<float(temp_dew)):  #wenn Temperatur außerhalb Grenzen, wegen Leistungstabellen und Vereisung
            bold=True

        temp_dew=""
        if info[5]=="1":    #wenn Vorzeichen negativ:
            temp_dew+="-"
        temp_dew+=f"{int(info[6:9])/10:04.1f}"
        info_new+=f"{temp_dew}°C".replace(".", ",")

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new