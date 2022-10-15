import datetime as dt
import re   #Regular Expressions
import KFS.fstr

def change_format_time(info, date, force_print):
    if( re.search("^[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]$", info)!=None   #am Anfang Angabe vollständig entfernen
    or  re.search("^[0-9][0-9]:[0-9][0-9]$", info)!=None):
        return ""

    if re.search("^[0-9][0-9][0-9][0-9][0-9][0-9]Z$", info)!=None:
        DT_publishion=dt.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), 0, 0, 0, 0, dt.timezone.utc) #Veröffentlichungsdatum laut Anfang
        while DT_publishion.strftime("%d")!=info[0:2]:                                                          #solange Tag nicht stimmt, also wenn nach Met Report Time nochmal aktualisiert :
            DT_publishion-=dt.timedelta(days=1)                                                                 #Tag abziehen
        DT_publishion+=dt.timedelta(hours=int(info[2:4]), minutes=int(info[4:6]))                               #Berichtsuhrzeit laut Tag-Zeit-Gruppe

        if force_print==True:                                                   #wenn Ausgabe erzwungen:
            timespan_published=dt.datetime.now(dt.timezone.utc)-DT_publishion   #Zeitspanne veröffentlicht
            info=f"{DT_publishion.strftime('%Y-%m-%dT%H:%M')} ({KFS.fstr.notation_tech(timespan_published.total_seconds(), 2)}s ago)"
        else:                                                                   #wenn Abonnement:
            info=f"{DT_publishion.strftime('%Y-%m-%dT%H:%M')}"                  #ohne Zeitspanne veröffentlicht

        return " "+info