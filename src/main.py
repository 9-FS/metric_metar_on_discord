import aiohttp.client_exceptions    #for exception catching
import asyncio
import discord, discord.ext.tasks   #discord, discord event scheduler
import datetime as dt               #datetime
import KFS
import logging                      #standard logging
import pandas                       #DataFrame
import re                           #regular expressions
import requests                     #HTTP exceptions
from aerodrome_info    import aerodrome_info    #aerodrome information command
from DB_Type           import DB_Type           #database type for init_DB
from Doc_Type          import Doc_Type          #process METAR or TAF?
from init_DB           import init_DB           #download database or load from file
from process_METAR_TAF import process_METAR_TAF #download and convert METAR or TAF
from weather_minimums  import WEATHER_MIN       #weather minimums for marking


#keep over runtime whole
aerodrome_DB: pandas.DataFrame=pandas.DataFrame()   #aerodrome database
country_DB: pandas.DataFrame=pandas.DataFrame()     #country database for country names
discord_bot_token: str|None                         #discord bot token
discord_channel_ID: int                             #bot channel ID
DOWNLOAD_TIMEOUT: int=50                            #METAR and TAF download timeouts [s]
COMMANDS_ALLOWED: tuple=(                           #commands allowed
    "^(?P<station_ICAO>[0-9A-Z]{4})$",
    "^(?P<station_ICAO>[0-9A-Z]{4}) TAF$",
    #"^(?P<station_ICAO>[0-9A-Z]{4}) INFO$" #TODO
)
force_print: bool=True                                  #force sending to discord (after user input request) or not (subscription)
frequency_DB: pandas.DataFrame=pandas.DataFrame()       #frequency database for information command
message_previous: None|str=None                         #message previous for subscription
METAR_o_previous: None|str                              #METAR previous for subscription
METAR_update_finished: bool                             #has program in subscription mode waited 1 round until source website refreshed METAR completely?
navaid_DB: pandas.DataFrame=pandas.DataFrame()          #navaid database for information command
now_DT: dt.datetime=dt.datetime.now(dt.timezone.utc)    #DT currently
RWY_DB: pandas.DataFrame=pandas.DataFrame()             #runway database for cross wind components and information command
TAF_o_previous: str|None                                #TAF previous for subscription
TAF_update_finished: bool                               #has program in subscription mode waited 1 round until source website refreshed TAF completely?


@KFS.log.timeit_async
async def main() -> None:
    intents: discord.Intents=discord.Intents.default()              #standard permissions
    intents.message_content=True                                    #in addition with message contents
    discord_client: discord.Client=discord.Client(intents=intents)  #create client instance

    discord_bot_token=KFS.config.load_config("discord_bot.token")               #load discord bot token
    discord_channel_ID=int(KFS.config.load_config("discord_channel_ID.config")) #load bot channel ID


    @discord_client.event
    async def on_ready():
        """
        Executed as soon as bot started up and is ready. Also executes after bot reconnects to the internet and is ready again. Initialised databases.
        """

        global aerodrome_DB
        global country_DB
        global frequency_DB
        global navaid_DB
        global RWY_DB
        

        logging.info("--------------------------------------------------")
        now_DT=dt.datetime.now(dt.timezone.utc)
        
        #initialise databases
        aerodrome_DB=init_DB(DB_Type.aerodrome, aerodrome_DB, now_DT, DOWNLOAD_TIMEOUT)
        country_DB  =init_DB(DB_Type.country,   country_DB,   now_DT, DOWNLOAD_TIMEOUT)
        frequency_DB=init_DB(DB_Type.frequency, frequency_DB, now_DT, DOWNLOAD_TIMEOUT)
        navaid_DB   =init_DB(DB_Type.navaid,    navaid_DB,    now_DT, DOWNLOAD_TIMEOUT)
        RWY_DB      =init_DB(DB_Type.runway,    RWY_DB,       now_DT, DOWNLOAD_TIMEOUT)

        logging.info("Started discord client.")
        #await discord_client.get_channel(DISCORD_CHANNEL_ID).send("Started discord client.") #tell user bot is ready to use now #type:ignore
        return

    @discord_client.event
    async def on_message(message):
        """
        Executed every time a message is sent on the server. If the message is not from the bot itself and in the botspam channel, process it.

        - \"{ICAO code}\" requests the current METAR and changes the subscribed station.

        - \"{ICAO code} TAF\" requests the current METAR and TAF and changes the subscribed station.

        - \"{ICAO code} INFO\" requests information and does not change the subscribed station. TODO: CURRENTLY UNUSABLE.
        """

        global force_print
        global message_previous
        global METAR_o_previous
        global METAR_update_finished
        global TAF_o_previous
        global TAF_update_finished


        #keep only for this iteration
        append_TAF: bool    #append TAF?
        INFO_command: bool  #information command?
        message_send: str   #message final to discord
        METAR_o: str|None   #METAR original format
        METAR: str|None     #METAR my format
        station: dict={}    #station parsed elev: float|None, ICAO: str, and name: str|None
        TAF_o: str|None     #TAF original format
        TAF: str|None       #TAF my format


        class ContextManager():
            def __enter__(self):
                pass
            def __exit__(self, exc_type, exc_value, exc_traceback): #upon exit, force print by default
                global force_print
                force_print=True
        with ContextManager():  #upon exit, force print by default
            if message.author==discord_client.user or message.channel.id!=discord_channel_ID:   #if message from bot itself or outside botspam channel: do nothing
                return
            message.content=message.content.upper()


            logging.info("--------------------------------------------------")
            now_DT=dt.datetime.now(dt.timezone.utc)

            #station_ICAO, append_TAF
            for command in COMMANDS_ALLOWED:                            #did message match an allowed command?
                re_match=re.search(command, message.content)
                if re_match==None:                                      #if message did not match this command:
                    continue
                station["ICAO"]=re_match.groupdict()["station_ICAO"]    #parse station ICAO code
                logging.info(f"Station: {station['ICAO']}")
                if message.content.endswith("TAF")==True:               #if message ends with TAF:
                    logging.info("TAF was requested.")
                    append_TAF=True                                     #TAF requested, append TAF later
                else:
                    append_TAF=False
                #if command.endswith("INFO"):                           #if matched command ends with INFO:
                #    logging.info("INFO was requested.")
                #    INFO_command=True                                  #INFO requested, get information later
                #else:
                INFO_command=False
                break                                                   #command found, exit
            else:                                                       #if message did not match any command:
                logging.error(f"Last message \"{message.content}\" did not match any allowed command.")
                return
            
            #station_name, station_elev
            logging.info(f"Looking for {station['ICAO']} in aerodrome database...")
            aerodrome=aerodrome_DB[aerodrome_DB["ident"]==station["ICAO"]] #aerodrome desired
            aerodrome=aerodrome.reset_index(drop=True)
            if aerodrome.empty==True:   #if aerodrome not found in database:
                logging.warning(f"\rCould not find {station['ICAO']} in aerodrome database. No title, elevation, and runway directions available.")
                station["elev"]=None
                station["name"]=None
            else:   #if aerodrome found in database:
                logging.info(f"\rFound {station['ICAO']} in aerodrome database.")
                country=country_DB[country_DB["code"]==aerodrome.at[0, "iso_country"]]  #country desired
                country=country.reset_index(drop=True)
                if country.empty==True: #if country not found in database:
                    logging.warning(f"Could not find country of country code \"{aerodrome.at[0, 'iso_country']}\".")
                    station["name"]=f"{aerodrome.at[0, 'iso_country']}, {aerodrome.at[0, 'name']}" #enter country code, aerodrome name
                else:   #if country found in database:
                    station["name"]=f"{country.at[0, 'name']}, {aerodrome.at[0, 'name']}"  #enter country, aerodrome name
                logging.info(f"Name: {station['name']}")

                if pandas.isna(aerodrome.at[0, "elevation_ft"])==True:  #if elevation unavailable:
                    logging.warning(f"\r{station['ICAO']} has no elevation information in aerodrome database. No elevation available.")
                    station["elev"]=None
                else:                                                   #if elevation available:
                    station["elev"]=aerodrome.at[0, "elevation_ft"]*KFS.convert_to_SI.length["ft"]  #save elevation [m]
                    logging.info(f"Elevation: {KFS.fstr.notation_abs(station['elev'], 0, round_static=True)}m")

            #information command
            if INFO_command==True:  #if information command: execute that, then return without downloading METAR, TAF etc.
                await aerodrome_info(station, frequency_DB, navaid_DB, RWY_DB, message)
                return
            

            #download and convert METAR and TAF
            try:
                METAR_o, METAR=process_METAR_TAF(Doc_Type.METAR, station, RWY_DB, now_DT, force_print, DOWNLOAD_TIMEOUT)
            except requests.ConnectTimeout:     #if unsuccessful: abort
                logging.error(f"\rDownloading METAR timed out after {DOWNLOAD_TIMEOUT}s.")
                return
            except requests.ConnectionError:    #if unsuccessful: abort
                logging.error("\rDownloading METAR failed.")
                return
            
            if append_TAF==True:    #if append TAF: append TAF
                try:
                    TAF_o, TAF=process_METAR_TAF(Doc_Type.TAF, station, RWY_DB, now_DT, force_print, DOWNLOAD_TIMEOUT)
                except requests.ConnectTimeout:     #if unsuccessful: just no TAF
                    logging.warning(f"\rDownloading TAF timed out after {DOWNLOAD_TIMEOUT}s. Continuing without TAF...")
                    append_TAF=False
                    TAF_o=None
                    TAF=None
                except requests.ConnectionError:    #if unsuccessful: just no TAF
                    logging.warning("\rDownloading TAF failed. Continuing without TAF...")
                    append_TAF=False
                    TAF_o=None
                    TAF=None
            else:   #default TAF
                TAF_o=None
                TAF=None


            #print message? subscription logic
            if force_print==True:                   #if force printing: no subscription
                message_previous=message            #refresh message previous
                METAR_o_previous=METAR_o            #refresh METAR original previous
                TAF_o_previous=TAF_o                #refresh TAF orginal previous #type:ignore
                METAR_update_finished=False         #reset already waited for METAR
                TAF_update_finished=False           #reset already waited for TAF
            
            elif append_TAF==False:                                                 #subscription; if TAF undesired: disregard TAF
                if METAR_o_previous==METAR_o:                                       #if METAR original same as previous one: subscription, don't print
                    logging.info("Original METAR has not been changed. Not sending anything.")
                    return
                elif METAR_o_previous!=METAR_o and METAR_update_finished==False:    #if METAR original new different, but not waited yet: subscription, wait 1 round until source website refreshed METAR completely
                    logging.info("Original METAR has changed, but update process may not have been finished yet. Not sending anything yet.")
                    METAR_update_finished=True   
                    return
                elif METAR_o_previous!=METAR_o and METAR_update_finished==True:     #if METAR original new different and waited already: subscription, source website refreshed METAR completely, now send METAR
                    logging.info("Original METAR has changed and update process should have been finished.")
                    METAR_o_previous=METAR_o                                        #refresh METAR original previous
                    METAR_update_finished=False                                     #reset already waited for METAR
            
            elif append_TAF==True:                                                  #subscription; if TAF desiredt: regard TAF
                if METAR_o_previous==METAR_o and TAF_o_previous==TAF_o:             #if METAR original and TAF original same as previous one: subscription, don't print #type:ignore
                    logging.info("Original METAR and TAF have not been changed. Not sending anything.")
                    return
                elif(METAR_o_previous!=METAR_o and TAF_o_previous!=TAF_o            #if METAR original new and TAF original new different, but not waited yet: subscription, wait 1 round until source website refreshed METAR and TAF completely #type:ignore
                    and METAR_update_finished==False and TAF_update_finished==False):
                    logging.info("Original METAR and TAF have changed, but update process may not have been finished yet. Not sending anything yet.")
                    METAR_update_finished=True
                    TAF_update_finished=True
                    return
                elif METAR_o_previous!=METAR_o and METAR_update_finished==False:    #if METAR original new different, but not waited yet: subscription, wait 1 round until source website refreshed METAR completely
                    logging.info("Original METAR has changed, but update process may not have been finished yet. Not sending anything yet.")
                    METAR_update_finished=True
                    return
                elif TAF_o_previous!=TAF_o and TAF_update_finished==False:          #if TAF original new different, but not waited yet: subscription, wait 1 round until source website refreshed TAF completely #type:ignore
                    logging.info("Original TAF has changed, but update process may not have been finished yet. Not sending anything yet.")
                    TAF_update_finished=True
                    return
                elif(METAR_o_previous!=METAR_o and TAF_o_previous!=TAF_o            #if METAR original new and TAF original new different and waited already: subscription, source website refreshed METAR and TAF completely, now send METAR and TAF #type:ignore
                    and METAR_update_finished==True and TAF_update_finished==True):
                    logging.info("Original METAR and TAF have changed and update process should have been finished.")
                    METAR_o_previous=METAR_o                                        #refresh METAR original previous
                    TAF_o_previous=TAF_o                                            #refresh TAF original previous #type:ignore
                    METAR_update_finished=False                                     #reset already waited for METAR
                    TAF_update_finished=False                                       #reset already waited for TAF
                elif METAR_o_previous!=METAR_o and METAR_update_finished==True:     #if METAR original new different and waited already: subscription, source website refreshed METAR completely, now send METAR
                    logging.info("Original METAR has changed and update process should have been finished.")
                    METAR_o_previous=METAR_o                                        #refresh METAR original previous
                    METAR_update_finished=False                                     #reset already waited for METAR
                    append_TAF=False                                                #TAF did probably not refresh yet, subscription, only send METAR
                elif TAF_o_previous!=TAF_o and TAF_update_finished==True:           #if TAF original new different and waited already: subscription, source website refreshed TAF completely, now send METAR and TAF #type:ignore
                    logging.info("Original TAF has changed and update process should have been finished.")
                    TAF_o_previous=TAF_o                                            #refresh TAF original previous #type:ignore
                    TAF_update_finished=False                                       #reset already waited for TAF

            #send messages
            if append_TAF==False:
                logging.info("Sending METAR and original METAR...")
            elif append_TAF==True and TAF_o!=None:  #type:ignore
                logging.info("Sending METAR, TAF, original METAR, and original TAF...")
            elif append_TAF==True and TAF_o==None:  #type:ignore
                logging.info("Sending METAR, original METAR, and error message...")

            message_send=""
            if station["name"]==None:                                       #if station name not found:
                message_send+=f"Could not find {station['ICAO']} in aerodrome database. No title, elevation, and runway directions available..\n----------\n"  #send error message
            else:                                                           #if station name found:
                message_send+=f"{station['name']}\n----------\n"            #send station name
            if METAR_o==None:                                               #if METAR not found:
                message_send+="There is no published METAR.\n----------\n"  #send error message
            else:                                                           #if METAR found:
                message_send+=f"```{METAR}```\n----------\n"                #send METAR
            if append_TAF==True and TAF_o==None:                            #if TAF desired and not found: #type:ignore
                message_send+="There is no pusblished TAF.\n----------\n"   #send error message
            elif append_TAF==True and TAF_o!=None:                          #if TAF desired and found: #type:ignore
                message_send+=f"```{TAF}```\n----------\n"                  #send TAF #type:ignore
            if METAR_o!=None:                                               #if METAR found:
                message_send+=f"```{METAR_o}```\n----------\n"              #send METAR original too
            if append_TAF==True and TAF_o!=None:                            #if TAF desired and found: #type:ignore
                message_send+=f"```{TAF_o}```\n----------\n"                #send TAF original too     #type:ignore
            if station["elev"]!=None:                                      #if station elevation found:
                message_send+=f"```Elevation = {KFS.fstr.notation_abs(station['elev'], 0, round_static=True)}m ({KFS.fstr.notation_abs(station['elev']/0.3048, 0, round_static=True)}ft)```\n----------\n".replace(",", ".")  #send station elevation
            
            if METAR_o!=None or TAF_o!=None:    #if a METAR of TAF sent: warnings #type:ignore
                message_send+="Only use original METAR and TAF for flight operations!\n"
                if station["name"]==None:       #if aerodrome not found in database
                    message_send+=f"Clouds are given as heights. Winds are assumed direct crosswind and will be marked at {KFS.fstr.notation_tech(WEATHER_MIN['CWC'], 2)}m/s or more. Variable winds are assumed direct tailwind and will be marked at {KFS.fstr.notation_tech(WEATHER_MIN['TWC'], 2)}m/s or more.\n"
                elif station["elev"]==None:     #if only elevation not found
                    message_send+="Clouds are given as heights.\n"
                else:                           #if everything found: default message
                    message_send+="Clouds are given as \"{coverage}{altitude}|{height}\".\n"
            
            try:
                await message.channel.send(message_send)    #send message to discord
            except discord.errors.DiscordServerError:
                logging.error("Sending message to discord failed.")
                return
            if append_TAF==False:
                logging.info("\rSent METAR and original METAR.")
            elif append_TAF==True and TAF_o!=None:
                logging.info("\rSent METAR, TAF, original METAR, and original TAF.")
            elif append_TAF==True and TAF_o==None:
                logging.info("\rSent METAR, original METAR, and error message.")

        return


    @discord.ext.tasks.loop(seconds=100)    #every 100s look for updates
    async def METAR_updated():
        global aerodrome_DB
        global country_DB
        global force_print
        global frequency_DB
        global message_previous
        global navaid_DB
        global RWY_DB


        #refresh databases
        now_DT=dt.datetime.now(dt.timezone.utc)
        aerodrome_DB=init_DB(DB_Type.aerodrome, aerodrome_DB, now_DT, DOWNLOAD_TIMEOUT)
        country_DB  =init_DB(DB_Type.country,   country_DB,   now_DT, DOWNLOAD_TIMEOUT)
        frequency_DB=init_DB(DB_Type.frequency, frequency_DB, now_DT, DOWNLOAD_TIMEOUT)
        navaid_DB   =init_DB(DB_Type.navaid,    navaid_DB,    now_DT, DOWNLOAD_TIMEOUT)
        RWY_DB      =init_DB(DB_Type.runway,    RWY_DB,       now_DT, DOWNLOAD_TIMEOUT)
        

        if message_previous==None:  #if no message since startup: no subscription possible
            return

        force_print=False           #subscription
        await on_message(message_previous)
        return
    METAR_updated.start()   #start event

    while True:
        logging.info("Starting discord client...")
        try:
            await discord_client.start(discord_bot_token)               #start discord client now
        except aiohttp.client_exceptions.ClientConnectorError:          #if temporary internet failure: retry connection
            logging.error("Starting discord client failed, because client could not connect. Retrying in 10s...")
            await asyncio.sleep(10)


# METAR now
# http://tgftp.nws.noaa.gov/data/observations/metar/stations/<station>.TXT
# TAF now
# https://tgftp.nws.noaa.gov/data/forecasts/taf/stations/<station>.TXT
#
# METAR explained
# https://mediawiki.ivao.aero/index.php?title=METAR_explanation
#
# databases
# https://ourairports.com/data/