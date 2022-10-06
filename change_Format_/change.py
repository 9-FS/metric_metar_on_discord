import datetime
import re   #Regular Expressions


def change_format_change(Info_List, i, Date):
    if(   re.search("^NOSIG$", Info_List[i])!=None
       or re.search("^BECMG$", Info_List[i])!=None
       or re.search("^TEMPO$", Info_List[i])!=None):
        try:
            if re.search("^PROB[0-9][0-9]$", Info_List[i-1])!=None:  #wenn Gruppe davor PROBxx: kein Zeilenumbruch
                return " "+Info_List[i]
        except IndexError:              #wenn Gruppe davor nicht existiert:
            pass                        #nix tun
        return "\n"+Info_List[i]        #bei Änderungsgruppe neu: Zeilenumbruch

    if re.search("^PROB[0-9][0-9]$", Info_List[i])!=None:
        if Info_List[i][5]=="0":
            Info_new=f"PROB0,{Info_List[i][4]}"
        else:
            Info_new=f"PROB0,{Info_List[i][4:6]}"
        return "\n"+Info_new          #bei Änderungsgruppe neu: Zeilenumbruch


    if re.search("^(FM|TL|AT)[0-3][0-9][0-2][0-9][0-5][0-9]$", Info_List[i])!=None:
        DT=datetime.datetime(int(Date[0:4]), int(Date[5:7]), int(Date[8:10]), 0, 0)             #Eventdatum, initialisiert mit Veröffentlichungsdatum
        while DT.strftime("%d")!=Info_List[i][2:4]:                                             #solange Eventtag nicht stimmt:
            DT+=datetime.timedelta(days=1)                                                      #Tag hinzufügen
        DT+=datetime.timedelta(hours=int(Info_List[i][4:6]), minutes=int(Info_List[i][6:8]))    #zu Startdatum Uhrzeit hinzufügen

        #Info_new=f"{Info_List[i][0:2]}{DT.strftime('%Y-%m-%dT%H:%M')}"
        Info_new=f"{Info_List[i][0:2]}{DT.strftime('%dT%H:%M')}"

        try:
            if Info_List[i-1]=="BECMG" or re.search("^PROB[0-9][0-9]$", Info_List[i-1])!=None:  #wenn Gruppe davor BECMG oder PROBxx: kein Zeilenumbruch
                return " "+Info_new
        except IndexError:              #wenn Gruppe davor nicht existiert:
            pass                        #nix tun
        return "\n"+Info_new          #bei Änderungsgruppe neu: Zeilenumbruch

    if re.search("^(FM|TL|AT)[0-2][0-9][0-5][0-9]$", Info_List[i])!=None:
        DT=datetime.datetime(int(Date[0:4]), int(Date[5:7]), int(Date[8:10]), 0, 0)             #Eventdatum, initialisiert mit Veröffentlichungsdatum
        if int(Info_List[i][2:4])<int(Date[11:13]):                                             #wenn Eventstunde<Veröffentlichungsstunde:
            DT+=datetime.timedelta(days=1)                                                      #Tag nächster
        DT+=datetime.timedelta(hours=int(Info_List[i][2:4]), minutes=int(Info_List[i][4:6]))    #zu Startdatum Uhrzeit hinzufügen

        #Info_new=f"{Info_List[i][0:2]}{DT.strftime('%Y-%m-%dT%H:%M')}"
        Info_new=f"{Info_List[i][0:2]}{DT.strftime('%dT%H:%M')}"
        
        try:
            if Info_List[i-1]=="BECMG" or re.search("^PROB[0-9][0-9]$", Info_List[i-1])!=None:  #wenn Gruppe davor BECMG oder PROBxx: kein Zeilenumbruch
                return " "+Info_new
        except IndexError:              #wenn Gruppe davor nicht existiert:
            pass                        #nix tun
        return "\n"+Info_new          #bei Änderungsgruppe neu: Zeilenumbruch