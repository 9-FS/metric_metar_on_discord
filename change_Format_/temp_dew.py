import re   #Regular Expressions


def change_format_temp_dew(info):
    #Temperatur und Taupunkt
    if re.search("^(M|)[0-9][0-9]/(((M|)[0-9][0-9])|)$", info)!=None:
        bold=False
        temp_dew=""   #Temperatur oder Taupunkt, Hilfsvariabel
        info_new=""
        for i in range(len(info)):
            if info[i]=="M":     #wenn M:
                temp_dew+="-"                           #Temperatur Vorzeichen
            elif re.search("[0-9]", info[i])!=None:     #wenn Zahl:
                temp_dew+=info[i]                       #Zahl Teil
            elif info[i]=="/":                                      #wenn /:
                if 0<len(temp_dew):                                 #wenn was im Buffer:
                    if 0<=int(temp_dew):                            #wenn 0°C<=T:
                        info_new+=f"{int(temp_dew):02.0f}°C/"       #konvertieren, weiterleiten
                    else:                                           #wenn T<0°C:
                        info_new+=f"{int(temp_dew):03.0f}°C/"       #konvertieren immer mit 2 Stellen aufgefüllt mit Nullen, weiterleiten

                    if int(temp_dew)<=0 or 50<=int(temp_dew):       #Temp min. 0°C weil keine Vereisungsbedingungen, max. 50°C wegen Performance Charts
                        bold=True
                    temp_dew=""
            if i==len(info)-1:                                      #wenn Durchgang letzter:
                if 0<len(temp_dew):                                 #wenn was im Buffer:
                    if 0<=int(temp_dew):                            #wenn 0°C<=T:
                        info_new+=f"{int(temp_dew):02.0f}°C"        #konvertieren, weiterleiten
                    else:                                           #wenn T<0°C:
                        info_new+=f"-{int(temp_dew[1:]):02.0f}°C"   #für Formatierung Minus wegschneiden, Nullen auf 2 Stellen auffüllen, Minus wieder hinzufügen beim Konvertieren, weiterleiten
                    temp_dew=""

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new


    #USA: Temperatur und Taupunkt
    if re.search("^T[01][0-9][0-9][0-9][01][0-9][0-9][0-9]$", info)!=None:
        bold=False
        temp_dew=""  #Temperatur oder Taupunkt, Hilfsvariabel
        info_new=""

        temp_dew=int(info[2:5])/10
        if info[1]=="1":                            #wenn Vorzeichen negativ:
            temp_dew*=-1
            info_new+=f"{temp_dew:05.1f}°C/".replace(".", ",")
        else:                                       #wenn Vorzeichen positiv oder unbestimmbar:
            info_new+=f"{temp_dew:04.1f}°C/".replace(".", ",")
        if float(temp_dew)<=0 or 50<=float(temp_dew): #Temp min. 0°C weil keine Vereisungsbedingungen, max. 50°C wegen Performance Charts
            bold=True

        temp_dew=int(info[6:9])/10
        if info[5]=="1":    #wenn Vorzeichen negativ:
            temp_dew*=-1
            info_new+=f"{temp_dew:05.1f}°C".replace(".", ",")
        else:               #wenn Vorzeichen positiv oder unbestimmbar:
            info_new+=f"{temp_dew:04.1f}°C".replace(".", ",")

        if bold==True:
            info_new=f"**{info_new}**"
        return " "+info_new