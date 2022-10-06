import datetime
import os
import pandas as pd     #Dataframes
import re
import requests
from io import StringIO #CSV String zu Dataframe
from KFS import KFSlog  #KFSlog


def init_DB(DB_name, DB, DT_now):
    DB_filenames=[]    #Datenbanken vorhanden Namen


    #wenn DB schon gefüllt und DB heute schon vorhanden: DB aktuell als bereits geladen annehmen
    if DB.empty==False and os.path.isfile(f"./Database/{DT_now.strftime('%Y-%m-%d')} {DB_name} DB.csv"):
        return DB
    
    DB=pd.DataFrame()   #Datenbank leeren

    #von Datei heute Datenbank laden
    KFSlog.write(f"Loading {DB_name.lower()} database from \"./Database/{DT_now.strftime('%Y-%m-%d')} {DB_name} DB.csv\"...")
    try:
        DB=pd.read_csv(f"./Database/{DT_now.strftime('%Y-%m-%d')} {DB_name} DB.csv")
    except FileNotFoundError:
        KFSlog.write(f"\rLoading {DB_name.lower()} database failed, because \"./Database/{DT_now.strftime('%Y-%m-%d')} {DB_name} DB.csv\" does not exist.")
    except pd.errors.EmptyDataError:
        KFSlog.write(f"\rLoaded {DB_name.lower()} database is empty.")
    except pd.errors.ParserError:
        KFSlog.write(f"\rParsing loaded {DB_name.lower()} database failed.")
    else:   #wenn Datenbank laden erfolgreich:
        KFSlog.write(f"\r{DB_name} database from \"./Database/{DT_now.strftime('%Y-%m-%d')} {DB_name} DB.csv\" loaded.")
        return DB


    #Laden nicht erfolgreich, Datenbank herunterladen
    KFSlog.write(f"Downloading {DB_name.lower()} database...")
    try:    #Datenbank herunterladen
        if DB_name=="Airport":
            DB=requests.get(f"https://ourairports.com/data/airports.csv", timeout=10).text
        elif DB_name=="Country":
            DB=requests.get(f"https://ourairports.com/data/countries.csv", timeout=10).text
        elif DB_name=="Frequency":
            DB=requests.get(f"https://ourairports.com/data/airport-frequencies.csv", timeout=10).text
        elif DB_name=="Navaid":
            DB=requests.get(f"https://ourairports.com/data/navaids.csv", timeout=10).text
        elif DB_name=="Runway":
            DB=requests.get(f"https://ourairports.com/data/runways.csv", timeout=10).text
        else:
            raise ValueError("Invalid database name.")
        DB=pd.read_csv(StringIO(DB))
    except requests.ConnectionError:
        KFSlog.write(f"\rDownloading {DB_name.lower()} database failed.")
    except requests.ReadTimeout:
        KFSlog.write(f"\rDownloading {DB_name.lower()} database timed out after 10s.")
    except pd.errors.EmptyDataError:
        KFSlog.write(f"\rDownloaded {DB_name.lower()} database is empty.")
    except pd.errors.ParserError:
        KFSlog.write(f"\rParsing dowloaded {DB_name.lower()} database failed.")
    else:   #Herunterladen erfolgreich, abspeichern
        KFSlog.write(f"\r{DB_name} database downloaded and formatted.")

        KFSlog.write(f"Saving {DB_name.lower()} database in \"./Database/{DT_now.strftime('%Y-%m-%d')} {DB_name} DB.csv\"...") #Datenbank speichern
        os.makedirs("Database", exist_ok=True)                                                                              #Datenbankordner erstellen
        try:
            DB.to_csv(f"./Database/{DT_now.strftime('%Y-%m-%d')} {DB_name} DB.csv", index=False, mode="wt")
        except:
            KFSlog.write(f"\rSaving {DB_name.lower()} database in \"./Database/{DT_now.strftime('%Y-%m-%d')} {DB_name} DB.csv\" failed.")
            return DB

        KFSlog.write(f"\r{DB_name} database in \"./Database/{DT_now.strftime('%Y-%m-%d')} {DB_name} DB.csv\" saved.")
        return DB
    finally:    #als letztes noch Anzahl Datenbanken abgespeichert prüfen, maximal 5 auf Festplatte halten
        KFSlog.write("Looking for old databases to remove from archive...")
        DB_filenames=[filename for filename in sorted(os.listdir("./Database/")) if re.search(f"^[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] {DB_name} DB.csv$", filename)!=None]   #Datenbanken vorhanden
        for i in range(len(DB_filenames)-5):    #Datenbanken abgespeichert alle löschen außer aktuellste 5
            os.remove(f"./Database/{DB_filenames[i]}")
            KFSlog.write(f"Removed \"./Database/{DB_filenames[i]}\".")

    #wenn Datenbank leer: Herunterladen nicht erfolgreich, aus Archiv laden
    KFSlog.write(f"Loading {DB_name.lower()} database from archive...")
    if os.path.isdir("./Database/")==True:  #wenn Archivorder vorhanden:
        DB_filenames=[filename for filename in sorted(os.listdir("./Database/")) if re.search(f"^[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9] {DB_name} DB.csv$", filename)!=None]   #Datenbanken vorhanden

        for i in range(len(DB_filenames)-1, -1, -1):    #Archiv durch von Datenbank aktuellster bis ältester
            KFSlog.write(f"Loading {DB_name.lower()} database from \"./Database/{DB_filenames[i]}\"...")
            try:
                DB=pd.read_csv(f"./Database/{DB_filenames[i]}")
            except:
                KFSlog.write(f"\rLoading {DB_name.lower()} database from \"./Database/{DB_filenames[i]}\" failed. Using empty database.")
                DB=pd.DataFrame()
            else:   #laden erfolgreich
                KFSlog.write(f"\r{DB_name} database from \"./Database/{DB_filenames[i]}\" loaded.")
                return DB
            
            if DB.empty==True:  #wenn Datenbank leer: Laden erfolgreich, aber Datei leer???
                KFSlog.write(f"\rLoading {DB_name.lower()} database from \"./Database/{DB_filenames[i]}\" was successful, but database is empty.")

    
    KFSlog.write("Archive folder \"./Database/\" does not exist.") #wenn Archivordner nicht vorhanden: Datenbank immer noch nicht geladen, leere zurückgeben
    KFSlog.write(f"{DB_name} database could neither be loaded from today's file, downloaded, nor loaded from archive. Using empty {DB_name.lower()} database.")
    return pd.DataFrame()