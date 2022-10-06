import datetime as dt
from multiprocessing.sharedctypes import Value
import re
import requests #http Zeugs
from change_format                  import change_format                    #Informationsformat ändern
from change_format_RMK              import change_Format_RMK                #in RMK-Sektion Informationsformat ändern
from KFS                            import KFSlog
from remove_unnecessary_whitespaces import remove_unnecessary_whitespaces   #Leerzeichen unnötig entfernen
from split                          import split                            #Liste trennen an mehreren Seperatoren


def process_METAR(station, station_elev, RWY_DB, force_print, DOWNLOAD_TIMEOUT):
    DT_publishion=dt.datetime(1970, 1, 1)   #Veröffentlichungszeitpunkt
    METAR_o=""                              #METAR Originalformatierung
    METAR_o_list=[]                         #METAR Originalformatierung als Liste, getrennt an " " und "\n"
    METAR=""                                #METAR Neuformatierung
    RMK=False                               #jetzt in RMK-Sektion?
    timespan_published=dt.timedelta()       #Zeitspanne veröffentlicht


    #METAR herunterladen
    KFSlog.write("Downloading METAR...")
    METAR_o=requests.get(f"http://tgftp.nws.noaa.gov/data/observations/metar/stations/{station}.TXT", timeout=DOWNLOAD_TIMEOUT) #METAR herunterladen
    
    if METAR_o.status_code==404:
        KFSlog.write(f"\r{station} METAR could not be found online.")
        return "", ""   #METAR leer zurückgeben für gescheite Rückmeldung an Nutzer

    METAR_o=METAR_o.text
    KFSlog.write("\rMETAR downloaded.")
    METAR_o=remove_unnecessary_whitespaces(METAR_o) #löscht Leerzeichen doppelt und in jeder "Zeile" Leerzeichen führend und nachfolgend
    KFSlog.write(METAR_o)
    if METAR_o=="":
        return "", ""
    METAR_o_list=split(METAR_o, " ", "\n")  #METAR Originalformatierung als Liste, getrennt an " " und "\n"


    #METAR abgelaufen?
    for info in METAR_o_list:                                           #alle Infos durchgehen
        if re.search("^[0-9][0-9][0-9][0-9][0-9][0-9]Z$", info)==None:  #wenn nicht Tag-Zeit-Gruppe: nächste Info
            continue
        
        DT_publishion=dt.datetime(int(METAR_o[0:4]), int(METAR_o[5:7]), int(METAR_o[8:10]), 0, 0, 0, 0, dt.timezone.utc)    #Veröffentlichungsdatum laut Anfang
        while int(DT_publishion.strftime("%d"))!=int(info[0:2]):                                                            #solange Tag nicht stimmt, also wenn nach Met Report Time nochmal aktualisiert:
            DT_publishion-=dt.timedelta(days=1)                                                                             #Tag abziehen   
        DT_publishion+=dt.timedelta(hours=int(info[2:4]), minutes=int(info[4:6]))                                           #Berichtsuhrzeit laut Tag-Zeit-Gruppe
        timespan_published=dt.datetime.now(dt.timezone.utc)-DT_publishion                                                   #Zeitspanne veröffentlicht
        if dt.timedelta(seconds=3600)<timespan_published:                                                                   #wenn METAR abgelaufen:
            METAR+="**EXPIRED** "                                                                                           #markieren
        break
    else:
        KFSlog.write("METAR report time could not be parsed. Expiration status is uncertain.")

    #METAR konvertieren
    KFSlog.write("Converting METAR...")
    i=0
    while i<len(METAR_o_list):   #alle Informationen im METAR nacheinander durch, while-Schleife weil man mit for keine Elemente während des Durchlaufens von METAR_o_List löschen kann
        if RMK==False:
            METAR_Info_new=change_format    (METAR_o_list, i, station, station_elev, METAR_o[:16], RWY_DB, force_print) #Info mit Format neu an METAR anhängen, change_Format(...) sorgt nach Bedarf mit Separierung durch Leerzeichen oder Zeilenumbrüchen
        else:                                                                                                           #wenn in RMK-Sektion:
            METAR_Info_new=change_Format_RMK(METAR_o_list, i, station, station_elev, METAR_o[:16], RWY_DB)              #Info mit Format neu an METAR ahänangen, change_Format_RMK(...) sorgt nach Bedarf mit Separierung

        if METAR_Info_new==" RMK" or METAR_Info_new==" FIRST" or METAR_Info_new==" LAST":  #wenn Info neu RMK-Marker oder RMK-Marker indirekt:
            RMK=True                                #RMK-Sektion folgt
            METAR_Info_new="\n"+METAR_Info_new[1:]  #Gruppe aktuell soll mit Zeilenumbruch anfangen, nicht mit Leerzeichen
        
        METAR+=METAR_Info_new   #Info neu anhängen
        i+=1
    
    METAR_o=METAR_o[17:]    #Datum vollständig am Anfang entfernen
    METAR=METAR.strip()     #Leerzeichen unnötig am Anfang und Ende entfernen, falls vorhanden
    KFSlog.write("\rMETAR converted.")
    KFSlog.write(METAR)

    return METAR_o, METAR