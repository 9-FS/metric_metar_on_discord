import re   #Regular Expressions


def change_format_RSM(info):
    if re.search("^R([0-3][0-9]|88)([LCR]|)/[0-9/][0-9/]([0-9][0-9]|//)([0-9][0-9]|//)$", info)!=None:
        bold=False
        RWY=""
        contanimation_HGT=""
        braking=""
        info_new=""

        i=0
        while i<len(info):  #durch Info durch, keine for-Schleife, weil i dort nicht änderbar
            if i==0:                    #wenn Stelle 0:
                info_new+=info[i]       #R weiterleiten
            elif i==1 or i==2:          #wenn Stelle 1 oder 2:
                RWY+=info[i]            #Piste Teil 1 weiterleiten
            elif i==3 and re.search("[LCR]", info[i])!=None:    #wenn Stelle 3 und L, C oder R:
                RWY+=info[i]                                    #Piste Teil 2 weiterleiten
                info=info[:3]+info[4:]                          #von Quelle L, C, R wegschneiden
                i-=1
            elif i==3 and re.search("[LCR]", info[i])==None:    #wenn Stelle 3 und nicht L, C oder R: Piste weiterleiten
                #if 50<=int(RWY[0:2]) and int(RWY[0:2])<=86:     #wenn Piste 50 bis 86:
                #    RWY[0]=f"{int(RWY[0])-5:.0f}"               #50 abziehen
                #    RWY+="R"                                    #R anhängen
                if RWY[0:2]=="88":                              #wenn Piste 88:
                    RWY="-ALL"                                  #Pisten alle
                #if len(RWY)==2:                                 #wenn Piste nur Zahl:
                #    RWY+="(L)"                                  #(L) anhängen
                info_new+=RWY+"/"                               #Piste und / weiterleiten
            elif i==4:  #wenn Stelle 4: Kontanimierungsart
                if   info[i]=="0":
                    info_new+="DRY/"
                elif info[i]=="1":
                    info_new+="DAMP/"
                elif info[i]=="2":
                    info_new+="WET/"
                elif info[i]=="3":
                    info_new+="FROST/"
                    bold=True
                elif info[i]=="4":
                    info_new+="SNOW-DRY/"
                    bold=True
                elif info[i]=="5":
                    info_new+="SNOW-WET/"
                    bold=True
                elif info[i]=="6":
                    info_new+="SLUSH/"
                elif info[i]=="7":
                    info_new+="ICE/"
                    bold=True
                elif info[i]=="8":
                    info_new+="SNOW-COMPACT/"
                    bold=True
                elif info[i]=="9":
                    info_new+="RUTS-FROZEN/"
                    bold=True
                elif info[i]=="/":
                    info_new+="-/"

            elif i==5:  #wenn Stelle 5: Kontanimierungsausdehnung
                if   info[i]=="1":
                    info_new+="0,1-/"
                elif info[i]=="2":
                    info_new+="0,11~0,25/"
                elif info[i]=="5":
                    info_new+="0,26~0,5/"
                elif info[i]=="9":
                    info_new+="0,51~1/"
                elif info[i]=="/":
                    info_new+="-/"
                else:
                    info_new+="-/"

            elif i==6:                      #wenn Stelle 6:
                contanimation_HGT=info[i]   #Kontanimierungstiefe Teil 1
            elif i==7:                      #wenn Stelle 7: Kontanimierungstiefe Teil 2, Auswertung
                contanimation_HGT+=info[i]  #Kontanimierungstiefe Teil 2
                if contanimation_HGT=="//" or contanimation_HGT=="91":  #wenn // oder Code invalid: -- weiterleiten
                    info_new+="--/"
                    i+=1
                    continue
                contanimation_HGT=int(contanimation_HGT)                #wenn nicht //: in Zahl umwandeln, Auswertung
                if   contanimation_HGT==0:
                    info_new+="1mm-/"
                elif  1<=contanimation_HGT and contanimation_HGT<=90:
                    info_new+=f"{contanimation_HGT}mm/"
                elif 92<=contanimation_HGT and contanimation_HGT<=97:
                    info_new+=f"{(contanimation_HGT-90)*50}mm/"
                elif contanimation_HGT==98:
                    info_new+="400mm+/"
                elif contanimation_HGT==99:
                    info_new+="RWY-INOP/"

            elif i==8:                  #wenn Stelle 8: Bremsmaß Teil 1
                braking=info[i]
            elif i==9:                  #wenn Stelle 9: Bremsmaß Teil 2, Auswertung
                braking+=info[i]        #Bremsmaß Teil 2
                if braking=="//":       #wenn //: -- weiterleiten
                    info_new+="--"
                    i+=1
                    continue
                braking=int(braking)    #wenn nicht //: in Zahl umwandlen, Auswertung
                if  ( 0<=braking and braking<=25) or braking==91:
                    info_new+="BAD"
                    bold=True
                elif(26<=braking and braking<=29) or braking==92:
                    info_new+="BAD~MEDIUM"
                    bold=True
                elif(30<=braking and braking<=35) or braking==93:
                    info_new+="MEDIUM"
                elif(36<=braking and braking<=39) or braking==94:
                    info_new+="MEDIUM~GOOD"
                elif(40<=braking and braking<=90) or braking==95:
                    info_new+="GOOD"
                elif braking==99:
                    info_new+="UNRELIABLE"

            i+=1
        if bold==True:
            info_new=f"*{info_new}*"
        return "\n"+info_new

    if re.search("^R([0-3][0-9]|88)([LCR]|)/CLRD//$", info)!=None:
        RWY=""
        info_new=""

        i=0
        while i<len(info):              #durch Info durch, keine for-Schleife, weil i dort nicht änderbar
            if i==0:                    #wenn Stelle 0:
                info_new+=info[i]       #R weiterleiten
            elif i==1 or i==2:          #wenn Stelle 1 oder 2:
                RWY+=info[i]            #Piste Teil 1 weiterleiten
            elif i==3 and re.search("[LCR]", info[i])!=None:    #wenn Stelle 3 und L, C oder R:
                RWY+=info[i]                                    #Piste Teil 2 weiterleiten
                info=info[:3]+info[4:]                          #von Quelle L, C, R wegschneiden
                i-=1
            elif i==3 and re.search("[LCR]", info[i])==None:    #wenn Stelle 3 und nicht L, C oder R: Piste weiterleiten
                #if 50<=int(RWY[0:2]) and int(RWY[0:2])<=86:     #wenn Piste 50 bis 86:
                #    RWY[0]=f"{int(RWY[0])-5:.0f}"               #50 abziehen
                #    RWY+="R"                                    #R anhängen
                if RWY[0:2]=="88":                            #wenn Piste 88:
                    RWY="-ALL"                                  #Pisten alle
                #if len(RWY)==2:                                 #wenn Piste nur Zahl:
                #    RWY+="(L)"                                  #(L) anhängen
                info_new+=RWY+"/"                               #Piste und / weiterleiten

                info_new+="CLRD"                                #gesäubert weiterleiten
                break
            i+=1
        return "\n"+info_new

    if info=="R/SNOCLO":
        return "\n"+f"**{info}**"