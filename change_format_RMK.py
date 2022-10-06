from change_Format_.HGT                  import change_Format_HGT
from change_Format_.QNH                  import change_format_QNH
from change_Format_.temp_dew             import change_format_temp_dew
from change_Format_.USA_codes            import change_format_USA_codes
from change_Format_.visibility_vertical  import change_format_VV
from change_Format_.wind                 import change_format_wind


def change_Format_RMK(info_list, i, station, station_elev, date, RWY_DB):
    if info_list[i]=="":    #wenn Info leer, kann vorkommen bei TAF weil mehrere Leerzeichen hintereinander
        return ""           #String leer zurück


    info_new=change_format_wind     (info_list[i], station, RWY_DB) #Wind
    if info_new!=None:
        return info_new

    info_new=change_format_temp_dew (info_list[i])                   #Temperatur und Taupunkt
    if info_new!=None:
        return info_new

    info_new=change_format_QNH      (info_list[i])                  #QNH, als Zusatz in Einheit anderer schon gesehen (Bsp. RCTP)
    if info_new!=None:
        return info_new

    info_new=change_Format_HGT      (info_list[i], station_elev)    #Höhe, Bsp Windänderungshöhe
    if info_new!=None:
        return info_new

    #in RMK 4 Ziffern können unterschiedliche Sachen bedeuten: Uhrzeit, QNH, ... wird daher unverändert weitergeleitet
    ###if re.search("^[0-2][0-9][0-5][0-9]$", Info)!=None:
        ###return " "+Info

    info_new=change_format_VV       (info_list[i])                  #Sicht vertikal
    if info_new!=None:
        return info_new

    info_new=change_format_USA_codes(info_list[i], date)            #USA Wetterstationcodes
    if info_new!=None:
        return info_new

    return " "+info_list[i]  #wenn Format nicht gefunden: einfach weiterleiten