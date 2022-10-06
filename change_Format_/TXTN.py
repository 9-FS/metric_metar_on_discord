import datetime
import re   #Regular Expressions


def change_format_TXTN(info, date):
    if re.search("^T[XN][0-9][0-9]/[0-3][0-9][0-2][0-9]Z$", info)!=None:
        DT=datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), 0, 0) #Eventdatum, initialisiert mit Veröffentlichungsdatum
        while DT.strftime("%d")!=info[5:7]:                                         #solange Eventtag nicht stimmt:
            DT+=datetime.timedelta(days=1)                                          #Tag hinzufügen
        DT+=datetime.timedelta(hours=int(info[7:9]))                                #zu Evenntdatum Uhrzeit hinzufügen

        #Info=f"T{Info[1]}{DT.strftime('%Y-%m-%dT%H:00')}/{Info[2:4]}°C"
        info=f"T{info[1]}{DT.strftime('%dT%H')}/{info[2:4]}°C"
        return " "+info

    if re.search("^T[XN]M[0-9][0-9]/[0-3][0-9][0-2][0-9]Z$", info)!=None:
        DT=datetime.datetime(int(date[0:4]), int(date[5:7]), int(date[8:10]), 0, 0) #Eventdatum, initialisiert mit Veröffentlichungsdatum
        while DT.strftime("%d")!=info[6:8]:                                         #solange Starttag nicht stimmt:
            DT+=datetime.timedelta(days=1)                                          #Tag hinzufügen
        DT+=datetime.timedelta(hours=int(info[8:10]))                               #zu Evenntdatum Uhrzeit hinzufügen

        #Info=f"T{Info[1]}{DT.strftime('%Y-%m-%dT%H:00')}/-{Info[3:5]}°C"
        info=f"T{info[1]}{DT.strftime('%dT%H')}/-{info[3:5]}°C"
        return " "+f"**{info}**"