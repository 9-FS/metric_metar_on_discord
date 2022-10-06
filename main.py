from email import message
import discord                          #Discord
from discord.ext import tasks           #Discord Event Scheduler
import datetime as dt                   #für Zeitpunkt aktuell
import pandas as pd                     #Dataframes
import re                               #Regular Expressions, für Formatsuch
import requests                         #HTTP Zeuch Exceptions
from airport_info  import airport_info  #Flughafeninformationsbefehl
from init_DB       import init_DB       #Datenbanken herunterladen oder aus Datei laden
from KFS           import KFSlog           #Debug-KFSlog statt print
from process_METAR import process_METAR #METAR herunterladen und konvertieren
from process_TAF   import process_TAF   #TAF herunterladen und konvertieren


#behalten über Laufzeit ganze
airport_DB=pd.DataFrame()                                                   #Flughafendatenbank
client=discord.Client()                                                     #Discord-Client
country_DB=pd.DataFrame()                                                   #Länderdatenbank für Ländernamen
DT_DB_last_updated=dt.datetime.now(dt.timezone.utc)                         #Datenbanken zuletzt aktualisiert Zeitpunkt
discord_bot_token=""                                                        #Bot-Token
discord_channel="botspam"                                                   #Botkanal
discord_channel_ID=839081784008245248                                       #Botkanal-ID
discord_username="Chemtrail Sprayer#6530"                                   #Nutzername eigener für Kontrollbefehlberechtigung
DT_now=dt.datetime.now(dt.timezone.utc)                                     #Durchgang aktuell Zeitpunkt
DOWNLOAD_TIMEOUT=50                                                         #Timeout für METAR- und TAF-Downloads
force_print=True                                                            #Station drucken erzwingen (Nutzereingabe) oder nicht (Abo)
frequency_DB=pd.DataFrame()                                                 #Frequenzdatenbanke für Info-Befehl
message_last=None                                                           #Nachricht zuletzt, für Abonnement
METAR_o_last=""                                                             #METAR zuletzt, für Abonnement
METAR_update_finished=False                                                 #hat Programm in Abo 1 Runde gewartet bis Quellwebseite mit METAR-Aktualisierung vollständig durch?
navaid_DB=pd.DataFrame()                                                    #Navaiddatenbank für Info-Befehl
RWY_DB=pd.DataFrame()                                                       #Pistendatenbank für Seitenwindkomponenten und Info-Befehl
TAF_o_last=""                                                               #TAF zuletzt, für Abonnement
TAF_update_finished=False                                                   #hat Programm in Abo 1 Runde gewartet bis Quellwebseite mit TAF-Aktualisierung vollständig durch?
terminate=False                                                             #Programm schließen?


@KFSlog.timeit
def main():
    @client.event
    async def on_ready():
        global airport_DB
        global country_DB
        global discord_bot_token
        global DT_DB_last_updated
        global frequency_DB
        global navaid_DB
        global RWY_DB


        KFSlog.write("--------------------------------------------------")
        DT_now=dt.datetime.now(dt.timezone.utc)
        
        #Datenbanken initialisieren
        airport_DB  =init_DB("Airport",   airport_DB,   DT_now)
        country_DB  =init_DB("Country",   country_DB,   DT_now)
        frequency_DB=init_DB("Frequency", frequency_DB, DT_now)
        navaid_DB   =init_DB("Navaid",    navaid_DB,    DT_now)
        RWY_DB      =init_DB("Runway",    RWY_DB,       DT_now)
        DT_DB_last_updated=DT_now   #Datenbanken jetzt zuletzt aktualisiert

        KFSlog.write("Discord client started.")
        await client.get_channel(discord_channel_ID).send("Discord client started.")
        return

    @client.event
    async def on_message(message):
        global force_print
        global message_last
        global METAR_o_last
        global METAR_update_finished
        global TAF_o_last
        global TAF_update_finished

        #behalten nur für Aktualisierungsdurchlauf aktuell
        append_TAF=False    #TAF noch dranhängen?
        message_send=""     #Nachricht final an Discord
        METAR_o=""          #METAR Originalformatierung
        METAR=""            #METAR Neuformatierung
        station=""          #Flughafen relevant
        station_elev=None   #Flughafenhöhe
        station_name=""     #Flughafenname
        TAF_o=""            #TAF Originalformatierung
        TAF=""              #TAF Neuformatierung


        if message.author==client.user or str(message.channel)!=discord_channel:    #wenn boteigene Nachricht oder außerhalb von botspam-Kanal: nix tun
            force_print=True                                                        #standardmäßig drucken zwingen
            return


        KFSlog.write("--------------------------------------------------")


        #Kontrollbefehle ausführen
        """if str(message.author)==discord_username:   #wenn Nutzer eigener: Kontrollbefehle ausführen
            if message.lower()=="stop": #wenn Stoppbefehl
                KFSlog.write("Executing stop command...")
                await message.channel.send('「Executing stop command.」\n')
                #await client.close()    #Client schließen, Laden runterfahren
                #TODO"""
            
        
        #Station herausfinden, TAF anhängen?, Info-Befehl?
        if((re.search("^[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]$",      message.content.upper())!=None)   #wenn Nachricht letzte im Format "ICAO-Code"
        or (re.search("^[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9] TAF$",  message.content.upper())!=None)   #TAF erwünscht
        or (re.search("^[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9] INFO$", message.content.upper())!=None)): #nur Info erwünscht
            station=message.content[0:4].upper()    #Station ist Nachrichtanfang
            KFSlog.write(f"Station: {station}")

            if re.search("^[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9] TAF$",  message.content.upper())!=None:   #wenn "ICAO-Code TAF":
                append_TAF=True     #TAF erwünscht
                KFSlog.write("TAF was requested.")

        else:                                           #wenn Nachricht letzte nicht im Format "ICAO-Code" oder "ICAO-Code TAF"
            KFSlog.write(f"Last message \"{message.content}\" is no ICAO format.")     #kein ICAO-Format, ignorieren
            force_print=True                                                        #standardmäßig drucken zwingen
            return

        #Station_Name und Station_Elev
        KFSlog.write(f"Looking for {station} in airport database...")
        airport=airport_DB[airport_DB["ident"]==station]                                #Flughafen gesucht
        airport=airport.reset_index(drop=True)
        if airport.empty==False:                                                        #wenn Flughafen gefunden:
            KFSlog.write(f"\r{station} found in airport database.")

            if pd.isna(airport.at[0, "elevation_ft"])==False:                           #wenn Wert gegeben:
                station_elev=round(airport.at[0, "elevation_ft"]*0.3048)                #Höhe eintragen [m]
            country=country_DB[country_DB["code"]==airport.at[0, "iso_country"]]        #Land gesucht
            country=country.reset_index(drop=True)
            if country.empty==False:                                                    #wenn Flughafenland gefunden:
                station_name=f"{country.at[0, 'name']}, {airport.at[0, 'name']}"        #Land, Name eintragen
            else:                                                                       #wenn Flughafenland nicht gefunden:
                KFSlog.write(f"Country of country code \"{airport.at[0, 'iso_country']}\" not found.")
                station_name=f"{airport.at[0, 'iso_country']}, {airport.at[0, 'name']}" #Landcode, Name eintragen
            KFSlog.write(f"Name: \"{station_name}\"")
            if station_elev!=None:
                KFSlog.write(" | "+f"Elev={station_elev:,.0f}m".replace(",", "."), append_to_line_current=True)
        else:                                                                   #wenn Flughafen nicht gefunden:
            KFSlog.write(f"\r{station} not found in airport database.")

        #Info-Befehl
        if re.search("^[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9] INFO$", message.content.upper())!=None: #wenn Info-Befehl:
            await airport_info(station, station_name, station_elev, frequency_DB, navaid_DB, RWY_DB, message)
            force_print=True    #standardmäßig drucken zwingen
            return              #kein METAR schicken
        

        #METAR und TAF herunterladen und konvertieren
        try:
            METAR_o, METAR=process_METAR(station, station_elev, RWY_DB, force_print, DOWNLOAD_TIMEOUT)
        except requests.ConnectionError:    #wenn nicht erfolgreich: abbrechen
            KFSlog.write("\rDownloading METAR failed.")
            force_print=True                #standardmäßig drucken zwingen
            return
        except requests.ReadTimeout:        #wenn nicht erfolgreich: abbrechen
            KFSlog.write(f"\rDownloading METAR timed out after {DOWNLOAD_TIMEOUT}s.")
            force_print=True                #standardmäßig drucken zwingen
            return

        if append_TAF==True:
            try:
                TAF_o, TAF=process_TAF(station, station_elev, RWY_DB, force_print, DOWNLOAD_TIMEOUT)
            except requests.ConnectionError:    #wenn nicht erfolgreich: TAF nicht drucken
                KFSlog.write("\rDownloading TAF failed. Continuing without TAF...")
                append_TAF=False
                TAF_o=""
                TAF=""
            except requests.ReadTimeout:    #wenn nicht erfolgreich: TAF nicht drucken
                KFSlog.write(f"\rDownloading TAF timed out after {DOWNLOAD_TIMEOUT}s. Continuing without TAF...")
                append_TAF=False
                TAF_o=""
                TAF=""


        #Nachricht drucken?, AboKFSlogik
        if force_print==True:           #wenn drucken erzwingen: kein Abo
            message_last=message        #Nutzernachricht zuletzt aktualisieren
            METAR_o_last=METAR_o        #METAR original aktualisieren
            TAF_o_last=TAF_o            #TAF orginal aktualisieren
            METAR_update_finished=False #schon gewartet zurücksetzen
            TAF_update_finished=False
        
        elif append_TAF==False:         #wenn kein drucken erzwingen: Abo; wenn TAF unerwünscht: TAF nicht berücksichtigen
            if METAR_o_last==METAR_o:   #wenn METAR original mit letztem übereinstimmen und drucken nicht zwingen: Abo, nichts drucken
                KFSlog.write("Original METAR has not been changed. Not sending anything.")
                force_print=True        #standardmäßig aber drucken zwingen
                return
            elif METAR_o_last!=METAR_o and METAR_update_finished==False:    #wenn METAR original neu anders, noch nicht gewartet: Abo, 1 Runde warten damit Quellwebseite mit Aktualisierung garantiert fertig
                KFSlog.write("Original METAR has changed, but update process may not have been finished yet. Not sending anything.")
                METAR_update_finished=True   
                force_print=True                                            #standardmäßig aber drucken zwingen
                return
            elif METAR_o_last!=METAR_o and METAR_update_finished==True:     #wenn METAR original neu anders, schon gewartet: Abo, 1 Runde gewartet und jetzt METAR aber mal senden
                KFSlog.write("Original METAR has changed and update process should have been finished.")
                METAR_o_last=METAR_o                                        #METAR original aktualisieren
                METAR_update_finished=False                                 #schon gewartet zurücksetzen
        
        elif append_TAF==True:          #Abo; wenn TAF abonniert: TAF auch berücksichtigen
            if METAR_o_last==METAR_o and TAF_o_last==TAF_o:                 #wenn METAR original und TAF original mit letztem übereinstimmen: Abo, nichts drucken
                KFSlog.write("Original METAR and TAF have not been changed. Not sending anything.")
                force_print=True                                            #standardmäßig aber drucken zwingen
                return
            elif(METAR_o_last!=METAR_o and TAF_o_last!=TAF_o
                 and METAR_update_finished==False and TAF_update_finished==False):#wenn METAR original neu und TAF original neu anders, noch nicht gewartet: Abo, 1 Runde warten damit Quellwebseite mit Aktualisierung garantiert fertig
                KFSlog.write("Original METAR and TAF have changed, but update process may not have been finished yet. Not sending anything.")
                METAR_update_finished=True
                TAF_update_finished=True
                force_print=True                                            #standardmäßig aber drucken zwingen
                return
            elif METAR_o_last!=METAR_o and METAR_update_finished==False:    #wenn METAR original neu anders, noch nicht gewartet: Abo, 1 Runde warten damit Quellwebseite mit Aktualisierung garantiert fertig
                KFSlog.write("Original METAR has changed, but update process may not have been finished yet. Not sending anything.")
                METAR_update_finished=True
                force_print=True                                            #standardmäßig aber drucken zwingen
                return
            elif TAF_o_last!=TAF_o and TAF_update_finished==False:          #wenn TAF original neu anders, noch nicht gewartet: Abo, 1 Runde warten damit Quellwebseite mit Aktualisierung garantiert fertig
                KFSlog.write("Original TAF has changed, but update process may not have been finished yet. Not sending anything.")
                TAF_update_finished=True
                force_print=True                                            #standardmäßig aber drucken zwingen
                return
            elif(METAR_o_last!=METAR_o and TAF_o_last!=TAF_o
                 and METAR_update_finished==True and TAF_update_finished==True):    #wenn METAR original neu und TAF original neu anders, schon gewartet: Abo, 1 Runde gewartet und jetzt METAR und TAF aber mal senden
                KFSlog.write("Original METAR and TAF have changed and update process should have been finished.")
                METAR_o_last=METAR_o                                        #METAR original aktualisieren
                TAF_o_last=TAF_o                                            #TAF orginal aktualisieren
                METAR_update_finished=False                                 #schon gewartet zurücksetzen
                TAF_update_finished=False
            elif METAR_o_last!=METAR_o and METAR_update_finished==True:     #wenn METAR original neu anders, schon gewartet: Abo, 1 Runde gewartet und jetzt METAR aber mal senden
                KFSlog.write("Original METAR has changed and update process should have been finished.")
                METAR_o_last=METAR_o                                        #METAR original aktualisieren
                METAR_update_finished=False                                 #schon gewartet zurücksetzen
                append_TAF=False                                            #METAR aktualisieren, aber TAF wahrscheinlich nicht, wegen Abo nur METAR schicken
            elif TAF_o_last!=TAF_o and TAF_update_finished==True:           #wenn TAF original neu anders, schon gewartet: Abo, 1 Runde gewartet und jetzt METAR und TAF aber mal senden
                KFSlog.write("Original TAF has changed and update process should have been finished.")
                TAF_o_last=TAF_o                                            #TAF orginal aktualisieren
                TAF_update_finished=False                                   #schon gewartet zurücksetzen

        #Nachrichten schicken
        if append_TAF==False:
            KFSlog.write("Sending METAR, original METAR, and elevation...")
        elif append_TAF==True and TAF_o!=f"{station} TAF could not be found.":
            KFSlog.write("Sending METAR, TAF, original METAR, original TAF, and elevation...")
        elif append_TAF==True and TAF_o==f"{station} TAF could not be found.":
            KFSlog.write("Sending METAR, original METAR, error message, and elevation...")

        if station_name!="":                                        #wenn Flughafenname vorhanden:
            message_send+=f"{station_name}\n----------\n"           #Flughafenname schicken
        else:
            message_send+="Station could not be found in airport database.\n----------\n"
        if METAR_o!="":                                             #wenn METAR gefunden:
            message_send+=f"```{METAR}```\n----------\n"            #METAR schicken
        else:
            message_send+="METAR could not be found.\n----------\n"
        if append_TAF==True and TAF_o!="":                          #wenn TAF geschickt werden soll:
            message_send+=f"```{TAF}```\n----------\n"              #TAF normal schicken
        elif append_TAF==True and TAF_o=="":
            message_send+="TAF could not be found.\n----------\n"
        if METAR_o!="":                                                                             #wenn METAR gefunden:
            message_send+=f"```{METAR_o}```\n----------\n"                                          #METAR original auch schicken
        if append_TAF==True and TAF_o!="":                                                          #wenn TAF geschickt werden soll und gefunden wurde und kein Abo:
            message_send+=f"```{TAF_o}```\n----------\n"                                            #TAF original auch schicken    
        if station_elev!=None:                                                                      #wenn Flughafenhöhe vorhanden:
            message_send+=f"```Elevation = {station_elev:,.0f}m ({station_elev/0.3048:,.0f}ft)```\n----------\n".replace(",", ".")  #Station_Elev zur Kontrolle auch schicken
        
        if METAR_o!="" or TAF_o!="":                                                                #wenn ein METAR oder TAF geschickt wurde: Hinweis
            message_send+="Only use original METAR and TAF for flight operations!\nClouds are given as [coverage][altitude]|[height].\n"
        if station_name=="":                                                                        #wenn Flughafenname nicht vorhanden: Fehlermeldung
            message_send+="Station could not be found in airport database.\nClouds are given as heights. Winds are assumed direct crosswind and will be marked at 10m/s or more. Variable winds are assumed direct tailwind and will be marked at 5m/s or more.\n"
        elif station_elev==None:
            message_send+="Station could not be found in airport database.\nClouds are given as heights.\n"
        
        try:
            await message.channel.send(message_send)    #Nachricht an Discord abschicken
        except discord.errors.DiscordServerError:
            KFSlog.write("Sending message to discord failed.")
        else:
            if append_TAF==False:
                KFSlog.write("\rMETAR, original METAR, and elevation sent.")
            elif append_TAF==True and TAF_o!="":
                KFSlog.write("\rMETAR, TAF, original METAR, original TAF, and elevation sent.")
            elif append_TAF==True and TAF_o=="":
                KFSlog.write("\rMETAR, original METAR, error message, and elevation sent.")

        force_print=True    #bei nächstem Durchlauf wieder standardmäßig drucken erzwingen
        return


    @tasks.loop(seconds=100)    #alle 100s auf Updates schauen
    async def METAR_updated():
        global airport_DB
        global country_DB
        global DT_DB_last_updated
        global force_print
        global frequency_DB
        global message_last
        global navaid_DB
        global RWY_DB


        #Datenbanken aktualisieren
        DT_now=dt.datetime.now(dt.timezone.utc)
        if DT_DB_last_updated.day!=DT_now.day:  #wenn seit Aktualisierung letzter Tag geändert: Datenbanken aktualisieren
            airport_DB  =init_DB("Airport",   airport_DB,   DT_now)
            country_DB  =init_DB("Country",   country_DB,   DT_now)
            frequency_DB=init_DB("Frequency", frequency_DB, DT_now)
            navaid_DB   =init_DB("Navaid",    navaid_DB,    DT_now)
            RWY_DB      =init_DB("Runway",    RWY_DB,       DT_now)
            DT_DB_last_updated=DT_now           #Datenbanken jetzt zuletzt aktualisiert
        

        if message_last==None:  #wenn seit Start noch keine Nachricht eingegangen: kein Abo möglich
            return

        force_print=False               #Abo
        await on_message(message_last)
        return
    METAR_updated.start()

    #Bot-Token initialisieren, nicht hardgecoded damit er nicht im Quelltext auf Github steht
    with open("discord_bot_token.txt", "rt") as discord_bot_token_file:
        discord_bot_token=discord_bot_token_file.read()
    client.run(discord_bot_token)


# METAR aktuell
# http://tgftp.nws.noaa.gov/data/observations/metar/stations/<station>.TXT
# TAF aktuell
# https://tgftp.nws.noaa.gov/data/forecasts/taf/stations/<station>.TXT
#
# Beispiel
# https://github.com/python-metar/python-metar
#
# METAR erklärt
# https://mediawiki.ivao.aero/index.php?title=METAR_explanation
#
# Flughafendatenbank
# https://raw.githubusercontent.com/mborsetti/airportsdata/main/airportsdata/airports.csv