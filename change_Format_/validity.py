import datetime
import re   #Regular Expressions


def change_format_validity(info, date):
    if re.search("^[0-3][0-9][0-2][0-9]/[0-3][0-9][0-2][0-9]$", info)!=None:
        DT_publishion=datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), int(date[11:13]), int(date[14:16]))    #Veröffentlichungszeitpunkt

        #Startzeitpunkt
        DT_start=datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), 0, 0)   #Startdatum, initialisiert mit Veröffentlichungsdatum
        while DT_start.strftime("%d")!=info[0:2]:                                           #solange Starttag nicht stimmt:
            DT_start+=datetime.timedelta(days=1)                                            #Tag hinzufügen
        DT_start+=datetime.timedelta(hours=int(info[2:4]))                                  #zu Startdatum Uhrzeit hinzufügen

        #Endzeitpunkt
        DT_end=DT_start                                     #Endzeitpunkt, initialsiert mit Startzeitpunkt
        DT_end-=datetime.timedelta(hours=int(info[2:4]))    #Enddatum
        while DT_end.strftime("%d")!=info[5:7]:             #solange Endtag nicht stimmt:
            DT_end+=datetime.timedelta(days=1)              #Tag hinzufügen
        DT_end+=datetime.timedelta(hours=int(info[7:9]))    #zu Enddatum Uhrzeit hinzufügen

        if DT_publishion.strftime("%Y-%m")==DT_start.strftime("%Y-%m"): #wenn Jahr und Monat gleich:
            info_new=f"{DT_start.strftime('%dT%H')}/"                   #Endzeitpunkt nur Tag und Stunde
        elif DT_publishion.strftime("%Y")==DT_start.strftime("%Y"):     #wenn Jahr gleich:
            info_new=f"{DT_start.strftime('%Y-%m-%dT%H')}/"             #Endzeitpunkt nur Monat, Tag und Stunde
        else:                                                           #wenn nichts gleich:
            info_new=f"{DT_start.strftime('%Y-%m-%dT%H')}/"             #Endzeitpunkt voll mit Jahr, Monat, Tag und Stunde

        if   DT_start.strftime("%Y-%m-%d")==DT_end.strftime("%Y-%m-%d"):    #wenn Jahr, Monat und Tag gleich:
            info_new+=f"{DT_end.strftime('%H')}"                            #Endzeitpunkt nur Stunde
        elif DT_start.strftime("%Y-%m")==DT_end.strftime("%Y-%m"):          #wenn Jahr und Monat gleich:
            info_new+=f"{DT_end.strftime('%dT%H')}"                         #Endzeitpunkt nur Tag und Stunde
        elif DT_start.strftime("%Y")==DT_end.strftime("%Y"):                #wenn Jahr gleich:
            info_new+=f"{DT_end.strftime('%m-%dT%H:00')}"                   #Endzeitpunkt nur Monat, Tag und Uhrzeit
        else:                                                               #wenn nichts gleich:
            info_new+=f"{DT_end.strftime('%Y-%m-%dT%H')}"                   #Endzeitpunkt voll mit Jahr, Monat, Tag und Stunde

        return " "+info_new