# Copyright (c) 2024 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import enum


class DB_Type(enum.Enum):
    """
    Which database on \"https://ourairports.com/data/\"?
    """

    aerodrome="https://davidmegginson.github.io/ourairports-data/airports.csv"  # aerodrome database
    country  ="https://davidmegginson.github.io/ourairports-data/countries.csv" # country database for country names
    # navaid   ="https://davidmegginson.github.io/ourairports-data/navaids.csv"   # navaid database for information command
    runway   ="https://davidmegginson.github.io/ourairports-data/runways.csv"   # runway database for cross wind components and information command