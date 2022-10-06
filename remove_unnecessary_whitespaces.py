def remove_unnecessary_whitespaces(str):
    #in Zeile Leerzeichen führend und nachfolgend entfernen
    strlist=[line.strip() for line in str.split("\n") if line!=""]  #an Newlines aufteilen, Elemente leer entfernen, Zeilen strippen
    str="\n".join(strlist)                                          #wieder zusammenfügen

    #Leerzeichen doppelt entfernen
    if len(str)<=1:
        return str
    for i in range(1, len(str)):
        if str[i-1]==" " and str[i]==" ":   #wenn Zeichen davor und Zeichen aktuell Leerzeichen:
            str=str[:i]+str[i+1:]       #Zeichen aktuell entfernen
            i-=1

    return str