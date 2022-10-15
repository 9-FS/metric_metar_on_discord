import datetime
import numpy as np  #für CWC, np-Funktionen wegen Dataframeseingabe
import re           #Regular Expressions
import KFS.fstr
from weather_minimums import WEATHER_MIN


def change_format_USA_codes(info, date, station, RWY_DB):
    #USA: Wetterbeginn oder Wetterende
    if re.search("^(([+-]|)([A-Z][A-Z]|)([A-Z][A-Z]|)([A-Z][A-Z]|)[BE]([0-9][0-9]|)[0-9][0-9])+$", info)!=None:
        info_new=""
        time=""     #Information Uhrzeit
        time_i=-1   #Uhrzeitbeginn Index


        Infos=re.findall("(([+-]|)([A-Z][A-Z]|)([A-Z][A-Z]|)([A-Z][A-Z]|)[BE]([0-9][0-9]|)[0-9][0-9])", info)    #Informationsgruppen trennen
        for i in range(len(Infos)): #weil findall aus GRÜNDEN alles extra gibt was in Klammern ist:
            Infos[i]=Infos[i][0]    #alles entfernen außer Informationen relevant


        for i in range(len(Infos)):                                         #Informationsgruppen alle durch
            for j in range(len(Infos[i])):                                  #Information durch, Uhrzeitindex suchen
                if re.search("^[0-9]$", Infos[i][j])!=None and time_i==-1:  #wenn Zahl gefunden:
                    time_i=j                                                #Uhrzeit
                    time=Infos[i][time_i:]
                    break

            DT=datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), int(date[11:13]), int(date[14:16]))      #Event, initialisiert mit Veröffentlichungzeitpunkt
            if len(time)==4:                            #wenn Uhrzeit gegeben 4 Stellen [h][min]
                while(DT.strftime("%M")!=time[2:4]):    #so lange von Veröffentlichungszeitpunkt Minuten abziehen bis übereinstimmt
                    DT-=datetime.timedelta(minutes=1)
                while(DT.strftime("%H")!=time[0:2]):    #so lange von Veröffentlichungszeitpunkt Stunden abziehen bis übereinstimmt
                    DT-=datetime.timedelta(hours=1)
            elif len(time)==2:                          #wenn Uhrzeit gegeben 2 Stellen [min]
                while(DT.strftime("%M")!=time):         #so lange von Veröffentlichungszeitpunkt Minuten abziehen bis übereinstimmt
                    DT-=datetime.timedelta(minutes=1)
            else:                                       #wenn Uhrzeit weder 2 noch 4 Stellen hat: da is was schiefjelaufe
                raise Exception("Error in change_Format_USA_Codes(Info, Date), \"^(([+-]|)([A-Z][A-Z]|)([A-Z][A-Z]|)[A-Z][A-Z][BE]([0-9][0-9]|)[0-9][0-9])+\": Time must consist of either 2 or 4 digits.")

            info_new+=" "                   #Leerzeichentrenner
            if Infos[i][time_i-1]=="B":     #wenn Wetterbeginn:
                info_new+="FM"
            elif Infos[i][time_i-1]=="E":   #wenn Wetterende:
                info_new+="TL"
            else:
                raise Exception("Error in change_Format_USA_Codes(Info, Date), \"^(([+-]|)([A-Z][A-Z]|)([A-Z][A-Z]|)[A-Z][A-Z][BE]([0-9][0-9]|)[0-9][0-9])+\": Character before time must be either \"B\" (begin) or \"E\" (end).")
            info_new+=f"{DT.strftime('%H:%M')}"
            if Infos[i][:time_i-1]!="":
                info_new+=f"/{Infos[i][:time_i-1]}"
            time=""
            time_i=-1
        return info_new

    #USA: Peak Wind
    if re.search("^[0-3][0-9][0-9][0-9][0-9]/[0-9][0-9][0-9][0-9]$", info)!=None:
        bold=True
        CWC=[]      #auf Pisten Seitenwindkomponenten [m/s]
        info_new=""
        
        if info[0:3]!="360":
            info_new=f"{info[6:8]}:{info[8:10]}/{info[0:3]}°{int(info[3:5])*0.5144444:02.0f}m/s"
        else:
            info_new=f"{info[6:8]}:{info[8:10]}/000°{int(info[3:5])*0.5144444:02.0f}m/s"

        RWY=RWY_DB[RWY_DB["airport_ident"]==station]                                                            #in Flughafen Pisten gesucht
        if RWY.empty==False:                                                                                    #wenn Pisten gefunden:
            CWC+=list((abs(np.sin(np.radians(int(info[0:3])-RWY["le_heading_degT"]))*int(info[3:5])*0.5144444)).dropna()) #sin(Richtungsdifferenz)*Windgeschwindigkeit, Betrag, Nans entfernen, konvertieren zu Liste
        else:                                       #wenn keine Piste in Datenbank gefunden:
            CWC.append(int(info[3:5])*0.5144444)    #direkten Seitenwind annehmen
        for i in range(len(CWC)):
            if CWC[i]<=WEATHER_MIN["CWC"]:  #wenn zumindest 1 Seitenwindkomponente unter Maximum:
                bold=False                  #landbar
                break

        if WEATHER_MIN["wind"]<int(info[3:5])*0.5144444:    #wenn trotz landbarem Seitenwind Gesamtwind einfach zu stark:
            bold=True

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new


    #USA: Niederschlagswasseräquivalent
    if re.search("^P[0-9][0-9][0-9][0-9]$", info)!=None:
        info=f"PWE/{KFS.fstr.notation_tech(int(info[1:5])/100*0.0254, 2)}m"
        return " "+info

    #USA Code 1 und 2: 22ks (6h) Temperatur max und min
    if re.search("^[12][01][0-9][0-9][0-9]$", info)!=None:
        bold=False
        info_new=""
        temp=""

        if   info[0]=="1":
            info_new+="TX6h/"
        elif info[0]=="2":
            info_new+="TN6h/"
        if info[1]=="1":      #wenn Vorzeichen negativ:
            temp+="-"
        temp+=f"{int(info[2:5])/10:.1f}"
        info_new=f"{temp}°C".replace(".", ",")

        if ("temp_min" in WEATHER_MIN and float(temp)<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<float(temp)):  #wenn Temperatur außerhalb Grenzen, wegen Leistungstabellen und Vereisung
            bold=True
        
        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new

    #USA Code 4/: Schneetiefe
    if re.search("^4/[0-9][0-9][0-9]$", info)!=None:
        info_new=f"SNOW/{KFS.fstr.notation_tech(int(info[2:5])*0.0254, 2)}m"
        if 0<int(info[2:5]):
            info_new=f"**{info_new}**"
        return " "+info_new

    #USA Code 4: 86ks (24h) Temperatur max und min
    if re.search("^4[01][0-9][0-9][0-9][01][0-9][0-9][0-9]$", info)!=None:
        temp="" #Temperatur, Hilfsvariabel
        TN24h=""
        TX24h=""

        TX24h="TX24h/"
        if info[1]=="1":    #wenn Vorzeichen negativ:
            temp+="-"
        temp+=f"{int(info[2:5])/10:04.1f}"
        TX24h+=f"{temp}°C".replace(".", ",")
        
        if ("temp_min" in WEATHER_MIN and float(temp)<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<float(temp)):  #wenn Temperatur außerhalb Grenzen, wegen Leistungstabellen und Vereisung
            TX24h=f"**{TX24h}**"

        temp=""
        TN24h="TN24h/"
        if info[5]=="1":    #wenn Vorzeichen negativ:
            temp+="-"
        temp+=f"{int(info[6:9])/10:04.1f}"
        TN24h=f"{temp}°C".replace(".", ",")

        if ("temp_min" in WEATHER_MIN and float(temp)<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<float(temp)):  #wenn Temperatur außerhalb Grenzen, wegen Leistungstabellen und Vereisung
            TN24h=f"**{TN24h}**"

        info_new=f"{TX24h} {TN24h}"
        return " "+info_new

    #USA Code 5: 11ks (3h) Drucktendenz
    if re.search("^5[0-8][0-9][0-9][0-9]$", info)!=None:
        info_new="ΔPRES3h/"
        if   0<=int(info[1]) and int(info[1])<=3:   #wenn Trend steigend:
            info_new+="+"
        elif 5<=int(info[1]) and int(info[1])<=8:   #wenn Trend sinkend:
            info_new+="-"
        if 1000<=int(info[2:5])*10:             #wenn 1kPa<=Druckänderung:
            info_new+=f"{int(info[2:5])*10/1000:.2f}kPa".replace(".", ",")
        else:                                   #wenn Druckänderung<1kPa
            info_new+=f"{int(info[2:5])*10:.0f}Pa"
        return " "+info_new

    #USA Code 6: in 11ks (3h) oder 22ks (6h) Niederschlagsmenge
    if re.search("^6[0-9][0-9][0-9][0-9]$", info)!=None:
        info=f"PCPN(3h,6h)/{KFS.fstr.notation_tech(int(info[1:5])/100*0.0254, 2)}m"
        return " "+info

    #USA Code 7: in 86ks (24h) Niederschlagsmenge
    if re.search("^7[0-9][0-9][0-9][0-9]$", info)!=None:
        info=f"PCPN24h/{KFS.fstr.notation_tech(int(info[1:5])/100*0.0254, 2)}m"
        return " "+info

    #USA Code 8/: Wolkenart
    if re.search("^8/[0-9][0-9/][0-9/]$", info)!=None:
        bold=False
        
        info_new="CLOUDS/"
        if   info[2]=="0":
            info_new+="-/"              #nix
        elif info[2]=="1":
            info_new+="CU/"             #Cumulus
        elif info[2]=="2":
            info_new+="CU-CON/"         #Cumulus Congestus
        elif info[2]=="3":
            info_new+="CB-CAL/"         #Cumulonimubus Calvus
        elif info[2]=="4":
            info_new+="SC/"             #Stratocumulus
        elif info[2]=="5":
            info_new+="SC/"             #Stratocumulus
        elif info[2]=="6":
            info_new+="ST,ST-FRA/"      #Stratus oder Stratofractus
            bold=True
        elif info[2]=="7":
            info_new+="CUFRA,ST-FRA/"   #Cumulufractus oder Stratofractus
            bold=True
        elif info[2]=="8":
            info_new+="CU,SC/"          #Cumulus oder Stratocumulus
        elif info[2]=="9":
            info_new+="CB/"             #Cumulonimbus
            bold=True
        if   info[3]=="0":
            info_new+="-/"              #nix
        elif info[3]=="1":
            info_new+="AS-HUM/"         #Altostratus dünn
        elif info[3]=="2":
            info_new+="AS-CON/"         #Altostratus dick
        elif info[3]=="3":
            info_new+="AC-HUM/"         #Altocumulus dünn
        elif info[3]=="4":
            info_new+="AC/"             #Altocumulus
        elif info[3]=="5":
            info_new+="AC-CON/"         #Altocumulus dick
        elif info[3]=="6":
            info_new+="AC/"             #Altocumulus
        elif info[3]=="7":
            info_new+="AC,AS,NS/"       #Altocumulus, Altostratus oder Nimbostratus
        elif info[3]=="8":
            info_new+="AC-CAS/"         #Altocumulus Castellanus
        elif info[3]=="9":
            info_new+="AC-FRA/"         #Altocumulus chaotisch
        elif info[3]=="/":
            info_new+="ABV-OVC/"        #über OVC Wolken
        if   info[4]=="0":
            info_new+="-"               #nix
        elif info[4]=="1":
            info_new+="CI"              #Cirrus
        elif info[4]=="2":
            info_new+="CI"              #Cirrus
        elif info[4]=="3":
            info_new+="CI"              #Cirrus
        elif info[4]=="4":
            info_new+="CI-CON"          #Cirrus dick
        elif info[4]=="5":
            info_new+="CI-LOW,CS-LOW"   #Cirrus tief oder Cirrostratus tief
        elif info[4]=="6":
            info_new+="CI-HIG,CS-HIG"   #Cirrus hoch oder Cirrostratus hoch
        elif info[4]=="7":
            info_new+="CS"              #Cirrustratus
        elif info[4]=="8":
            info_new+="CS"              #Cirrustratus
        elif info[4]=="9":
            info_new+="CC,CI,CS"        #Cirrocumulus oder Cirrus oder Cirrostratus
        elif info[4]=="/":
            info_new+="ABV-OVC"         #über OVC Wolken

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new

    #USA Code 98: Sonnenscheindauer
    if re.search("^98[0-9][0-9][0-9]$", info)!=None:
        info=f"SUN/{KFS.fstr.notation_tech(int(info[2:5])*60, 2)}s"
        return " "+info

    #USA Code 931: in 22ks (6h) Schneemenge
    if re.search("^931[0-9][0-9][0-9]$", info)!=None:
        info_new=f"SNOW6h/{KFS.fstr.notation_tech(int(info[3:6])/10*0.0254, 2)}m"
        if 0<int(info[3:6]):
            info_new=f"**{info_new}**"
        return " "+info_new

    #USA Code 933: Schneeflüssigkeitsäquivalent
    if re.search("^933[0-9][0-9][0-9]$", info)!=None:
        info=f"SWE/{KFS.fstr.notation_tech(int(info[3:6])/10*0.0254, 2)}m"
        return " "+info