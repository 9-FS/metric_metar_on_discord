import dataclasses


@dataclasses.dataclass
class Station:
    """
    represents 1 aeronautical station (aerodrome)
    """

    ICAO: str               # station ICAO code
    name: str|None=None     # station name
    elev: float|None=None   # station elevation [m]