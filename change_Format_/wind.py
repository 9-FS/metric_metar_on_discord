import numpy as np  #für CWC, np-Funktionen wegen Dataframeseingabe
import re           #Regular Expressions


def change_format_wind(info, station, RWY_DB):
    if re.search("^VRB[0-9][0-9]MPS$", info)!=None:
        info_new=info.replace("MPS", "m/s")
        if 10*0.5144444<int(info[3:5]): #TWC max. 10kt (5m/s)
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^VRB[0-9][0-9]KT$", info)!=None:
        info_new=f"VRB{int(info[3:5])*0.5144444:02.0f}m/s"
        if 10*0.5144444<int(info[3:5])*0.5144444:   #TWC max. 10kt (5m/s)
            info_new=f"***{info_new}**"
        return " "+info_new

    if re.search("^VRB[0-9][0-9]G[0-9][0-9]MPS$", info)!=None:
        info_new=info.replace("MPS", "m/s")
        if 10*0.5144444<int(info[6:8]): #TWC max. 10kt (5m/s)
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^VRB[0-9][0-9]G[0-9][0-9]KT$", info)!=None:
        info_new=f"VRB{int(info[3:5])*0.5144444:02.0f}G{int(info[6:8])*0.5144444:02.0f}m/s"
        if 10*0.5144444<int(info[6:8])*0.5144444:   #TWC max. 10kt (5m/s)
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^[0-3][0-9][0-9][0-9][0-9]MPS$", info)!=None:
        bold=True
        CWC=[]      #auf Pisten Seitenwindkomponenten [m/s]
        info_new=""
        if info[0:3]!="360":
            info_new=f"{info[0:3]}°{info[3:5]}m/s"
        else:
            info_new=f"000°{info[3:5]}m/s"

        RWY=RWY_DB[RWY_DB["airport_ident"]==station]                                                            #in Flughafen Pisten gesucht
        if RWY.empty==False:                                                                                    #wenn Pisten gefunden:
            CWC+=list((abs(np.sin(np.radians(int(info[0:3])-RWY["le_heading_degT"]))*int(info[3:5]))).dropna()) #sin(Richtungsdifferenz)*Windgeschwindigkeit, Betrag, Nans entfernen, konvertieren zu Liste
        else:                           #wenn keine Piste in Datenbank gefunden:
            CWC.append(int(info[3:5]))  #direkten Seitenwind annehmen
        for i in range(len(CWC)):
            if CWC[i]<=20*0.5144444:    #wenn zumindest 1 Seitenwindkomponente<=20kt (10m/s):
                bold=False              #landbar
                break

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^[0-3][0-9][0-9][0-9][0-9]KT$", info)!=None:
        bold=True
        CWC=[]      #auf Pisten Seitenwindkomponenten [m/s]
        info_new=""
        if info[0:3]!="360":
            info_new=f"{info[0:3]}°{int(info[3:5])*0.5144444:02.0f}m/s"
        else:
            info_new=f"000°{int(info[3:5])*0.5144444:02.0f}m/s"

        RWY=RWY_DB[RWY_DB["airport_ident"]==station]                                                            #in Flughafen Pisten gesucht
        if RWY.empty==False:                                                                                    #wenn Pisten gefunden:
            CWC+=list((abs(np.sin(np.radians(int(info[0:3])-RWY["le_heading_degT"]))*int(info[3:5])*0.5144444)).dropna()) #sin(Richtungsdifferenz)*Windgeschwindigkeit, Betrag, Nans entfernen, konvertieren zu Liste
        else:                                       #wenn keine Piste in Datenbank gefunden:
            CWC.append(int(info[3:5])*0.5144444)    #direkten Seitenwind annehmen
        for i in range(len(CWC)):
            if CWC[i]<=20*0.5144444:    #wenn zumindest 1 Seitenwindkomponente<=20kt (10m/s):
                bold=False              #landbar
                break

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^[0-3][0-9][0-9][0-9][0-9]G[0-9][0-9]MPS$", info)!=None:
        bold=True
        CWC=[]      #auf Pisten Seitenwindkomponenten [m/s]
        info_new=""
        if info[0:3]!="360":
            info_new=f"{info[0:3]}°{info[3:5]}G{info[6:8]}m/s"
        else:
            info_new=f"000°{info[3:5]}G{info[6:8]}m/s"

        RWY=RWY_DB[RWY_DB["airport_ident"]==station]                                                            #in Flughafen Pisten gesucht
        if RWY.empty==False:                                                                                    #wenn Pisten gefunden:
            CWC+=list((abs(np.sin(np.radians(int(info[0:3])-RWY["le_heading_degT"]))*int(info[6:8]))).dropna()) #sin(Richtungsdifferenz)*Windgeschwindigkeit, Betrag, Nans entfernen, konvertieren zu Liste
        else:                           #wenn keine Piste in Datenbank gefunden:
            CWC.append(int(info[6:8]))  #direkten Seitenwind annehmen
        for i in range(len(CWC)):
            if CWC[i]<=20*0.5144444:    #wenn zumindest 1 Seitenwindkomponente<=20kt (10m/s):
                bold=False              #landbar
                break

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^[0-3][0-9][0-9][0-9][0-9]G[0-9][0-9]KT$", info)!=None:
        bold=True
        CWC=[]      #auf Pisten Seitenwindkomponenten [m/s]
        info_new=""
        if info[0:3]!="360":
            info_new=f"{info[0:3]}°{int(info[3:5])*0.5144444:02.0f}G{int(info[6:8])*0.5144444:02.0f}m/s"
        else:
            info_new=f"000°{int(info[3:5])*0.5144444:02.0f}G{int(info[6:8])*0.5144444:02.0f}m/s"

        RWY=RWY_DB[RWY_DB["airport_ident"]==station]                                                                        #in Flughafen Pisten gesucht
        if RWY.empty==False:                                                                                                #wenn Pisten gefunden:
            CWC+=list((abs(np.sin(np.radians(int(info[0:3])-RWY["le_heading_degT"]))*int(info[6:8])*0.5144444)).dropna())   #sin(Richtungsdifferenz)*Windgeschwindigkeit, Betrag, Nans entfernen, konvertieren zu Liste
        else:                                       #wenn keine Piste in Datenbank gefunden:
            CWC.append(int(info[6:8])*0.5144444)    #direkten Seitenwind annehmen
        for i in range(len(CWC)):
            if CWC[i]<=20*0.5144444:    #wenn zumindest 1 Seitenwindkomponente<=20kt (10m/s):
                bold=False              #landbar
                break

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^ABV49MPS$", info)!=None or re.search("^ABV99KT$", info)!=None:
        info="50m/s+"
        return " "+f"**{info}**"

    if re.search("^[0-3][0-9][0-9]V[0-3][0-9][0-9]$", info)!=None:
        if info[0:3]!="360":
            info_new=f"{info[0:3]}°V"
        else:
            info_new="000°V"
        if info[4:7]!="360":
            info_new+=f"{info[4:7]}°"
        else:
            info_new+="000°"
        return " "+info_new