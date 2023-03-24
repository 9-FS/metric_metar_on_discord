import datetime as dt
import inspect
import KFS
import logging
import numpy        #for crosswind component, numpy unctions because of DataFrames input
import pandas
import re
from weather_minimums import WEATHER_MIN


def change_format_USA_codes(info: str, met_report_DT: dt.datetime, station: dict, RWY_DB: pandas.DataFrame) -> str|None:
    re_match: re.Match|None

    WMO_CLOUD_TYPE_LOW={
        "0": ("-",             False),  #nothing
        "1": ("CU",            False),  #cumulus
        "2": ("CU-CON",        False),  #cumulus congestus
        "3": ("CB-CAL",        True),   #cumulonimbus calvus
        "4": ("SC",            False),  #stratocumulus
        "5": ("SC",            False),  #stratocumulus
        "6": ("ST,ST-FRA",     True),   #stratus or stratus fractus
        "7": ("CU-FRA,ST-FRA", True),   #cumulus fractus, stratus fractus
        "8": ("CU,SC",         False),  #cumulus, stratocumulus
        "9": ("CB",            True),   #cumulonimbus
        "/": ("-",             False)   #nothing
    }

    WMO_CLOUD_TYPE_MIDDLE={
        "0": ("-",        False),   #nothing
        "1": ("AS-HUM",   False),   #altostratus humilis
        "2": ("AS-CON",   False),   #altostratus congestus
        "3": ("AC-HUM",   False),   #altocumulus humilis
        "4": ("AC",       False),   #altocumulus
        "5": ("AC-CON",   False),   #altocumulus congestus
        "6": ("AC",       False),   #altocumulus
        "7": ("AC,AS,NS", False),   #altocumulus, altostratus, nimbostratus
        "8": ("AC-CAS",   False),   #altocumulus castellanus
        "9": ("AC-FRA",   False),   #altostratus fractus
        "/": ("ABV-OVC",  False)    #above overcast layer
    }

    WMO_CLOUD_TYPE_HIGH={
        "0": ("-",               False),    #nothing
        "1": ("CI-HUM",          False),    #cirrus humilis
        "2": ("CI",              False),    #cirrus
        "3": ("CI-CAP",          False),    #CB, part capillatus CI
        "4": ("CI-CON",          False),    #cirrus congestus
        "5": ("CI:LOW,CS:LOW",   False),    #cirrus low altitude, cirrostratus low altitude
        "6": ("CI:HIGH,CS:HIGH", False),    #cirrus high altitude, cirrostratus high altitude
        "7": ("CS:OVC",          False),    #cirrostratus overcast sky
        "8": ("CS",              False),    #cirrostratus partial sky
        "9": ("CC,CI,CS",        False),    #cirrocumulus, cirrus, cirrostratus
        "/": ("ABV-OVC",         False)     #above overcast layer
    }

        
    #USA: peak wind
    re_match=re.search("^(?P<wind_direction>[0-3][0-9]{2})(?P<wind_speed>[0-9]{2})/(?P<hour>[0-2][0-9])(?P<minute>[0-5][0-9])$", info)
    if re_match!=None:
        bold: bool
        CWC: list=[]                                                            #across all runways, crosswind component
        event_DT: dt.datetime
        info_new: str
        RWY: pandas.DataFrame=RWY_DB[RWY_DB["airport_ident"]==station["ICAO"]]  #in aerodrome all runways
        wind_direction: int=int(re_match.groupdict()["wind_direction"])%360     #keep in [0; 360[
        wind_speed: float=float(re_match.groupdict()["wind_speed"])*KFS.convert_to_SI.speed["kt"]

        event_DT=met_report_DT                                          #event date, initialised with met report datetime
        while event_DT.strftime("%M")!=re_match.groupdict()["minute"]:  #as long as minutes not matching:
            event_DT-=dt.timedelta(minutes=1)                           #event must be before met report datetime, decrement minute until same
        while event_DT.strftime("%H")!=re_match.groupdict()["hour"]:    #as long as hours not matching:
            event_DT-=dt.timedelta(hours=1)                             #event must be before met report datetime, decrement hour until same


        if   met_report_DT.strftime("%Y-%m-%d")==event_DT.strftime("%Y-%m-%d"): #if date still same:
            info_new=f"{event_DT.strftime('%H:%M')}"                            #time
        elif met_report_DT.strftime("%Y-%m")==event_DT.strftime("%Y-%m"):       #if year and month still same:
            info_new=f"{event_DT.strftime('%dT%H:%M')}"                         #day, hour, minute
        elif met_report_DT.strftime("%Y")==event_DT.strftime("%Y"):             #if year still same:
            info_new=f"{event_DT.strftime('%m-%dT%H:%M')}"                      #month, day, hour
        else:                                                                   #nothing same:
            info_new=f"{event_DT.strftime('%Y-%m-%dT%H:%M')}"                   #full datetime

        info_new+=f"/{KFS.fstr.notation_abs(wind_direction, 0, round_static=True, width=3)}°{KFS.fstr.notation_abs(wind_speed, 0, round_static=True, width=2)}m/s"


        if RWY.empty==True: #if no runways found: assume direct crosswind
            CWC.append(wind_speed)
        else:   #if runways found: for each runway calculate crosswind components
            CWC+=abs(numpy.sin(numpy.radians(wind_direction-RWY["le_heading_degT"]))*wind_speed).dropna().tolist()  #sin(direction difference)*wind speed, abs, remove NaN, convert to list #type:ignore
        for i in range(len(CWC)):
            if CWC[i]<=WEATHER_MIN["CWC"]:  #if at least 1 CWC below maximum:
                bold=False                  #landable
                break
        else:   #if all CWC above maximum:
            bold=True

        if WEATHER_MIN["wind"]<wind_speed:  #if despite landable crosswind component overall wind just too strong:
            bold=True

        if bold==True:
            info_new=f"**{info_new}**"
        return f" {info_new}"
    

    #USA: weather begin or end at time
    re_match=re.search("^((?P<weather>[+-]?([A-Z][A-Z])+)(?P<change_type>[BE])(?P<hour>([0-9]{2})?)(?P<minute>[0-9]{2}))$", info)
    if re_match!=None:
        change_type: str
        event_DT: dt.datetime
        info_new: str

        event_DT=met_report_DT                                          #event date, initialised with met report datetime
        while event_DT.strftime("%M")!=re_match.groupdict()["minute"]:  #as long as minutes not matching:
            event_DT-=dt.timedelta(minutes=1)                           #event must be before met report datetime, decrement minute until same
        if re_match.groupdict()["hour"]!="":
            while event_DT.strftime("%H")!=re_match.groupdict()["hour"]:    #as long as hours not matching:
                event_DT-=dt.timedelta(hours=1)                             #event must be before met report datetime, decrement hour until same


        change_type=re_match.groupdict()["change_type"]
        if change_type=="B":
            info_new="FM"
        elif change_type=="E":
            info_new="TL"
        else:
            logging.critical(f"Weather change type is neither \"B\" (began), nor \"E\" (ended), but \"{change_type}\".")
            raise RuntimeError(f"Error in {change_format_USA_codes.__name__}{inspect.signature(change_format_USA_codes)}: Weather change type is neither \"B\" (began), nor \"E\" (ended), but \"{change_type}\".")

        if   met_report_DT.strftime("%Y-%m-%d")==event_DT.strftime("%Y-%m-%d"): #if date still same:
            info_new+=f"{event_DT.strftime('%H:%M')}"                           #time
        elif met_report_DT.strftime("%Y-%m")==event_DT.strftime("%Y-%m"):       #if year and month still same:
            info_new+=f"{event_DT.strftime('%dT%H:%M')}"                        #day, hour, minute
        elif met_report_DT.strftime("%Y")==event_DT.strftime("%Y"):             #if year still same:
            info_new+=f"{event_DT.strftime('%m-%dT%H:%M')}"                     #month, day, hour
        else:                                                                   #nothing same:
            info_new+=f"{event_DT.strftime('%Y-%m-%dT%H:%M')}"                  #full datetime

        info_new+=f"/{re_match.groupdict()['weather']}"
        
        return info_new


    #USA code PWE: precipitation water equivalent
    re_match=re.search("^P(?P<PWE>[0-9]{4})$", info)
    if re_match!=None:
        PWE=int(re_match.groupdict()["PWE"])/100*KFS.convert_to_SI.length["in"]
        return f" PWE/{KFS.fstr.notation_tech(PWE, 2)}m"
    

    #USA code T: temperature and dewpoint
    re_match=re.search("^T(?P<temperature>[0-1][0-9]{3})(?P<dewpoint>[0-1][0-9]{3})$", info)
    if re_match!=None:
        dewpoint: str
        info_new: str
        temperature: str

        temperature=re_match.groupdict()["temperature"]
        temperature=f"{temperature[:3]},{temperature[3:]}"  #add decimal separator
        if temperature[0]=="0":                             #if sign positive: cut
            temperature=temperature[1:]
        elif temperature[0]=="1":                           #if sign negative: replace
            temperature=temperature.replace("1", "-", 1)
        
        dewpoint=re_match.groupdict()["dewpoint"]
        dewpoint=f"{dewpoint[:3]},{dewpoint[3:]}"
        if dewpoint[0]=="0":                                #if sign positive: cut
            dewpoint=dewpoint[1:]
        elif dewpoint[0]=="1":                              #if sign negative: replace
            dewpoint=dewpoint.replace("1", "-", 1)
        

        if dewpoint=="":
            info_new=f"{temperature}°C"
        else:
            info_new=f"{temperature}°C/{dewpoint}°C"
        
        if ("temp_min" in WEATHER_MIN and float(temperature.replace(",", "."))<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<float(temperature.replace(",", "."))):    #if temperature outside limits: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"


    #USA code 1 and 2: 22ks (6h) temperature max. or min.
    re_match=re.search("^(?P<temperature_type>[1-2])(?P<temperature>[0-1][0-9][0-9][0-9])$", info)
    if re_match!=None:
        bold: bool
        info_new: str=""
        temperature_type: str=re_match.groupdict()["temperature_type"]

        if   temperature_type=="1": #replace temperature type code with readable abbreviation
            temperature_type="TX6h"
        elif temperature_type=="2":
            temperature_type="TN6h"
        else:
            logging.critical(f"Temperature type shoud be in [1; 2], but it is {temperature_type}.")
            raise RuntimeError(f"Error in {change_format_USA_codes.__name__}{inspect.signature(change_format_USA_codes)}: Temperature type shoud be in [1; 2], but it is {temperature_type}.")

        temperature=re_match.groupdict()["temperature"]
        temperature=f"{temperature[:3]},{temperature[3:]}"  #add decimal separator
        if temperature[0]=="0":                             #if sign positive: cut
            temperature=temperature[1:]
        elif temperature[0]=="1":                           #if sign negative: replace
            temperature=temperature.replace("1", "-", 1)


        info_new=f"{temperature_type}/{temperature}°C"
        
        if ("temp_min" in WEATHER_MIN and float(temperature.replace(",", "."))<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<float(temperature.replace(",", "."))):    #if temperature outside limits: mark
            info_new=f"**{info_new}**"
        return f" {info_new}"


    #USA code 4/: snow depth
    re_match=re.search("^4/(?P<snow_depth>[0-9]{3})$", info)
    if re_match!=None:
        snow_depth: float=int(re_match.groupdict()["snow_depth"])*KFS.convert_to_SI.length["in"]
        info_new: str


        info_new=f"SNOW/{KFS.fstr.notation_tech(snow_depth, 2)}m"
        
        if 0<snow_depth:
            info_new=f"**{info_new}**"
        return f" {info_new}"


    #USA code 4: 86ks (1d) temperature max. and min.
    re_match=re.search("^4(?P<temperature_max>[0-1][0-9]{3})(?P<temperature_min>[0-1][0-9]{3})$", info)
    if re_match!=None:
        info_new: str=""
        temperature_max: str
        temperature_min: str

        temperature_max=re_match.groupdict()["temperature_max"]
        temperature_max=f"{temperature_max[:3]},{temperature_max[3:]}"  #add decimal separator
        if temperature_max[0]=="0":     #if sign positive: cut
            temperature_max=temperature_max[1:]
        elif temperature_max[0]=="1":   #if sign negative: replace
            temperature_max=temperature_max.replace("1", "-", 1)
        
        temperature_min=re_match.groupdict()["temperature_min"]
        temperature_min=f"{temperature_min[:3]},{temperature_min[3:]}"
        if temperature_min[0]=="0":     #if sign positive: cut
            temperature_min=temperature_min[1:]
        elif temperature_min[0]=="1":   #if sign negative: replace
            temperature_min=temperature_min.replace("1", "-", 1)
        

        if ("temp_min" in WEATHER_MIN and int(temperature_max)<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<int(temperature_max)):    #if temperature outside limits: mark
            info_new+=f"**TX24h/{temperature_max}°C**"
        else:
            info_new+=f"TX24h/{temperature_max}°C"
        
        if ("temp_min" in WEATHER_MIN and int(temperature_min)<WEATHER_MIN["temp_min"]) or ("temp_max" in WEATHER_MIN and WEATHER_MIN["temp_max"]<int(temperature_min)):    #if temperature outside limits: mark
            info_new+=f" **TN24h/{temperature_min}°C**"
        else:
            info_new+=f" TN24h/{temperature_min}°C"
        
        return f" {info_new}"
        

    #USA code 5: 11ks (3h) pressure trend
    re_match=re.search("^5(?P<trend_direction>[0-8])(?P<pressure_change>[0-9]{3})$", info)
    if re_match!=None:
        info_new: str
        pressure_change: float=int(re_match.groupdict()["pressure_change"])*10
        trend_direction: str

        trend_direction=re_match.groupdict()["trend_direction"]
        if 0<=int(trend_direction) and int(trend_direction)<=3: #convert trend direction to sign
            trend_direction="+"
        elif int(trend_direction)==4:
            trend_direction=""
        elif 5<=int(trend_direction) and int(trend_direction)<=8:
            trend_direction="-"
        else:
            logging.critical(f"Pressure trend direction is not in [0; 8], but \"{trend_direction}\".")
            raise RuntimeError(f"Error in {change_format_USA_codes.__name__}{inspect.signature(change_format_USA_codes)}: Pressure trend direction is not in [0; 8], but \"{trend_direction}\".")


        info_new=f"ΔPRES3h/{trend_direction}{KFS.fstr.notation_tech(pressure_change, -1, round_static=True)}Pa"
        
        return f" {info_new}"


    #USA code 6: in 11ks (3h) or 22ks (6h) precipitation amount
    re_match=re.search("^6(?P<precipitation>[0-9]{4})$", info)
    if re_match!=None:
        precipitation: float=float(re_match.groupdict()["precipitation"])/100*KFS.convert_to_SI.length["in"]
        
        
        return f" PCPN(3h,6h)/{KFS.fstr.notation_tech(precipitation, 2)}m"


    #USA code 7: in 86ks (24h) precipitation amount
    re_match=re.search("^7(?P<precipitation>[0-9]{4})$", info)
    if re_match!=None:
        precipitation: float=float(re_match.groupdict()["precipitation"])/100*KFS.convert_to_SI.length["in"]


        return f" PCPN24h/{KFS.fstr.notation_tech(precipitation, 2)}m"


    #USA code 8/: cloud type
    re_match=re.search("^8/(?P<cloud_type_low>[0-9])(?P<cloud_type_medium>[0-9/])(?P<cloud_type_high>[0-9/])$", info)
    if re_match!=None:
        cloud_type_high: str  =WMO_CLOUD_TYPE_HIGH  [re_match.groupdict()["cloud_type_high"]]
        cloud_type_high_bold: bool
        cloud_type_low: str   =WMO_CLOUD_TYPE_LOW   [re_match.groupdict()["cloud_type_low"]]
        cloud_type_low_bold: bool
        cloud_type_medium: str=WMO_CLOUD_TYPE_MIDDLE[re_match.groupdict()["cloud_type_medium"]]
        cloud_type_medium_bold: bool
        info_new: str
        
        try:
            cloud_type_low,    cloud_type_low_bold   =WMO_CLOUD_TYPE_LOW   [re_match.groupdict()["cloud_type_low"]]
        except KeyError:
            cloud_type_low,    cloud_type_low_bold=("-", False)
        try:
            cloud_type_medium, cloud_type_medium_bold=WMO_CLOUD_TYPE_MIDDLE[re_match.groupdict()["cloud_type_medium"]]
        except KeyError:
            cloud_type_medium, cloud_type_medium_bold=("-", False)
        try:
            cloud_type_high,   cloud_type_high_bold  =WMO_CLOUD_TYPE_HIGH  [re_match.groupdict()["cloud_type_high"]]
        except KeyError:
            cloud_type_high,   cloud_type_high_bold=("-", False)
        

        info_new=f"CLOUDS/{cloud_type_low}/{cloud_type_medium}/{cloud_type_high}"

        if cloud_type_low_bold==True or cloud_type_medium_bold==True or cloud_type_high_bold==True:
            info_new=f"**{info_new}**"
        return f" {info_new}"


    #USA code 98: sunshine duration
    re_match=re.search("^98(?P<sunshine_duration>[0-9]{3})$", info)
    if re_match!=None:
        sunshine_duration: int=int(re_match.groupdict()["sunshine_duration"])*KFS.convert_to_SI.time["min"]
        return f" SUN/{KFS.fstr.notation_tech(sunshine_duration, 2)}s"
    

    #USA code 931: in 22ks (6h) snowfall
    re_match=re.search("^931(?P<snowfall>[0-9]{3})$", info)
    if re_match!=None:
        snowfall: float=int(re_match.groupdict()["snowfall"])/10*KFS.convert_to_SI.length["in"]
        
        
        info_new=f"SNOW6h/{KFS.fstr.notation_tech(snowfall, 2)}m"
        
        if 0<snowfall:
            info_new=f"**{info_new}**"
        return f" {info_new}"


    #USA code 933: snow liquid water equivalent (SWE)
    re_match=re.search("^933(?P<SWE>[0-9]{3})$", info)
    if re_match!=None:
        SWE: float=int(re_match.groupdict()["SWE"])/10*KFS.convert_to_SI.length["in"]
        
        
        info_new=f"SWE/{KFS.fstr.notation_tech(SWE, 2)}m"
        
        if 0<SWE:
            info_new=f"**{info_new}**"
        return f" {info_new}"