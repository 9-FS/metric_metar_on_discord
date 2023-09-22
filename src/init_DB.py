# Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import datetime as dt
import io   # CSV string -> pandas.DataFrame
import logging
import os
import pandas
import re
import requests
from DB_Type import DB_Type


def init_DB(DB_type: DB_Type, DB: pandas.DataFrame, now_DT: dt.datetime, DOWNLOAD_TIMEOUT: int) -> pandas.DataFrame:
    DB_filenames: list[str]                                                                     # databases existing filenames
    DB_filepath: str                                                                            # filepath to database, date can be in past
    DB_TODAY_FILEPATH: str=f"./database/{now_DT.strftime('%Y-%m-%d')} {DB_type.name} DB.csv"    # filepath to database

    
    if DB.empty==False and os.path.isfile(DB_TODAY_FILEPATH):   # if database not empty and from today already existing: assume database as already loaded
        return DB
    
    DB=pandas.DataFrame()                                           # clear database
    os.makedirs(os.path.dirname(DB_TODAY_FILEPATH), exist_ok=True)  # create database folder


    # from file today, load database:
    logging.info(f"Loading {DB_type.name} database from \"{DB_TODAY_FILEPATH}\"...")
    try:    # load database
        DB=pandas.read_csv(f"{DB_TODAY_FILEPATH}")
    except FileNotFoundError:
        logging.warning(f"Loading {DB_type.name} database failed, because \"{DB_TODAY_FILEPATH}\" does not exist.")
    except pandas.errors.EmptyDataError:
        logging.warning(f"Loaded {DB_type.name} database, but it is empty.")
    except pandas.errors.ParserError:
        logging.warning(f"Loaded {DB_type.name} database, but parsing failed.")
    else:   # if loading database successful:
        logging.info(f"\rLoaded {DB_type.name} database from \"{DB_TODAY_FILEPATH}\".")
        return DB


    # loading unsuccessful, download database
    logging.info(f"Downloading {DB_type.name} database...")
    try:                                                                                # download database
        DB=requests.get(DB_type.value, timeout=DOWNLOAD_TIMEOUT).text                   # type:ignore
        DB=pandas.read_csv(io.StringIO(DB))                                             # type:ignore
    except requests.ConnectionError:
        logging.warning(f"Downloading {DB_type.name} database failed with requests.ConnectionError.")
    except requests.ReadTimeout:
        logging.warning(f"Downloading {DB_type.name} database timed out after 10s.")
    except pandas.errors.EmptyDataError:
        logging.warning(f"Downloaded {DB_type.name} database is empty.")
    except pandas.errors.ParserError:
        logging.warning(f"Downloaded {DB_type.name} database, but parsing failed.")
    else:                                                                               # downloading successful, save
        logging.info(f"\rDownloaded and formatted {DB_type.name} database.")

        logging.info(f"Saving {DB_type.name} database in \"{DB_TODAY_FILEPATH}\"...")   # save downloaded database
        try:                                                                            # save database
            DB.to_csv(DB_TODAY_FILEPATH, index=False, mode="wt")
        except OSError:
            logging.warning(f"Saving {DB_type.name} database in \"{DB_TODAY_FILEPATH}\" failed.")
        else:
            logging.info(f"\rSaved {DB_type.name} database in \"{DB_TODAY_FILEPATH}\".")
        return DB
    finally:                                                                            # finally check number of databases on harddrive, keep maximum 5
        logging.info("Looking for old databases to remove from archive...")
        DB_filenames=[filename                                                          # load databases existing
                      for filename in sorted(os.listdir(os.path.dirname(DB_TODAY_FILEPATH)))
                      if re.search(f"^[0-9]{4}-[0-1][0-9]-[0-3][0-9] {DB_type.name} DB.csv$", filename)!=None]
        for i in range(len(DB_filenames)-5):                                            # delete all databases saved except 5 most current
            DB_filepath=os.path.join(os.path.dirname(DB_TODAY_FILEPATH), DB_filenames[i])
            logging.info(f"Removing \"{DB_filepath}\"...")
            try:
                os.remove(DB_filepath)
            except OSError:
                logging.warning(f"Removing \"{DB_filepath}\" failed with OSError.")
            logging.info(f"\rRemoved \"{DB_filepath}\".")

    # if database empty: downloading unsuccessful, load from archive
    logging.info(f"Loading {DB_type.name} database from archive...")
    DB_filenames=[filename  # load databases existing
                  for filename in sorted(os.listdir(os.path.dirname(DB_TODAY_FILEPATH)))
                  if re.search(f"^[0-9]{4}-[0-1][0-9]-[0-3][0-9] {DB_type.name} DB.csv$", filename)!=None]

    for i in range(len(DB_filenames)-1, -1, -1):    # iterate archive from most recent to oldest
        DB_filepath=os.path.join(os.path.dirname(DB_TODAY_FILEPATH), DB_filenames[i])
        logging.info(f"Loading {DB_type.name} database from \"{DB_filepath}\"...")
        try:
            DB=pandas.read_csv(DB_filepath)
        except OSError:
            logging.warning(f"Loading {DB_type.name} database from \"{DB_filepath}\" failed with OSError.")
        else:                                       # loading successful
            logging.info(f"\rLoaded {DB_type.name} database from \"{DB_filepath}\".")
            return DB

    logging.error(f"Could neither load current database, download, nor load from archive. Using empty {DB_type.name} database.")
    DB=pandas.DataFrame()
    return DB