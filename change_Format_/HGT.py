import re   #Regular Expressions
import KFS.math


def change_Format_HGT(info, station_elev):
    if re.search("^([0-9]|)([0-9]|)([0-9]|)[0-9]FT$", info)!=None:
        if station_elev=="":    #wenn Flughafenhöhe unbekannt:
            station_elev=0      #Höhen als AGL schreiben

        HGT=""          #Höhenangabe wirklich AGL? Da nicht sicher, wird Elev nicht draufgerechnet
        info_new=""

        for i in range(len(info)):
            if   re.search("[0-9]", info[i])!=None:   #wenn Zahl:
                HGT+=info[i]                          #HGT Teil
            elif re.search("[A-Z]", info[i])!=None:   #wenn Buchstabe:
                if 0<len(HGT):                        #wenn HGT im Buffer: konvertieren und weiterleiten
                    info_new+=f"{KFS.math.round_sig(int(HGT)*0.3048, 2)}m"
                    HGT=""
                info_new+=info[i]
        return " "+info_new.replace("FT", "")