WEATHER_MIN={
    "ceiling": 1500*0.3048,                                                 #Hauptwolkenuntergrenze min. AGL 1.500ft (460m)
    "CWC": 20*0.5144444,                                                    #! Seitenwindkomponente max. 20kt (10m/s)
    "QNH_min": 95e3,                                                        #QNH min. wegen Höhenmesseinstellung
    "QNH_max": 105e3,                                                       #QNH max. wegen Höhenmesseinstellung
    "RVR": 5e3,                                                             #Sicht min. 5km
    "temp_min": -20,                                                        #Temperatur min. wegen Leistungstabellen und Vereisungsbedingungen
    "temp_max": 50,                                                         #Temperatur max. wegen Leistungstabellen
    "TWC": 10*0.5144444,                                                    #! Rückenwindkomponente max. 10kt (5m/s)
    "USA_vis": 3*1609.344,                                                  #in USA Sicht min. 3SM (4,8km)
    "vis": 5e3,                                                             #Sicht min. 5km
    "weather_forbidden": "BR|DS|FC|FG|FZ|GR|GS|HZ|IC|PL|SG|SN|SQ|SS|TS|VA", #bei dem Wetter nich fliegen, Sicht, Vereisung, Stürme etc
    "wind": 30*0.5144444                                                    #! Windstärke max. allgemein 40kt (20m/s)
}

# Ausrufezeichen bedeutet nicht deaktivierbar
"""
Existiert, weil es keine Ausweichlogik bei den Minima gibt. Bedeutet z.B. Wind VRB nimmt immer Wind als Rückenwind an und
benutzt dementsprechend auch TWC-Maximum. Wenn nur TWC-Markierung ausgeschaltet wird, weicht er nicht aus auf das nächst
höhere Windmaximum, sondern markiert gar keine Wind VRB mehr, das ist ungewünscht.
"""