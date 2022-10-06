import re   #Regular Expressions
from KFS import KFSfstr


def change_format_vis(info_list, i):
    if re.search("9999", info_list[i])!=None:
        info_list[i]="10km+"
        return " "+info_list[i]

    if re.search("^([PM]|)[0-9][0-9][0-9][0-9](N|NE|E|SE|S|SW|W|NW|)$", info_list[i])!=None:
        bold=False
        vis=""
        info_new=""

        for j in range(len(info_list[i])):
            if   re.search("[0-9]", info_list[i][j])!=None: #wenn Zahl:
                vis+=info_list[i][j]                        #Vis Teil
            elif re.search("[A-Z]", info_list[i][j])!=None: #wenn Buchstabe:
                if 0<len(vis):                              #wenn Vis im Buffer: konvertieren und weiterleiten
                    if 5e3<=int(vis):
                        info_new+=f"{KFSfstr.notation_tech(int(vis), 1)}m/"
                    else:
                        info_new+=f"{KFSfstr.notation_tech(int(vis), 2)}m/"
                        bold=True                           #Vis min. 5km
                    vis=""
                info_new+=info_list[i][j]
            if j==len(info_list[i])-1:                      #wenn Durchgang letzter:
                if 0<len(vis):                              #wenn Vis im Buffer: konvertieren und weiterleiten
                    if 5e3<=int(vis):
                        info_new+=f"{KFSfstr.notation_tech(int(vis), 1)}m"
                    else:
                        info_new+=f"{KFSfstr.notation_tech(int(vis), 2)}m"
                        bold=True                           #Vis min. 5km

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^([0-9]|)[0-9]KM$", info_list[i])!=None:
        bold=False
        vis=""
        info_new=""

        for j in range(len(info_list[i])):
            if   re.search("[0-9]", info_list[i][j])!=None: #wenn Zahl:
                vis+=info_list[i][j]                        #Vis Teil
            elif re.search("[A-Z]", info_list[i][j])!=None: #wenn Buchstabe:
                if 0<len(vis):                              #wenn Vis im Buffer: konvertieren und weiterleiten, Buchstaben ignorieren
                    if 5e3<=int(vis)*1e3:
                        info_new+=f"{KFSfstr.notation_tech(int(vis)*1e3, 2)}m"
                    else:
                        info_new+=f"{KFSfstr.notation_tech(int(vis)*1e3, 2)}m"
                        bold=True                           #Vis min. 5km
                    break

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^([PM]|)([0-9]|)[0-9]SM$", info_list[i])!=None:
        bold=False
        vis=""
        info_new=""

        for j in range(len(info_list[i])):
            if re.search("[0-9]", info_list[i][j])!=None:   #wenn Zahl:
                vis+=info_list[i][j]                        #Vis Teil
            elif re.search("[A-Z]", info_list[i][j])!=None: #wenn Buchstabe:
                if 0<len(vis):                              #wenn Vis im Buffer: konvertieren und weiterleiten
                    info_new+=f"{KFSfstr.notation_tech(int(vis)*1609.344, 2)}m"
                    if int(vis)<3:                          #Vis min 3SM (4,8km)
                        bold=True
                    vis=""
                info_new+=info_list[i][j]
        info_new=info_new.replace("SM", "")

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new
    
    try:
        if re.search("^[0-9]$", info_list[i])!=None and re.search("^[0-9]/[0-9]SM$", info_list[i+1])!=None:             #wenn einzelne Ziffer a Teil von Sicht "a b/cSM":
            info_list[i+1]=f"{int(info_list[i+1][0])+int(info_list[i])*int(info_list[i+1][2])}/{info_list[i+1][2]}SM"   #Umwandeln in einzelnen Bruch (b+a*c)/c
            info_list.pop(i)    #einzelne Zahl a entfernen
    except IndexError:          #Wenn Exception weil nächstes Element nicht existiert:
        pass                    #nix tun

    if re.search("^([PM]|)([0-9]|)[0-9]/([0-9]|)[0-9]SM$", info_list[i])!=None:
        bold=False
        slash_found=False
        vis1=""
        vis2=""
        info_new=""

        for j in range(len(info_list[i])):
            if   slash_found==False and re.search("[A-Z]", info_list[i][j])!=None:  #wenn Slash nicht gefunden und Buchstabe:
                info_new+=info_list[i][j]                                           #weiterleiten
            elif slash_found==False and re.search("[0-9]", info_list[i][j])!=None:  #wenn Slash nicht gefunden und Zahl:
                vis1+=info_list[i][j]                                               #Vis1 Teil
            elif slash_found==False and info_list[i][j]=="/":                       #wenn noch kein Slash und Slash gefunden:
                slash_found=True                                                    #gefunden
            elif slash_found==True and re.search("[0-9]", info_list[i][j])!=None:   #wenn Slash gefunden und Zahl:
                vis2+=info_list[i][j]                                               #Vis2 Teil
            elif slash_found==True and re.search("[A-Z]", info_list[i][j])!=None:   #wenn Slash gefunden und Buchstabe
                if 0<len(vis1) and 0<len(vis2):                                     #wenn Vis1 und Vis2 im Buffer: alles konvertieren und weiterleiten
                    info_new+=f"{KFSfstr.notation_tech(int(vis1)/int(vis2)*1609.344, 2)}m"
                    if int(vis1)/int(vis2)<3:                                       #Vis min 3SM (4,8km)
                        bold=True
                    vis1=""
                    vis2=""
                info_new+=info_list[i][j]
        info_new=info_new.replace("SM", "")

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new