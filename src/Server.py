import dataclasses
import discord


@dataclasses.dataclass
class Server:
    """
    all variables for 1 server instance
    """
    
    id: int         #discord server id
    name: str       #discord server name

    channel_id: int|None=None           #active channel id, needed later for subscription
    command: str|None=None              #active command, needed later for subscription
    force_print: bool=True              #force sending to discord (after user input request) or not (subscription)
    METAR_o_previous: str|None=None     #METAR previous for subscription
    METAR_update_finished: bool=False   #has program in subscription mode waited 1 round until source website refreshed METAR completely?
    TAF_o_previous: str|None=None       #TAF previous for subscription
    TAF_update_finished: bool=False     #has program in subscription mode waited 1 round until source website refreshed TAF completely?