import datetime as dt
import re
import requests #http Zeugs
from change_format                  import change_format                    #Informationsformat ändern
from change_format_RMK              import change_Format_RMK                #in RMK-Sektion Informationsformat ändern
from KFS                            import KFSlog
from remove_unnecessary_whitespaces import remove_unnecessary_whitespaces   #Leerzeichen unnötig entfernen
from split                          import split                            #Liste trennen an mehreren Seperatoren


def process_TAF(station, station_elev, RWY_DB, force_print, DOWNLOAD_TIMEOUT):
    DT_publishion=dt.datetime(1970, 1, 1)   #Veröffentlichungszeitpunkt
    RMK=False                               #jetzt in RMK-Sektion?
    TAF_o=""                                #TAF Originalformatierung
    TAF_o_list=[]                           #TAF Originalformatierung als Liste, getrennt an " " und "\n"
    TAF=""                                  #TAF Felixformatierung :)
    timespan_published=dt.timedelta()       #Zeitspanne veröffentlicht


    #TAF herunterladen
    KFSlog.write("Downloading TAF...")
    TAF_o=requests.get(f"http://tgftp.nws.noaa.gov/data/forecasts/taf/stations/{station}.TXT", timeout=DOWNLOAD_TIMEOUT)    #TAF herunterladen
    
    if TAF_o.status_code==404:
        KFSlog.write(f"\r{station} TAF could not be found online.")
        return "", ""   #TAF leer zurückgeben für gescheite Rückmeldung an Nutzer

    TAF_o=TAF_o.text
    KFSlog.write("\rTAF downloaded.")
    TAF_o=remove_unnecessary_whitespaces(TAF_o) #löscht Leerzeichen doppelt und in jeder "Zeile" Leerzeichen führend und nachfolgend
    KFSlog.write(TAF_o)
    if TAF_o=="":
        return "", ""
    TAF_o_list=split(TAF_o, " ", "\n")  #TAF Originalformatierung als Liste, getrennt an " " und "\n"
    if TAF_o_list[2]!="TAF":            #wenn kein TAF heruntergeladen (siehe EDFE TAF)
        return "", ""

    #TAF abgelaufen?
    for info in TAF_o_list:
        if re.search("^[0-9][0-9][0-9][0-9][0-9][0-9]Z$", info)==None:  #wenn nicht Tag-Zeit-Gruppe: nächste Info
            continue

        DT_publishion=dt.datetime(int(TAF_o[0:4]), int(TAF_o[5:7]), int(TAF_o[8:10]), 0, 0, 0, 0, dt.timezone.utc)  #Veröffentlichungsdatum laut Anfang
        while int(DT_publishion.strftime("%d"))!=int(info[0:2]):                                                    #solange Tag nicht stimmt, also wenn nach Met Report Time nochmal aktualisiert :
            DT_publishion-=dt.timedelta(days=1)                                                                     #Tag abziehen
        DT_publishion+=dt.timedelta(hours=int(info[2:4]), minutes=int(info[4:6]))                                   #Berichtsuhrzeit laut Tag-Zeit-Gruppe
        timespan_published=dt.datetime.now(dt.timezone.utc)-DT_publishion                                           #Zeitspanne veröffentlicht
        if dt.timedelta(seconds=86400)<timespan_published:                                                          #wenn TAF abgelaufen:
            TAF+="**EXPIRED** "                                                                                     #markieren
        break
    else:
        KFSlog.write("TAF report time could not be parsed. Expiration status is uncertain.")

    #TAF Konvertieren
    KFSlog.write("Converting TAF...")
    i=0
    while i<len(TAF_o_list): #alle Informationen im TAF nacheinander durch, while-Schleife weil man mit for keine Elemente während des Durchlaufens von TAF_o_List löschen kann
        if RMK==False:
            TAF_Info_new=change_format    (TAF_o_list, i, station, station_elev, TAF_o[:16], RWY_DB, force_print)  #Info mit Format neu an TAF anhängen, change_Format(...) sorgt nach Bedarf mit Separierung durch Leerzeichen oder Zeilenumbrüchen
        else:                                                                                               #wenn in RMK-Sektion:
            TAF_Info_new=change_Format_RMK(TAF_o_list, i, station, station_elev, TAF_o[:16], RWY_DB)        #Info mit Format neu an TAF ahänangen, change_Format_RMK(...) sorgt nach Bedarf mit Separierung

        if TAF_Info_new==" RMK" or TAF_Info_new==" FIRST" or TAF_Info_new==" LAST": #wenn Info neu RMK-Marker oder RMK-Marker indirekt:
            RMK=True                            #RMK-Sektion folgt
            TAF_Info_new="\n"+TAF_Info_new[1:]  #Gruppe aktuell soll mit Zeilenumbruch anfangen, nicht mit Leerzeichen
        
        TAF+=TAF_Info_new   #Info neu anhängen
        i+=1
    
    TAF_o=TAF_o[17:]    #Datum vollständig am Anfang entfernen
    TAF=TAF.strip()     #Leerzeichen unnötig am Anfang und Ende entfernen, falls vorhanden
    KFSlog.write("\rTAF converted.")
    KFSlog.write(TAF)

    return TAF_o, TAF