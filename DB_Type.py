import enum


class DB_Type(enum.Enum):
    """
    Which database on \"https://ourairports.com/data/\"?
    """

    aerodrome="https://ourairports.com/data/airports.csv"               #aerodrome database
    country  ="https://ourairports.com/data/countries.csv"              #country database for country names
    frequency="https://ourairports.com/data/airport-frequencies.csv"    #frequency database for information command
    navaid   ="https://ourairports.com/data/navaids.csv"                #navaid database for information command
    runway   ="https://ourairports.com/data/runways.csv"                #runway database for cross wind components and information command