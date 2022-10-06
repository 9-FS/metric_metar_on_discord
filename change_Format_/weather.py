import re   #Regular Expressions


def change_format_weather(info):
    if re.search("^([+-]|)([A-Z][A-Z]|)([A-Z][A-Z]|)[A-Z][A-Z]$", info)!=None:
        bold=False
        i=0
        while i<len(info):
            if i==0 and re.search("^[+-]$", info[i])!=None:
                i+=1
                continue
            if re.search("BR|DS|FC|FG|FZ|GR|GS|HZ|IC|PL|SG|SN|SQ|SS|TS|VA", info[i:i+2])!=None: #bei dem Wetter nich fliegen, Sicht, Vereisung, Stürme etc
                bold=True
            i+=2
        if bold==True:
            info=f"**{info}**"
        return " "+info