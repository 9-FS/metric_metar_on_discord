#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import aiohttp.client_exceptions
import asyncio
import discord, discord.ext.tasks
import datetime as dt
import inspect
import jsonpickle
import KFS.config, KFS.convert_to_SI, KFS.fstr, KFS.log
import logging
import pandas
import re
import requests
from DB_Type           import DB_Type
from Doc_Type          import Doc_Type
from init_DB           import init_DB
from process_METAR_TAF import process_METAR_TAF
from Server            import Server
from Station           import Station
from weather_minimums  import WEATHER_MIN


#keep over runtime whole
aerodrome_DB: pandas.DataFrame=pandas.DataFrame()   #aerodrome database
country_DB: pandas.DataFrame  =pandas.DataFrame()   #country database for country names
frequency_DB: pandas.DataFrame=pandas.DataFrame()   #frequency database for information command
navaid_DB: pandas.DataFrame   =pandas.DataFrame()   #navaid database for information command
RWY_DB: pandas.DataFrame      =pandas.DataFrame()   #runway database for cross wind components and information command
servers: list[Server]                               #all variables for 1 server instance
SERVERS_FILENAME: str="servers.json"                #save filename for all servers, so subscription is remembered beyond restarts


@KFS.log.timeit_async
async def main() -> None:
    global servers
    
    #keep over runtime whole, but read-only in sub-functions
    DOWNLOAD_TIMEOUT: int=50                #METAR and TAF download timeouts [s]
    COMMANDS_ALLOWED: tuple=(               #commands allowed
        "^(?P<station_ICAO>[0-9A-Z]{4})$",
        "^(?P<station_ICAO>[0-9A-Z]{4}) TAF$",
        #"^(?P<station_ICAO>[0-9A-Z]{4}) INFO$" #TODO
    )
    discord_bot: discord.Client             #discord client instance
    discord_bot_channel_names: list[str]    #bot channel names
    discord_bot_token: str                  #discord bot token
    intents: discord.Intents                #client permissions
    if logging.root.level<=logging.DEBUG:   #if level debug or lower:
        UPDATE_FREQUENCY: float=200e-3      #update subscription with 200mHz (every 5s)
    else:
        UPDATE_FREQUENCY: float=10e-3       #but usually update subscription with 10mHz (every 100s)

    discord_bot_channel_names=[bot_channel_name for bot_channel_name in KFS.config.load_config("discord_bot_channel_names.config", "bots\nbotspam\nmetar").split("\n") if bot_channel_name!=""] #load bot channel names, remove empty lines
    discord_bot_token=KFS.config.load_config("discord_bot.token")   #load discord bot token
    intents=discord.Intents.default()                               #standard permissions
    intents.message_content=True                                    #in addition with message contents
    discord_bot=discord.Client(intents=intents)                     #create client instance

    logging.info(f"Restoring server states from \"{SERVERS_FILENAME}\"...")
    try:
        with open(SERVERS_FILENAME, "rt") as servers_file:  #try to restore server states
            servers=jsonpickle.decode(servers_file.read())  #type:ignore
    except FileNotFoundError:   #if file not created yet: no server states available yet
        logging.warning(f"\rRestoring server states from \"{SERVERS_FILENAME}\" failed with FileNotFoundError.")
        servers=[]
    else:
        logging.info(f"\rRestored server states from \"{SERVERS_FILENAME}\".")


    @discord_bot.event
    async def on_ready():
        """
        Executed as soon as bot started up and is ready. Also executes after bot reconnects to the internet and is ready again. Initialised databases.
        """
        logging.info("Started discord client.")
        station_subscription.start()    #start station subscription task

        return

    @discord_bot.event
    async def on_message(message: discord.Message|Server): #either discord.Message if discord triggers or Server instance if subscription task triggers
        """
        Executed every time a message is sent on the server. If the message is not from the bot itself and in a bot channel, process it.

        - \"{ICAO code}\" requests the current METAR and changes the subscribed station.

        - \"{ICAO code} TAF\" requests the current METAR and TAF and changes the subscribed station.

        - \"{ICAO code} INFO\" requests information and does not change the subscribed station. TODO: CURRENTLY UNUSABLE.
        """

        global servers


        #keep only for this iteration
        append_TAF: bool    #append TAF?
        #INFO_command: bool  #information command?
        channel_id: int     #current channel id
        command: str        #current command
        message_send: str   #message final to discord
        METAR_o: str|None   #METAR original format
        METAR: str|None     #METAR my format
        server: Server      #server current
        station: Station    #station parsed ICAO: str, and name: str|None, elev: float|None
        TAF_o: str|None     #TAF original format
        TAF: str|None       #TAF my format


        class ContextManager():
            server: Server
            def __enter__(self):                                    #get current server, here because need access to server for force print in exit
                if isinstance(message, discord.message.Message):    #discord triggered
                    if message.guild!=None and message.guild.id not in [server.id for server in servers]:   #if server not yet in server list: append
                        servers.append(Server(message.guild.id, message.guild.name))
                    self.server=next(server for server in servers if server.id==message.guild.id)   #get current server, SHALLOW COPY which is desired #type:ignore
                elif isinstance(message, Server):   #subscription triggered
                    self.server=message 
                else:
                    logging.critical("message: discord.Message|Server has invalid type \"{type(message)}\".")
                    raise RuntimeError(f"Error in {main.__name__}{inspect.signature(main)}: message: discord.Message|Server has invalid type \"{type(message)}\".")
                return self
            def __exit__(self, exc_type, exc_value, exc_traceback): #upon exit, force print by default
                self.server.force_print=True
                return
        with ContextManager() as context:               #upon exit, force print by default
            server=context.server                       #get current server from context, SHALLOW COPY which is desired
            if isinstance(message, discord.message.Message):
                if message.author==discord_bot.user or message.channel.name not in discord_bot_channel_names:  #if message from bot itself or outside dedicated bot channel: do nothing #type:ignore
                    return
                channel_id=message.channel.id   #save active channel id
                command=message.content.upper() #save active command
            elif isinstance(message, Server): 
                channel_id=server.channel_id    #type:ignore
                command=server.command          #type:ignore
            else:
                logging.critical("message: discord.Message|Server has invalid type \"{type(message)}\".")
                raise RuntimeError(f"Error in {main.__name__}{inspect.signature(main)}: message: discord.Message|Server has invalid type \"{type(message)}\".")
            
            
            logging.info("--------------------------------------------------")
            logging.info(f"On server: {server.name} ({server.id})")     #which server are we on?
            now_DT=dt.datetime.now(dt.timezone.utc)

            #station_ICAO, append_TAF
            logging.info(f"Command: {command}")
            for command_allowed in COMMANDS_ALLOWED:                    #did message match an allowed command?
                re_match=re.search(command_allowed, command)
                if re_match==None:                                      #if message did not match this command:
                    continue
                station=Station(re_match.groupdict()["station_ICAO"])   #parse station ICAO code
                logging.info(f"Station: {station.ICAO}")
                if command.endswith("TAF")==True:                       #if message ends with TAF:
                    logging.info("TAF was requested.")
                    append_TAF=True                                     #TAF requested, append TAF later
                else:
                    append_TAF=False
                # if command.endswith("INFO"):                           #if matched command ends with INFO:
                #    logging.info("INFO was requested.")
                #    INFO_command=True                                   #INFO requested, get information later
                # else:
                #     INFO_command=False
                break                                                   #command found, exit
            else:                                                       #if message did not match any command:
                logging.error(f"Last command \"{command}\" did not match any allowed command.")
                return
            
            #station_name, station_elev
            logging.info(f"Looking for {station.ICAO} in aerodrome database...")
            aerodrome=aerodrome_DB[aerodrome_DB["ident"]==station.ICAO] #aerodrome desired
            aerodrome=aerodrome.reset_index(drop=True)
            if aerodrome.empty==True:   #if aerodrome not found in database:
                logging.warning(f"\rCould not find {station.ICAO} in aerodrome database. No title, elevation, and runway directions available.")
                station.elev=None
                station.name=None
            else:                                                                       #if aerodrome found in database:
                logging.info(f"\rFound {station.ICAO} in aerodrome database.")
                country=country_DB[country_DB["code"]==aerodrome.at[0, "iso_country"]]  #country desired
                country=country.reset_index(drop=True)
                if country.empty==True:                                                 #if country not found in database:
                    logging.warning(f"Could not find country of country code \"{aerodrome.at[0, 'iso_country']}\".")
                    station.name=f"{aerodrome.at[0, 'iso_country']}, {aerodrome.at[0, 'name']}" #enter country code, aerodrome name
                else:   #if country found in database:
                    station.name=f"{country.at[0, 'name']}, {aerodrome.at[0, 'name']}"          #enter country, aerodrome name
                logging.info(f"Name: {station.name}")

                if pandas.isna(aerodrome.at[0, "elevation_ft"])==True:  #if elevation unavailable:
                    logging.warning(f"\r{station.ICAO} has no elevation information in aerodrome database. No elevation available.")
                    station.elev=None
                else:                                                   #if elevation available:
                    station.elev=aerodrome.at[0, "elevation_ft"]*KFS.convert_to_SI.length["ft"]  #save elevation [m]
                    logging.info(f"Elevation: {KFS.fstr.notation_abs(station.elev, 0, round_static=True)}m")

            #information command
            # if INFO_command==True:  #if information command: execute that, then return without downloading METAR, TAF etc.
            #     await aerodrome_info(station, frequency_DB, navaid_DB, RWY_DB, command)
            #     return
            

            #download and convert METAR and TAF
            try:
                METAR_o, METAR=process_METAR_TAF(Doc_Type.METAR, station, RWY_DB, now_DT, server, DOWNLOAD_TIMEOUT)
            except requests.ConnectTimeout:     #if unsuccessful: abort
                logging.error(f"\rDownloading METAR timed out after {DOWNLOAD_TIMEOUT}s.")
                return
            except requests.ConnectionError:    #if unsuccessful: abort
                logging.error("\rDownloading METAR failed.")
                return
            
            if append_TAF==True:    #if append TAF: append TAF
                try:
                    TAF_o, TAF=process_METAR_TAF(Doc_Type.TAF, station, RWY_DB, now_DT, server, DOWNLOAD_TIMEOUT)
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
            if server.force_print==True:            #if force printing: no subscription
                server.channel_id=channel_id        #save active channel id, at this point known that command valid
                server.command=command              #save active command, this point known valid
                server.METAR_o_previous=METAR_o     #refresh METAR original previous
                server.TAF_o_previous=TAF_o         #refresh TAF orginal previous
                server.METAR_update_finished=False  #reset already waited for METAR
                server.TAF_update_finished=False    #reset already waited for TAF
            
            elif append_TAF==False:                                                             #subscription; if TAF undesired: disregard TAF
                if server.METAR_o_previous==METAR_o:                                            #if METAR original same as previous one: subscription, don't print
                    logging.info("Original METAR has not been changed. Not sending anything.")
                    return
                elif server.METAR_o_previous!=METAR_o and server.METAR_update_finished==False:  #if METAR original new different, but not waited yet: subscription, wait 1 round until source website refreshed METAR completely
                    logging.info("Original METAR has changed, but update process may not have been finished yet. Not sending anything yet.")
                    server.METAR_update_finished=True   
                    return
                elif server.METAR_o_previous!=METAR_o and server.METAR_update_finished==True:   #if METAR original new different and waited already: subscription, source website refreshed METAR completely, now send METAR
                    logging.info("Original METAR has changed and update process should have been finished.")
                    server.METAR_o_previous=METAR_o                                             #refresh METAR original previous
                    server.METAR_update_finished=False                                          #reset already waited for METAR
            
            elif append_TAF==True:                                                              #subscription; if TAF desiredt: regard TAF
                if server.METAR_o_previous==METAR_o and server.TAF_o_previous==TAF_o:           #if METAR original and TAF original same as previous one: subscription, don't print
                    logging.info("Original METAR and TAF have not been changed. Not sending anything.")
                    return
                elif(server.METAR_o_previous!=METAR_o and server.TAF_o_previous!=TAF_o          #if METAR original new and TAF original new different, but not waited yet: subscription, wait 1 round until source website refreshed METAR and TAF completely
                    and server.METAR_update_finished==False and server.TAF_update_finished==False):
                    logging.info("Original METAR and TAF have changed, but update process may not have been finished yet. Not sending anything yet.")
                    server.METAR_update_finished=True
                    server.TAF_update_finished=True
                    return
                elif server.METAR_o_previous!=METAR_o and server.METAR_update_finished==False:  #if METAR original new different, but not waited yet: subscription, wait 1 round until source website refreshed METAR completely
                    logging.info("Original METAR has changed, but update process may not have been finished yet. Not sending anything yet.")
                    server.METAR_update_finished=True
                    return
                elif server.TAF_o_previous!=TAF_o and server.TAF_update_finished==False:        #if TAF original new different, but not waited yet: subscription, wait 1 round until source website refreshed TAF completely
                    logging.info("Original TAF has changed, but update process may not have been finished yet. Not sending anything yet.")
                    server.TAF_update_finished=True
                    return
                elif(server.METAR_o_previous!=METAR_o and server.TAF_o_previous!=TAF_o          #if METAR original new and TAF original new different and waited already: subscription, source website refreshed METAR and TAF completely, now send METAR and TAF
                    and server.METAR_update_finished==True and server.TAF_update_finished==True):
                    logging.info("Original METAR and TAF have changed and update process should have been finished.")
                    server.METAR_o_previous=METAR_o                                             #refresh METAR original previous
                    server.TAF_o_previous=TAF_o                                                 #refresh TAF original previous
                    server.METAR_update_finished=False                                          #reset already waited for METAR
                    server.TAF_update_finished=False                                            #reset already waited for TAF
                elif server.METAR_o_previous!=METAR_o and server.METAR_update_finished==True:   #if METAR original new different and waited already: subscription, source website refreshed METAR completely, now send METAR
                    logging.info("Original METAR has changed and update process should have been finished.")
                    server.METAR_o_previous=METAR_o                                             #refresh METAR original previous
                    server.METAR_update_finished=False                                          #reset already waited for METAR
                    append_TAF=False                                                            #TAF did probably not refresh yet, subscription, only send METAR
                elif server.TAF_o_previous!=TAF_o and server.TAF_update_finished==True:         #if TAF original new different and waited already: subscription, source website refreshed TAF completely, now send METAR and TAF
                    logging.info("Original TAF has changed and update process should have been finished.")
                    server.TAF_o_previous=TAF_o                                                 #refresh TAF original previous
                    server.TAF_update_finished=False                                            #reset already waited for TAF

            #send messages
            if append_TAF==False:
                logging.info("Sending METAR and original METAR...")
            elif append_TAF==True and TAF_o!=None:
                logging.info("Sending METAR, TAF, original METAR, and original TAF...")
            elif append_TAF==True and TAF_o==None:
                logging.info("Sending METAR, original METAR, and error message...")

            message_send=""
            if station.name==None:                                          #if station name not found:
                message_send+=f"Could not find {station.ICAO} in aerodrome database. No title, elevation, and runway directions available..\n----------\n"  #send error message
            else:                                                           #if station name found:
                message_send+=f"{station.name}\n----------\n"               #send station name
            if METAR_o==None:                                               #if METAR not found:
                message_send+="There is no published METAR.\n----------\n"  #send error message
            else:                                                           #if METAR found:
                message_send+=f"```{METAR}```\n----------\n"                #send METAR
            if append_TAF==True and TAF_o==None:                            #if TAF desired and not found:
                message_send+="There is no published TAF.\n----------\n"    #send error message
            elif append_TAF==True and TAF_o!=None:                          #if TAF desired and found:
                message_send+=f"```{TAF}```\n----------\n"                  #send TAF
            if METAR_o!=None:                                               #if METAR found:
                message_send+=f"```{METAR_o}```\n----------\n"              #send METAR original too
            if append_TAF==True and TAF_o!=None:                            #if TAF desired and found:
                message_send+=f"```{TAF_o}```\n----------\n"                #send TAF original too
            if station.elev!=None:                                          #if station elevation found:
                message_send+=f"```Elevation = {KFS.fstr.notation_abs(station.elev, 0, round_static=True)}m ({KFS.fstr.notation_abs(station.elev/0.3048, 0, round_static=True)}ft)```\n----------\n".replace(",", ".")  #send station elevation
            
            if METAR_o!=None or TAF_o!=None:    #if a METAR of TAF sent: warnings
                message_send+="Only use original METAR and TAF for flight operations!\n"
                if station.name==None:          #if aerodrome not found in database
                    message_send+=f"Clouds are given as heights. Winds are assumed direct crosswind and will be marked at {KFS.fstr.notation_tech(WEATHER_MIN['CWC'], 2)}m/s or more. Variable winds are assumed direct tailwind and will be marked at {KFS.fstr.notation_tech(WEATHER_MIN['TWC'], 2)}m/s or more.\n"
                elif station.elev==None:        #if only elevation not found
                    message_send+="Clouds are given as heights.\n"
                else:                           #if everything found: default message
                    message_send+="Clouds are given as \"{coverage}{altitude}|{height}\".\n"
            
            try:
                await discord_bot.get_channel(channel_id).send(message_send)    #send message to discord #type:ignore
            except discord.errors.DiscordServerError:
                logging.error("Sending message to discord failed.")
                return
            if append_TAF==False:
                logging.info("\rSent METAR and original METAR.")
            elif append_TAF==True and TAF_o!=None:
                logging.info("\rSent METAR, TAF, original METAR, and original TAF.")
            elif append_TAF==True and TAF_o==None:
                logging.info("\rSent METAR, original METAR, and error message.")

        #save server states
        logging.info(f"Saving server states in \"{SERVERS_FILENAME}\"...")
        with open(SERVERS_FILENAME, "wt") as servers_file:                  #save servers state so subscription is remembered beyond restarts
            servers_file.write(jsonpickle.encode(servers, indent=4))        #recursively convert everything in the list to a dict so json can save it #type:ignore
        logging.info(f"\rSaved server states in \"{SERVERS_FILENAME}\".")

        return


    @discord.ext.tasks.loop(seconds=1/UPDATE_FREQUENCY) #every 100s look for updates
    async def station_subscription():
        """
        Executed every 100s for subscription logic.
        """
        global aerodrome_DB
        global country_DB
        global frequency_DB
        global navaid_DB
        global RWY_DB
        global servers


        #refresh databases
        now_DT=dt.datetime.now(dt.timezone.utc)
        aerodrome_DB=init_DB(DB_Type.aerodrome, aerodrome_DB, now_DT, DOWNLOAD_TIMEOUT)
        country_DB  =init_DB(DB_Type.country,   country_DB,   now_DT, DOWNLOAD_TIMEOUT)
        frequency_DB=init_DB(DB_Type.frequency, frequency_DB, now_DT, DOWNLOAD_TIMEOUT)
        navaid_DB   =init_DB(DB_Type.navaid,    navaid_DB,    now_DT, DOWNLOAD_TIMEOUT)
        RWY_DB      =init_DB(DB_Type.runway,    RWY_DB,       now_DT, DOWNLOAD_TIMEOUT)
        

        for server in servers:
            server.force_print=False    #subscription
            await on_message(server)    #type:ignore
        return


    while True:
        logging.info("Starting discord client...")
        try:
            await discord_bot.start(discord_bot_token)          #start discord client now
        except aiohttp.client_exceptions.ClientConnectorError:  #if temporary internet failure: retry connection
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