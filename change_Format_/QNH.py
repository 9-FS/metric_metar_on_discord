import re   #Regular Expressions

def change_format_QNH(info):
    #QNH
    if re.search("^Q[0-9][0-9][0-9][0-9]$", info)!=None:
        info_new=f"Q{int(info[1:5])/10:05.1f}kPa".replace(".", ",")
        if int(info[1:5])*100<=95e3 or 105e3<=int(info[1:5])*100:   #Druck ungewöhnlich, schau wegen QNH-Skala und bei Tief Stürmen
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^A[0-9][0-9][0-9][0-9]$", info)!=None:
        info_new=f"A{int(info[1:5])/100*3386.3879597/1000:05.1f}kPa".replace(".", ",")
        if int(info[1:5])/100*3386.3879597<=95e3 or 105e3<=int(info[1:5])/100*3386.3879597: #Druck ungewöhnlich, schau wegen QNH-Skala und bei Tief Stürmen
            info_new=f"**{info_new}**"
        return " "+info_new

    if re.search("^QNH[0-9][0-9][0-9][0-9]INS$", info)!=None:
        info_new=f"A{int(info[3:7])/100*3386.3879597/1000:05.1f}kPa".replace(".", ",")
        if int(info[3:7])/100*3386.3879597<=95e3 or 105e3<=int(info[3:7])/100*3386.3879597: #Druck ungewöhnlich, schau wegen QNH-Skala und bei Tief Stürmen
            info_new=f"**{info_new}**"
        return " "+info_new


    #Russland: QFE
    if re.search("^QFE[0-9][0-9][0-9]$", info)!=None:
        info=f"QFE{int(info[3:6])*133.3223694/1000:05.1f}kPa".replace(".", ",")
        return " "+info

    if re.search("^QFE[0-9][0-9][0-9].[0-9]$", info)!=None:
        info=f"QFE{float(info[3:8])*133.3223694/1000:05.1f}kPa".replace(".", ",")
        return " "+info

    if re.search("^QFE[0-9][0-9][0-9]/[0-9][0-9][0-9][0-9]$", info)!=None:
        info=f"QFE{int(info[7:11])/10:05.1f}kPa".replace(".", ",")
        return " "+info


    #USA: SLP
    if re.search("^SLP[0-9][0-9][0-9]$", info)!=None:
        if 0<=int(info[3:6])*10 and int(info[3:6])*10<5000: #wenn 0kPa<=SLP_Angabe<5kPa: +100kPa
            info=f"SLP{(int(info[3:6])*10+100e3)/1000:06.2f}kPa".replace(".", ",")
        elif 5000<=int(info[3:6])*10 and int(info[3:6])*10<10000:   #wenn 5kPa<=SLP_Angabe<10kPa: +90kPa
            info=f"SLP{(int(info[3:6])*10+90e3)/1000:06.2f}kPa".replace(".", ",")
        return " "+info