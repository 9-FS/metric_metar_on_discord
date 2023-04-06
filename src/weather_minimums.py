#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import KFS.convert_to_SI


WEATHER_MIN={
    "ceiling":           1500*KFS.convert_to_SI.length["ft"],               #cloud ceiling height min. AGL 1.500ft (460m)
    "CWC":                 20*KFS.convert_to_SI.speed["kt"],                #! crosswind component
    "QNH_min":             95e3,                                            #QNH min. because possible altimeter setting
    "QNH_max":            105e3,                                            #QNH max. because possible altimeter setting
    "RVR":                  5e3,                                            #visibility min. 5km
    "temp_min":           -20,                                              #temperature min. because performance and icing
    "temp_max":            50,                                              #temperatur max. because performance
    "TWC":                 10*KFS.convert_to_SI.speed["kt"],                #! tailwind component max.
    "USA_vis":              3*KFS.convert_to_SI.length["SM"],               #in USA visibility min. 3SM (4,8km)
    "vis":                  5e3,                                            #visibility min. 5km
    "weather_forbidden": "BR|DS|FC|FG|FZ|GR|GS|HZ|IC|PL|SG|SN|SQ|SS|TS|VA", #do not fly during this weather; visibility, icing, storms...
    "wind":                40*KFS.convert_to_SI.speed["kt"]                 #! wind max. in general
}
"""
weather minimums, if exceeded mark
"""
#no docstring in dict, because docstring implicity combines with first key

#Exclamation mark means do not deactivate.
"""
Exists because there is no fallback logic for minimums.
Means for example wind VRB always assumes tailwind and uses tailwind limitation for marking.
If only tailwind limitation is deactivated, does not fallback to the next higher wind limitation like crosswind limitation,
but instead just does not mark any wind VRB anymore, which is undesired.
"""