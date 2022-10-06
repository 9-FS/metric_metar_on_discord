import concurrent.futures
import pandas as pd     #Dataframes
from KFS import KFSfstr #Notation technisch
from KFS import KFSlog  #KFSlog


async def airport_info(station, station_name, station_elev, frequency_DB, navaid_DB, RWY_DB, message):
    freq=frequency_DB[frequency_DB["airport_ident"]==station].reset_index(drop=True)    #Frequenzen relevant
    freq_info=""                                                                        #Frequenzinformationen zu schicken
    message_send=""                                                                     #Nachricht final an Discord
    nav=navaid_DB[navaid_DB["associated_airport"]==station].reset_index(drop=True)      #Funknavigationshilfen relevant
    nav_info=""                                                                         #Funknavigationshilfsinformationen zu schicken
    RWY=RWY_DB[RWY_DB["airport_ident"]==station].reset_index(drop=True)                 #Pisten relevant
    RWY_info=["", "", "", ""]   #Pisteninformationen zu schicken, [0]: Pisten mit Name<=18, [1]: Pisten mit 18<Name, [2]: Pisten geschlossen mit Name<=18, [3]: Pisten geschlossen mit 18<Name, 
    

    if station_name=="":                                                #wenn Station in Datenbank nicht gefunden:
        KFSlog.write("Station could not be found in airport database.")
        await message.channel.send("Station could not be found in airport database.")
        

    #Pisteninformationen zusammenstellen
    KFSlog.write("Generating runway information...")
    for i in RWY.index:
        RWY_info_i=0    #Infoindex, [0]: Pisten offen, [1]: Pisten geschlossen

        if RWY["closed"][i]==1:                                                     #wenn Piste geschlossen:
            RWY_info_i=1
            RWY_info[RWY_info_i]+="*CLOSED* "
        
        if(    pd.isna(RWY["le_ident"][i])==False                 and pd.isna(RWY["he_ident"][i])==False                    #wenn beide Pistennamen gegeben
           and pd.isna(RWY["le_displaced_threshold_ft"][i])==True and pd.isna(RWY["he_displaced_threshold_ft"][i])==True):  #und keine Pistenschwelle versetzt:
            RWY_info[RWY_info_i]+=f"{RWY['le_ident'][i].upper()}/{RWY['he_ident'][i].upper()}"                              #beiden Pisten in 1 Eintrag
            if pd.isna(RWY["length_ft"][i])==False:
                RWY_info[RWY_info_i]+=f": {KFSfstr.notation_tech(int(RWY['length_ft'][i])*0.3048, 2)}m"    #Pistenlänge
            if pd.isna(RWY["width_ft"][i])==False:
                RWY_info[RWY_info_i]+=f" • {KFSfstr.notation_tech(int(RWY['width_ft'][i])*0.3048, 2)}m"    #Pistenbreite
            if pd.isna(RWY["surface"][i])==False:
                RWY_info[RWY_info_i]+=f", {RWY['surface'][i].upper()}"                      #Pistenoberfläche
            if pd.isna(RWY["lighted"][i])==False and RWY["lighted"][i]==0:                  #wenn nicht beleuchtet:
                RWY_info[RWY_info_i]+=f", NO LIGHTS"                                        #Warnung
            RWY_info[RWY_info_i]+="\n"
        else:                                                                               #beide Pisten in Einträgen getrennt
            if pd.isna(RWY["le_ident"][i])==False:
                RWY_info[RWY_info_i]+=f"{RWY['le_ident'][i].upper()}"                       #Pistenname
            else:
                continue
            if pd.isna(RWY["length_ft"][i])==False:
                RWY_info[RWY_info_i]+=f": {KFSfstr.notation_tech(int(RWY['length_ft'][i])*0.3048, 2)}m"  #Pistenlänge
            if pd.isna(RWY["le_displaced_threshold_ft"][i])==False:                                                                     #wenn Schwelle versetzt vorhanden:
                RWY_info[RWY_info_i]+=f" ({KFSfstr.notation_tech((int(RWY['length_ft'][i])-int(RWY['le_displaced_threshold_ft'][i]))*0.3048, 2)}m)"  #LDA
            if pd.isna(RWY["width_ft"][i])==False:
                RWY_info[RWY_info_i]+=f" • {KFSfstr.notation_tech(int(RWY['width_ft'][i])*0.3048, 2)}m"  #Pistenbreite
            if pd.isna(RWY["surface"][i])==False:
                RWY_info[RWY_info_i]+=f", {RWY['surface'][i].upper()}"                      #Pistenoberfläche
            if pd.isna(RWY["lighted"][i])==False and RWY["lighted"][i]==0:                  #wenn nicht beleuchtet:
                RWY_info[RWY_info_i]+=f", NO LIGHTS"                                        #Warnung
            RWY_info[RWY_info_i]+="\n"

            if RWY["closed"][i]==1:                                                         #wenn Piste geschlossen:
                RWY_info[RWY_info_i]+="*CLOSED* "                                           #bei zweiter Piste auch eintragen

            if pd.isna(RWY["he_ident"][i])==False:
                RWY_info[RWY_info_i]+=f"{RWY['he_ident'][i].upper()}"                       #Pistenname
            else:
                continue
            if pd.isna(RWY["length_ft"][i])==False:
                RWY_info[RWY_info_i]+=f": {KFSfstr.notation_tech(int(RWY['length_ft'][i])*0.3048, 2)}m"  #Pistenlänge
            if pd.isna(RWY["he_displaced_threshold_ft"][i])==False:                                                                     #wenn Schwelle versetzt vorhanden:
                RWY_info[RWY_info_i]+=f" ({KFSfstr.notation_tech((int(RWY['length_ft'][i])-int(RWY['he_displaced_threshold_ft'][i]))*0.3048, 2)}m)"  #LDA
            if pd.isna(RWY["width_ft"][i])==False:
                RWY_info[RWY_info_i]+=f" • {KFSfstr.notation_tech(int(RWY['width_ft'][i])*0.3048, 2)}m"  #Pistenbreite
            if pd.isna(RWY["surface"][i])==False:
                RWY_info[RWY_info_i]+=f", {RWY['surface'][i].upper()}"                      #Pistenoberfläche
            if pd.isna(RWY["lighted"][i])==False and RWY["lighted"][i]==0:                  #wenn nicht beleuchtet:
                RWY_info[RWY_info_i]+=f", NO LIGHTS"                                        #Warnung
            RWY_info[RWY_info_i]+="\n"
    
    RWY_info=RWY_info[0]+RWY_info[1]
    KFSlog.write("\rRunway information generated.")
    KFSlog.write(RWY_info)


    #Frequenzinformationen zusammenstellen
    KFSlog.write("Generating frequency information...")
    for i in freq.index:
        if pd.isna(freq["frequency_mhz"][i])==True: #wenn Frequenz nicht vorhanden:
            continue                                #Eintrag überspringen
        if pd.isna(freq["type"][i])==False:
            freq_info+=f"{freq['type'][i].upper()}" #Dienstleistungstyp
        #if pd.isna(Freq["description"][i])==False and Freq['type'][i]!=Freq['description'][i]:  #wenn Beschreibung vorhanden und ungleich Typ:
        #    Freq_Info+=f"/{Freq['description'][i]}" #zusätzlich Dienstleistungsbeschreibung (Name)
        freq_info+=f": {KFSfstr.notation_tech(float(freq['frequency_mhz'][i])*1e6, -3, round_static=True, trailing_zeros=False)}Hz\n"
    KFSlog.write("\rFrequency information generated.")
    KFSlog.write(freq_info)


    #Funknavigationhilfsinformationen zusammenstellen
    KFSlog.write("Generating navaid information...")
    for i in nav.index:
        if pd.isna(nav["frequency_khz"][i])==True:  #wenn Frequenz nicht vorhanden:
            continue                                #Eintrag überspringen
        if pd.isna(nav["type"][i])==False:
            nav_info+=f"{nav['type'][i].upper()} "
        if pd.isna(nav["name"][i])==False:
            nav_info+=f"{nav['name'][i]}"
        if pd.isna(nav["ident"][i])==False:
            nav_info+=f" ({nav['ident'][i].upper()})"
        nav_info+=f": {KFSfstr.notation_tech(float(nav['frequency_khz'][i])*1e3, -3, round_static=True, trailing_zeros=False)}Hz\n"
    KFSlog.write("\rNavaid information generated.")
    KFSlog.write(nav_info)


    #Nachrichten schicken
    if station_name!="":                                                                        #wenn Flughafenname vorhanden:
        message_send+=f"{station_name}\n----------\n"                                           #Flughafenname schicken
    else:
        message_send+="Station could not be found in airport database.\n----------\n"
    if RWY_info!="":
        message_send+=f"```{RWY_info}```\n----------\n"                                         #Flughafeninformationen schicken
    else:
        message_send+="Runways could not be found.\n----------\n"
    if freq_info!="":
        message_send+=f"```{freq_info}```\n----------\n"                                        #Frequenzinformationen schicken
    else:
        message_send+="Frequencies could not be found.\n----------\n"
    if nav_info!="":
        message_send+=f"```{nav_info}```\n----------\n"                                         #Funknavigationshilfsinformationen schicken
    else:
        message_send+="Navaids could not be found.\n----------\n"
    if station_elev!=None:                                                                      #wenn Flughafenhöhe vorhanden:
        message_send+=f"```Elevation={station_elev:,.0f}m```\n----------\n".replace(",", ".")   #Station_Elev zur Kontrolle auch schicken
    if RWY_info!="" or freq_info!="" or nav_info!="":                                           #wenn was geschickt wurde: Hinweis
        message_send+="Do not use for flight operations! Data source is inofficial (https://ourairports.com/data/)."

    await message.channel.send(message_send)    #Nachricht an Discord abschicken
    KFSlog.write("Runways, frequencies, navaids, and elevation sent.")
    return