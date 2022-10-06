import re   #Regular Expressions


def change_format_clouds(info, station_elev):
    if re.search("^(FEW|SCT|BKN|OVC)[0-9][0-9][0-9]", info)!=None:
        if station_elev==None:  #wenn Flughafenhöhe unbekannt:
            station_elev=0      #Höhen als AGL schreiben

        HGT=int(info[3:6])*100*0.3048   #Höhe AGL
        ALT=HGT+station_elev            #Höhe MSL

        if HGT==0 and round(ALT)!=round(HGT):                                                       #wenn HGT==0 und gerundet HGT!=ALT:
            info_new=f"{info[0:3]}{ALT:,.0f}m|{HGT:,.0f}m".replace(",", ".")                        #ALT=Elevation
        elif HGT==0 and round(ALT)==round(HGT):                                                     #wenn HGT==0 und gerundet HGT==ALT:
            info_new=f"{info[0:3]}{ALT:,.0f}m".replace(",", ".")                                    #ALT=Elevation, HGT nicht anhängen

        elif 0<HGT and HGT<10000*0.3048 and round(ALT, -1)!=round(HGT, -1):                         #wenn 0<HGT<10.000ft (3.000m) und gerundet HGT!=ALT:
            info_new=f"{info[0:3]}{round(ALT, -1):,.0f}m|{round(HGT, -1):,.0f}m".replace(",", ".")  #ALT und HGT auf 10m runden
        elif 0<HGT and HGT<10000*0.3048 and round(ALT, -1)==round(HGT, -1):                         #wenn 0<HGT<10.000ft (3.000m) und gerundet HGT==ALT:
            info_new=f"{info[0:3]}{round(ALT, -1):,.0f}m".replace(",", ".")                         #ALT auf 10m runden, HGT nicht anhängen

        elif 10000*0.3048<=HGT and round(ALT, -2)!=round(HGT, -2):                                  #wenn 10.000ft (3.000m)<=HGT
            info_new=f"{info[0:3]}{round(ALT, -2):,.0f}m|{round(HGT, -2):,.0f}m".replace(",", ".")  #ALT und HGT auf 100m runden
        elif 10000*0.3048<=HGT and round(ALT, -2)==round(HGT, -2):                                  #wenn 10.000ft (3.000m)<=HGT
            info_new=f"{info[0:3]}{round(ALT, -2):,.0f}m".replace(",", ".")                         #ALT auf 100m runden, HGT nicht anhängen

        if 6<len(info):                 #wenn 6<Infolänge:
            info_new+=f"|{info[6:]}"    #meist TCU oder CB, anhängen

        if 6<len(info) and info[6:8]=="CB":                             #wenn CB: markieren
            info_new=f"**{info_new}**"
        elif re.search("BKN|OVC", info[0:3])!=None and HGT<1500*0.3048: #Ceil min. AGL 1.500ft (460m)
            info_new=f"**{info_new}**"

        return " "+info_new