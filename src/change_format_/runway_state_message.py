#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import re   #Regular Expressions


def change_format_RSM(info: str) -> str|None:
    re_match: re.Match|None

    DEPOSIT={
        "0": ("DRY",          False),
        "1": ("DAMP",         False),
        "2": ("WET",          False),
        "3": ("FROST",        True),
        "4": ("SNOW:DRY",     True),
        "5": ("SNOW:WET",     True),
        "6": ("SLUSH",        True),
        "7": ("ICE",          True),
        "8": ("SNOW:COMPACT", True),
        "9": ("RUTS:FROZEN",  True),
        "/": ("-",            False)
    }

    EXTENT={
        "1": "0,1-",
        "2": "0,11~0,25",
        "5": "0,26~0,5",
        "9": "0,51~1",
        "/": "-"
    }

    DEPTH={
        "00": ("1mm-",     False),
        "91": ("--",       False),
        "98": ("400mm+",   False),
        "99": ("RWY:INOP", True),
        "//": ("--",       False)
    }
    for d in range(1, 90+1):
        DEPTH[f"{d:02}"]=(f"{d}mm",         False)
    for d in range(92, 97+1):
        DEPTH[f"{d:02}"]=(f"{(d-90)*50}mm", False)

    BRAKING={
        "91": ("BAD",         True),
        "92": ("BAD~MEDIUM",  True),
        "93": ("MEDIUM",      False),
        "94": ("MEDIUM~GOOD", False),
        "95": ("GOOD",        False),
        "99": ("UNRELIABLE",  True),
        "//": ("--",          False)
    }
    for b in range(0, 25+1):
        BRAKING[f"{b:02}"]=("BAD",         True)
    for b in range(26, 29+1):
        BRAKING[f"{b:02}"]=("BAD~MEDIUM",  True)
    for b in range(30, 35+1):
        BRAKING[f"{b:02}"]=("MEDIUM",      False)
    for b in range(36, 39+1):
        BRAKING[f"{b:02}"]=("MEDIUM~GOOD", False)
    for b in range(40, 90+1):
        BRAKING[f"{b:02}"]=("GOOD",        False)


    #runway state message
    re_match=re.search("^R(?P<runway>[0-3][0-9]([LCR])?)/(?P<deposit>[0-9]|/)(?P<extent>[0-9]|/)(?P<depth>[0-9][0-9]|//)(?P<braking>[0-9][0-9]|//)$", info)
    if re_match!=None:
        braking: str
        braking_bold: bool
        deposit: str
        deposit_bold: bool
        depth: str
        depth_bold: bool
        extent: str
        runway: str
        info_new: str

        runway=re_match.groupdict()["runway"]
        if runway=="88":    #if runway 88: all runways
            runway=":ALL"
        try:
            deposit, deposit_bold=DEPOSIT[re_match.groupdict()["deposit"]]
        except KeyError:
            deposit, deposit_bold=("-", False)
        try:
            extent=EXTENT[re_match.groupdict()["extent"]]
        except KeyError:
            extent="-"
        try:
            depth, depth_bold=DEPTH[re_match.groupdict()["depth"]]
        except KeyError:
            depth, depth_bold=("--", False)
        try:
            braking, braking_bold=BRAKING[re_match.groupdict()["braking"]]
        except KeyError:
            braking, braking_bold=("--", False)
        

        info_new=f"R{runway}/{deposit}/{extent}/{depth}/{braking}"
        
        if braking_bold==True or deposit_bold==True or depth_bold==True:
            info_new=f"**{info_new}**"
        return f"\n{info_new}"


    #runway cleared
    re_match=re.search("^R([0-3][0-9]|88)([LCR]|)/CLRD//$", info)
    if re_match!=None:
        info_new: str
        runway: str

        runway=re_match.groupdict()["runway"]
        if runway=="88":
            runway=":ALL"


        info_new=f"R{runway}/CLRD"
        
        return f"\n{info_new}"
        

    #aerodrome snow closed
    if info=="R/SNOCLO":
        return f"\n**{info}**"