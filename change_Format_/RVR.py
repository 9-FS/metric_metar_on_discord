import re   #Regular Expressions
from KFS import KFSfstr


def change_format_RVR(info):
    if(   re.search("^R[0-3][0-9]([LCR]|)/([PM]|)[0-9][0-9][0-9][0-9]([UND]|)$", info)!=None
       or re.search("^R[0-3][0-9]([LCR]|)/([PM]|)[0-9][0-9][0-9][0-9]V[0-9][0-9][0-9][0-9]([UND]|)$", info)!=None):
        slash_found=False
        RVR=""
        info_new=""

        for i in range(len(info)):
            if   slash_found==False and re.search("[0-9A-Z]", info[i])!=None:   #wenn noch kein Slash und Buchstabe oder Zahl:
                info_new+=info[i]                                               #weiterleiten
            elif slash_found==False and info[i]=="/":                           #wenn noch kein Slash und Slash gefunden:
                slash_found=True                                                #gefunden
                info_new+=info[i]                                               #weiterleiten
            elif slash_found==True and re.search("[PM]", info[i])!=None:        #wenn Slash gefundenund Buchstabe P oder M:
                info_new+=info[i]                                               #weiterleiten
            elif slash_found==True and re.search("[0-9]", info[i])!=None:       #wenn Slash gefunden und Zahl:
                RVR+=info[i]                                                    #RVR Teil
            elif slash_found==True and info[i]=="V":                            #wenn Slash gefunden und Buchstabe V
                if 0<len(RVR):                                                  #wenn RVR im Buffer: konvertieren und weiterleiten
                    if 1e3<=int(RVR):
                        info_new+=f"{KFSfstr.notation_tech(RVR, 2)}m"
                    else:
                        info_new+=f"{KFSfstr.notation_tech(RVR, 3)}m"
                    RVR=""
                info_new+=info[i]
            elif slash_found==True and re.search("[UND]", info[i])!=None:       #wenn Slash gefunden und Buchstabe U, N, D
                if 0<len(RVR):                                                  #wenn RVR im Buffer: konvertieren und weiterleiten
                    if 1e3<=int(RVR):
                        info_new+=f"{KFSfstr.notation_tech(RVR, 2)}m/"
                    else:
                        info_new+=f"{KFSfstr.notation_tech(RVR, 3)}m/"
                    RVR=""
                info_new+=info[i]
            if i==len(info)-1:                                                  #wenn Durchgang letzter:
                if 0<len(RVR):                                                  #wenn RVR im Buffer: konvertieren und weiterleiten
                    if 1e3<=int(RVR):
                        info_new+=f"{KFSfstr.notation_tech(RVR, 2)}m"
                    else:
                        info_new+=f"{KFSfstr.notation_tech(RVR, 3)}m"
        return " "+info_new

    if(   re.search("^R[0-3][0-9]([LCR]|)/([PM]|)[0-9][0-9][0-9][0-9]FT(/[UND]|)$", info)!=None
       or re.search("^R[0-3][0-9]([LCR]|)/([PM]|)[0-9][0-9][0-9][0-9]V([PM]|)[0-9][0-9][0-9][0-9]FT(/[UND]|)$", info)!=None):
        slash_found=False
        RVR=""
        info_new=""

        for i in range(len(info)):
            if   slash_found==False and re.search("[0-9A-Z]", info[i])!=None:   #wenn noch kein Slash und Buchstabe oder Zahl:
                info_new+=info[i]                                               #weiterleiten
            elif slash_found==False and info[i]=="/":                           #wenn noch kein Slash und Slash gefunden:
                slash_found=True                                                #gefunden
                info_new+=info[i]                                               #weiterleiten
            elif slash_found==True and re.search("[PM]", info[i])!=None:        #wenn Slash gefundenund Buchstabe P oder M:
                info_new+=info[i]                                               #weiterleiten
            elif slash_found==True and re.search("[0-9]", info[i])!=None:       #wenn Slash gefunden und Zahl:
                RVR+=info[i]                                                    #RVR Teil
            elif slash_found==True and re.search("[A-Z/]", info[i])!=None:      #wenn Slash gefunden und Buchstabe oder Slash
                if 0<len(RVR):                                                  #wenn RVR im Buffer: konvertieren und weiterleiten
                    info_new+=f"{KFSfstr.notation_tech(int(RVR)*0.3048, 2)}m"
                    RVR=""
                info_new+=info[i]
        return " "+info_new.replace("FT", "")