import dataclasses
import datetime as dt


@dataclasses.dataclass
class Server:
    """
    all variables for 1 server instance
    """
    
    id: int                             #discord server id
    name: str                           #discord server name

    force_print: bool=True              #force sending to discord (after user input request) or not (subscription)
    message_previous: str|None=None     #message previous for subscription
    METAR_o_previous: str|None=None     #METAR previous for subscription
    METAR_update_finished: bool=False   #has program in subscription mode waited 1 round until source website refreshed METAR completely?
    TAF_o_previous: str|None=None       #TAF previous for subscription
    TAF_update_finished: bool=False     #has program in subscription mode waited 1 round until source website refreshed TAF completely?