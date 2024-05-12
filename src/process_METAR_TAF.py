# Copyright (c) 2024 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import datetime as dt
import inspect
import logging
import pandas
import re
import requests
from change_format     import change_format     # change information format
from change_format_RMK import change_format_RMK # in remark section change information format
from Doc_Type          import Doc_Type          # processing METAR or TAF?
from KFSfstr           import KFSfstr
from Server            import Server
from Station           import Station


def process_METAR_TAF(doc_type: Doc_Type, station: Station, RWY_DB: pandas.DataFrame, now_DT: dt.datetime, server: Server, DOWNLOAD_TIMEOUT: float) -> tuple[str|None, str|None]:
    """
    Processes whole METAR or TAF, from downloading, cleaning up, looking whether it is expired or not, changing format, to returning in both original format and my format.
    """

    
    met_report_DT: dt.datetime          # publishion datetime
    METAR_TAF_o: requests.Response|str  # METAR or TAF original format
    METAR_TAF_o_list: list              # METAR or TAF original format as list, separated at blank and newline
    METAR_TAF=""                        # METAR or TAF my format
    METAR_TAF_URL: str                  # URL to download from
    RMK_section=False                   # now in remark section?
    timespan_published: dt.timedelta    # how long ago published

    match doc_type:
        case Doc_Type.METAR:
            METAR_TAF_URL=f"http://tgftp.nws.noaa.gov/data/observations/metar/stations/{station.ICAO}.TXT"
        case Doc_Type.TAF:
            METAR_TAF_URL=f"http://tgftp.nws.noaa.gov/data/forecasts/taf/stations/{station.ICAO}.TXT"
        case _:
            logging.critical(f"Document type ({doc_type}) is neither {Doc_Type.METAR} nor {Doc_Type.TAF}.")
            raise RuntimeError(f"Error in {process_METAR_TAF.__name__}{inspect.signature(process_METAR_TAF)}: Document type ({doc_type}) is neither {Doc_Type.METAR} nor {Doc_Type.TAF}.")
    

    # download METAR or TAF
    logging.info(f"Downloading {doc_type.name}...")
    try:
        METAR_TAF_o=requests.get(METAR_TAF_URL, timeout=DOWNLOAD_TIMEOUT)   # download METAR or TAF
    except requests.ConnectionError as e:                                   # if unsuccessful: abort
        logging.error(f"\rDownloading {doc_type.name} failed with {KFSfstr.full_class_name(e)}. Error message: {e.args}")
        raise
    else:
        logging.info(f"\rDownloaded {doc_type.name}.")
    if METAR_TAF_o.ok==False:                                               # if something went wrong
        match METAR_TAF_o.status_code:
            case 403:                                                       # if forbidden: resource temporarily unavailable, probably update
                logging.error(f"{station.ICAO} {doc_type.name} is currently unavailable.")
                raise ValueError(f"Error in {process_METAR_TAF.__name__}{inspect.signature(process_METAR_TAF)}: {station.ICAO} {doc_type.name} is currently unavailable.")
            case 404:                                                       # if NOAA has no METAR or TAF page: station has no METAR or TAF
                logging.error(f"{station.ICAO} does not publish any {doc_type.name}.")
                return None, None                                           # return None to continue outside to send message that station does not publish METAR or TAF
            case _:
                logging.error(f"Downloading {station.ICAO} {doc_type.name} failed with status code {METAR_TAF_o.status_code}.")
                raise ValueError(f"Error in {process_METAR_TAF.__name__}{inspect.signature(process_METAR_TAF)}: Downloading {station.ICAO} {doc_type.name} failed with status code {METAR_TAF_o.status_code}.")
    

    METAR_TAF_o=METAR_TAF_o.text                                                                # requests.Response -> str
    METAR_TAF_o="\n".join([info.strip() for info in re.split("\n", METAR_TAF_o) if info!=""])   # METAR or TAF original format, separate at newline, remove empty infos, strip infos, rejoin at newline
    METAR_TAF_o_list=[info.strip() for info in re.split("[ \n]", METAR_TAF_o) if info!=""]      # METAR or TAF original format as list, separated at blank and newline, remove empty infos, strip infos
    logging.info(METAR_TAF_o)

    if METAR_TAF_o=="": # if METAR or TAF exists but empty string:
        return "", ""   # that's the METAR or TAF lol, but don't process
    

    # METAR or TAF expired?
    for info in METAR_TAF_o_list:                                                                       # look for publishion datetime
        re_match=re.search("^(?P<day>[0-3][0-9])(?P<hour>[0-2][0-9])(?P<minute>[0-5][0-9])Z$", info)    # look for met report time group
        if re_match==None:                                                                              # if not day time info: next
            continue
        
        met_report_DT=dt.datetime(int(METAR_TAF_o[0:4]), int(METAR_TAF_o[5:7]), int(METAR_TAF_o[8:10]), 0, 0, 0, 0, dt.timezone.utc)    # met report date according header for year and month, next fill out rest with met report time info
        while int(met_report_DT.strftime("%d"))!=int(re_match.groupdict()["day"]):                                                      # as long as days not matching: met report datetime must be before website refresh, decrement day until same
            met_report_DT-=dt.timedelta(days=1)                                                                                         # decrement day
        met_report_DT+=dt.timedelta(hours=int(re_match.groupdict()["hour"]), minutes=int(re_match.groupdict()["minute"]))               # correct day now, add time according met report time info
        break
    else:   # if met report time info not found: use website publishion datetime as fallback
        logging.warning(f"{doc_type.name} report time info could not be found.")
        logging.info("Using NOAA website publishion datetime as fallback...")
        try:
            met_report_DT=dt.datetime(int(METAR_TAF_o[0:4]), int(METAR_TAF_o[5:7]), int(METAR_TAF_o[8:10]), int(METAR_TAF_o[11:13]), int(METAR_TAF_o[14:16]), 0, 0, dt.timezone.utc)    # publision datetime according header
        except ValueError:
            logging.error(f"\rUsing NOAA website publishion datetime as fallback failed. The downloaded {doc_type.name} does not seem to be valid.")
            raise
        else:
            logging.info("\rUsed NOAA website publishion datetime as fallback.")
    METAR_TAF_o     =METAR_TAF_o[17:]       # remove website publishion header
    METAR_TAF_o_list=METAR_TAF_o_list[2:]   # remove website publishion header 

    timespan_published=now_DT-met_report_DT                 # timespan published
    if   doc_type==Doc_Type.METAR:
        if dt.timedelta(seconds=3600) <timespan_published:  # if METAR expired:
            METAR_TAF+="**EXPIRED** "                       # mark
    elif doc_type==Doc_Type.TAF:
        if dt.timedelta(seconds=86400)<timespan_published:  # if TAF expired:
            METAR_TAF+="**EXPIRED** "                       # mark
    else:
        logging.critical(f"Document type ({doc_type}) is neither {Doc_Type.METAR} nor {Doc_Type.TAF}.")
        raise RuntimeError(f"Error in {process_METAR_TAF.__name__}{inspect.signature(process_METAR_TAF)}: Document type ({doc_type}) is neither {Doc_Type.METAR} nor {Doc_Type.TAF}.")

    # convert METAR or TAF
    logging.info(f"Converting {doc_type.name}...")
    i=0
    while i<len(METAR_TAF_o_list):                                                                          # iterate through all METAR or TAF infos, while loop to be able to delete infos if needed
        logging.debug(f"Converting \"{METAR_TAF_o_list[i]}\"...")
        if RMK_section==True:                                                                               # if in remark section:
            info_new=change_format_RMK(METAR_TAF_o_list, i, station, met_report_DT, RWY_DB)                 # info new to append to METAR or TAF, change_format_RMK(...) adds separating chars as needed
        else:
            info_new=change_format    (METAR_TAF_o_list, i, station, met_report_DT, now_DT, RWY_DB, server) # info new to append to METAR or TAF, change_format(...) adds separating chars as needed

        if re.search("^(RMK|FIRST|LAST)$", info_new.strip())!=None: # if info new RMK marker or RMK marker indirectly:
            RMK_section=True                                        # RMK section following
            info_new=f"\n{info_new.strip()}"                        # info current should start with linebreak, not default space
        
        logging.debug(f"\rConverted \"{METAR_TAF_o_list[i]}\" to \"{info_new}\".")
        METAR_TAF+=info_new # append info new
        i+=1
    
    METAR_TAF=METAR_TAF.strip()
    logging.debug("")
    logging.info(f"\rConverted {doc_type.name}.")
    logging.info(METAR_TAF)

    return METAR_TAF_o, METAR_TAF