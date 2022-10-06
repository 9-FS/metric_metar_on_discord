from change_Format_.change               import change_format_change
from change_Format_.clouds               import change_format_clouds
from change_Format_.QNH                  import change_format_QNH
from change_Format_.runway_state_message import change_format_RSM
from change_Format_.RVR                  import change_format_RVR
from change_Format_.temp_dew             import change_format_temp_dew
from change_Format_.time                 import change_format_time
from change_Format_.TXTN                 import change_format_TXTN
from change_Format_.USA_codes            import change_format_USA_codes
from change_Format_.validity             import change_format_validity
from change_Format_.visibility           import change_format_vis
from change_Format_.visibility_vertical  import change_format_VV
from change_Format_.weather              import change_format_weather
from change_Format_.wind                 import change_format_wind


def change_format(info_list, i, station, station_elev, date, RWY_DB, force_print):
    if info_list[i]=="":    #wenn Info aktuell leer, kann vorkommen weil bei TAF Leerzeichen mehrere manchmal hintereinander
        return ""           #String leer zurück


    #Station einfach weiterleiten

    info_new=change_format_time    (info_list[i], date, force_print)        #Zeitpunkt
    if info_new!=None:
        return info_new

    info_new=change_format_wind    (info_list[i], station, RWY_DB)          #Wind
    if info_new!=None:
        return info_new

    info_new=change_format_vis     (info_list, i)                           #Sicht
    if info_new!=None:
        return info_new

    info_new=change_format_RVR     (info_list[i])                           #RVR
    if info_new!=None:
        return info_new

    info_new=change_format_weather (info_list, i)                           #Wetter, nur Wetter gefährlich markieren
    if info_new!=None:
        return info_new

    info_new=change_format_clouds  (info_list[i], station_elev)             #Wolken, Wolkenhöhe in MSL [m]
    if info_new!=None:
        return info_new

    info_new=change_format_VV      (info_list[i])                           #Sicht vertikal
    if info_new!=None:
        return info_new

    info_new=change_format_temp_dew (info_list[i])                          #Temperatur und Taupunkt
    if info_new!=None:
        return info_new

    info_new=change_format_QNH     (info_list[i])                           #QNH
    if info_new!=None:
        return info_new

    info_new=change_format_RSM     (info_list[i])                           #Pistenzustand, Runway State Message
    if info_new!=None:
        return info_new

    info_new=change_format_change  (info_list, i, date)                     #TREND & TAF: Veränderung
    if info_new!=None:
        return info_new

    info_new=change_format_validity(info_list[i], date)                     #TAF: Validitätszeitspanne
    if info_new!=None:
        return info_new

    info_new=change_format_TXTN    (info_list[i], date)                     #TAF: Tagestemperatur max und min
    if info_new!=None:
        return info_new

    info_new=change_format_USA_codes(info_list[i], date, station, RWY_DB)   #USA Wetterstationcodes
    if info_new!=None:
        return info_new

    return " "+info_list[i] #wenn Format nicht gefunden: einfach weiterleiten