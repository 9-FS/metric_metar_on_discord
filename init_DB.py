import datetime as dt
import io               #CSV string -> pandas.DataFrame
import logging
import os
import pandas           #Dataframes
import re
import requests
from DB_Type import DB_Type


def init_DB(DB_type: DB_Type, DB: pandas.DataFrame, now_DT: dt.datetime, DOWNLOAD_TIMEOUT: int) -> pandas.DataFrame:
    DB_filenames: list[str]     #databases existing filenames

    
    if DB.empty==False and os.path.isfile(f"./Database/{now_DT.strftime('%Y-%m-%d')} {DB_type.name} DB.csv"):    #if database not empty and from today already existing: assume database as already loaded
        return DB
    
    DB=pandas.DataFrame()                       #clear database
    os.makedirs("./Database/", exist_ok=True)   #create database folder
        

    #from file today, load database:
    logging.info(f"Loading {DB_type.name} database from \"./Database/{now_DT.strftime('%Y-%m-%d')} {DB_type.name} DB.csv\"...")
    try:
        DB=pandas.read_csv(f"./Database/{now_DT.strftime('%Y-%m-%d')} {DB_type.name} DB.csv")
    except FileNotFoundError:
        logging.warning(f"Loading {DB_type.name} database failed, because \"./Database/{now_DT.strftime('%Y-%m-%d')} {DB_type.name} DB.csv\" does not exist.")
    except pandas.errors.EmptyDataError:
        logging.warning(f"Loaded {DB_type.name} database, but it is empty.")
    except pandas.errors.ParserError:
        logging.warning(f"Loaded {DB_type.name} database, but parsing failed.")
    else:   #if loading database successful:
        logging.info(f"\rLoaded {DB_type.name} database from \"./Database/{now_DT.strftime('%Y-%m-%d')} {DB_type.name} DB.csv\".")
        return DB


    #loading unsuccessful, download database
    logging.info(f"Downloading {DB_type.name} database...")
    try:    #Datenbank herunterladen
        DB=requests.get(DB_type.value, timeout=DOWNLOAD_TIMEOUT).text #type:ignore
        DB=pandas.read_csv(io.StringIO(DB)) #type:ignore
    except requests.ConnectionError:
        logging.warning(f"Downloading {DB_type.name} database failed.")
    except requests.ReadTimeout:
        logging.warning(f"Downloading {DB_type.name} database timed out after 10s.")
    except pandas.errors.EmptyDataError:
        logging.warning(f"Downloaded {DB_type.name} database is empty.")
    except pandas.errors.ParserError:
        logging.warning(f"Downloaded {DB_type.name} database, but parsing failed.")
    else:   #downloading successful, save
        logging.info(f"\rDownloaded and formatted {DB_type.name} database.")

        logging.info(f"Saving {DB_type.name} database in \"./Database/{now_DT.strftime('%Y-%m-%d')} {DB_type.name} DB.csv\"...") #save downloaded database
        try:    #save database
            DB.to_csv(f"./Database/{now_DT.strftime('%Y-%m-%d')} {DB_type.name} DB.csv", index=False, mode="wt")
        except OSError:
            logging.warning(f"Saving {DB_type.name} database in \"./Database/{now_DT.strftime('%Y-%m-%d')} {DB_type.name} DB.csv\" failed.")
        else:
            logging.info(f"\rSaved {DB_type.name} database in \"./Database/{now_DT.strftime('%Y-%m-%d')} {DB_type.name} DB.csv\".")
        return DB
    finally:    #finally check number of databases on harddrive, keep maximum 5
        logging.info("Looking for old databases to remove from archive...")
        DB_filenames=[filename for filename in sorted(os.listdir("./Database/")) if re.search(f"^[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] {DB_type.name} DB.csv$", filename)!=None]   #Datenbanken vorhanden
        for i in range(len(DB_filenames)-5):    #delete all databases saved except 5 most current
            logging.info(f"Removing \"./Database/{DB_filenames[i]}\"...")
            try:
                os.remove(f"./Database/{DB_filenames[i]}")
            except OSError:
                logging.warning(f"Removing \"./Database/{DB_filenames[i]}\" failed.")
            logging.info(f"\rRemoved \"./Database/{DB_filenames[i]}\".")

    #if database empty: downloading unsuccessful, load from archive
    logging.info(f"Loading {DB_type.name} database from archive...")
    DB_filenames=[filename for filename in sorted(os.listdir("./Database/")) if re.search(f"^[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] {DB_type.name} DB.csv$", filename)!=None]   #Datenbanken vorhanden

    for i in range(len(DB_filenames)-1, -1, -1):    #iterate archive from most recent to oldest
        logging.info(f"Loading {DB_type.name} database from \"./Database/{DB_filenames[i]}\"...")
        try:
            DB=pandas.read_csv(f"./Database/{DB_filenames[i]}")
        except OSError:
            logging.warning(f"Loading {DB_type.name} database from \"./Database/{DB_filenames[i]}\" failed.")
        else:   #loading successful
            logging.info(f"\rLoaded {DB_type.name} database from \"./Database/{DB_filenames[i]}\".")
            return DB

    logging.error(f"Could neither load current database, download, nor load from archive. Using empty {DB_type.name} database.")
    return pandas.DataFrame()