def split(str, *seperators):    #trennt den String an allen gegebenen Seperatoren
    list=[""]                   #Ergebnis
    char_is_sep=False           #ist Zeichen aktuell ein Seperator?

    for char in str:            #String durch
        char_is_sep=False
        for sep in seperators:
            if char==sep:
                char_is_sep=True
                break

        if(char_is_sep==False):     #wenn Zeichen aktuell kein Seperator:
            list[len(list)-1]+=char #bei Liste an letztem String anhängen
        else:                       #wenn Zeichen aktuell Seperator:
            list.append("")         #Zeichen ignorieren, in Liste String neu anfangen

    return list