import requests
import json
import csv
import config
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import config
start = time.time()

path=config.path
my_list=open(path+'list.txt', 'r')
options = FirefoxOptions()
options.add_argument("--incognito")
options.add_argument("--headless")
result_file=open(path+"result.csv",'a')
firmu_list=[]
for reg in my_list:
    driver = webdriver.Firefox(options=options, executable_path=config.driver_path)
    driver.get('https://info.ur.gov.lv/?#/legal-entity/'+reg)
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "react-tabs-0")))
    Url=str('https://info.ur.gov.lv/?#/legal-entity/'+reg)
    soup=BeautifulSoup(driver.page_source, 'lxml')
    firma=soup.find("h1", {"class": "Headline1"}).text.strip()
    mylist=['', '', '', '', '']
    for elem in soup.findAll("div", {"class": "Dropdown"}):
        if re.findall('Maksātnespējas process\([1-9]\)', elem.text):
            mylist[0]=str(reg.rstrip())
            mylist[1]=str(firma)
            mylist[2]="NEDERĪGS"
            mylist[3]="Maksātnespējas process"
    for elem in soup.find_all("div", {"class": "ContentLight"}):
        if elem.text.strip() == "Izslēgts no reģistra":
            mylist[0]=str(reg.rstrip())
            mylist[1]=str(firma)
            mylist[2]=str("NEDERĪGS")
            mylist[3]=str("Iemesls:"+elem.text.strip())
        elif elem.text.strip() == "Reģistrācijas datums" and mylist[2] == "NEDERĪGS":
            mylist[4]=str(elem.next_element.next_element.text.strip())
            # mylist[4]="Reģistrācijas datums: "+str(elem.next_element.next_element.text.strip())
        elif elem.text.strip() == "Reģistrācijas datums" and not mylist[2] == "NEDERĪGS":
            mylist[0]=str(reg.rstrip())
            mylist[1]=str(firma)
            mylist[2]=str("DERĪGS")
            mylist[4]=str(elem.next_element.next_element.text.strip())
            # mylist[4]="Reģistrācijas datums:"+str(elem.next_element.next_element.text.strip())
    for elem in soup.find_all("div", {"class": "ContentLight"}):
        if elem.text.strip() == "Adrese" and not mylist[2] == "NEDERĪGS":
            mylist[3]="Adrese:"+str(elem.next_element.next_element.text.strip())   
    firmu_list.append(mylist)
    driver.quit()

json_path = {
    'members':'/persons/members?lang=LV&fillForeignerData=true&printout=false',
    'procurations': '/procurations?fillForeignerData=true',
    'officers':'/persons/officers?lang=LV&fillForeignerData=true',
    'beneficiaries':'/persons/beneficiaries?lang=LV&fillForeignerData=true'}
big_list=[]
for reg_nr in firmu_list:
    elem=(str(reg_nr[0])[1:10])
    first_part=str(reg_nr[0]+"|"+\
        reg_nr[1]+"|"+\
        reg_nr[2]+"|"+\
        reg_nr[3]+"|"+\
        reg_nr[4]+"|")
    # first_part=str("Reģistrācijas_numurs:"+reg_nr[0]+"|"+\
    #     "Nosaukums:"+reg_nr[1]+"|"+\
    #     "Status:"+reg_nr[2]+"|"+\
    #     reg_nr[3]+"|"+\
    #     reg_nr[4]+"|")
    for key in json_path:
        if key == "members":
            url='https://info.ur.gov.lv/api/legalentity/api/'+elem+json_path[key]
            response = requests.get(url)
            dati = response.json()
            if('records') in dati:
                if len(dati['records']) > 1:
                    for subelem in range(0,len(dati['records'])):
                        for key in dati['records'][subelem]:
                            if dati['records'][subelem][key]==("FOR_ENTITY"):
                                big_list.append(first_part+"MEMBERS"+"|"+\
                                    "fullname:"+dati['records'][subelem]['name']+"|"+\
                                    "registrationNumber:"+str(dati['records'][subelem]['registrationNumber'])+"|"+\
                                    "sharePercent:"+str(dati['records'][subelem]['sharePercent'])+"|"+\
                                    "shareCount:"+str(dati['records'][subelem]['shareCount'])+"|"+\
                                    "shareValue:"+str(dati['records'][subelem]["shareValue"]))
                            if dati['records'][subelem][key]==("LVENTITY"):
                                big_list.append(first_part+"MEMBERS"+"|"+\
                                    "fullname:"+dati['records'][subelem]['name']+"|"+\
                                    "registrationNumber:"+dati['records'][subelem]['registrationNumber']+"|"+\
                                    "sharePercent:"+str(dati['records'][subelem]['sharePercent'])+"|"+\
                                    "shareCount:"+str(dati['records'][subelem]['shareCount'])+"|"+\
                                    "shareValue:"+str(dati['records'][subelem]["shareValue"]))
                            if dati['records'][subelem][key]==("PERSON"):
                                big_list.append(first_part+"MEMBERS"+"|"+\
                                "fullname:"+dati['records'][subelem]['name']+"|"+\
                                "personCode:"+dati['records'][subelem]['personCode']+"|"+\
                                "sharePercent:"+str(dati['records'][subelem]['sharePercent'])+"|"+\
                                "shareCount:"+str(dati['records'][subelem]['shareCount'])+"|"+\
                                "shareValue:"+str(dati['records'][subelem]["shareValue"]))
                            if dati['records'][subelem][key]==("FOR_PERSON"):
                                big_list.append(first_part+"MEMBERS"+"|"+\
                                    "fullname:"+dati['records'][subelem]['name']+"|"+\
                                    "personCode:"+dati['records'][subelem]['personCode']+"|"+\
                                    "sharePercent:"+str(dati['records'][subelem]['sharePercent'])+"|"+\
                                    "shareCount:"+str(dati['records'][subelem]['shareCount'])+"|"+\
                                    "shareValue:"+str(dati['records'][subelem]["shareValue"]))
                else:                         
                    for row in dati['records']:
                        if('name' in row):
                            if row["entityType"] == "FOR_ENTITY":
                                big_list.append(first_part+"MEMBERS"+"|"+\
                                    "fullname:"+row['name']+"|"+\
                                    "registrationNumber:"+str(row['registrationNumber'])+"|"+\
                                    "sharePercent:"+str(row['sharePercent'])+"|"+\
                                    "shareCount:"+str(row['shareCount'])+"|"+\
                                    "shareValue:"+str(row["shareValue"]))
                            if row["entityType"] == "LVENTITY":
                                big_list.append(first_part+"MEMBERS"+"|"+\
                                    "fullname:"+row['name']+"|"+\
                                    "registrationNumber:"+row['registrationNumber']+"|"+\
                                    "sharePercent:"+str(row['sharePercent'])+"|"+\
                                    "shareCount:"+str(row['shareCount'])+"|"+\
                                    "shareValue:"+str(row["shareValue"]))
                            if row["entityType"]=="PERSON":
                                big_list.append(first_part+"MEMBERS"+"|"+\
                                    "fullname:"+row['name']+"|"+\
                                    "personCode:"+row['personCode']+"|"+\
                                    "sharePercent:"+str(row['sharePercent'])+"|"+\
                                    "shareCount:"+str(row['shareCount'])+"|"+\
                                    "shareValue:"+str(row["shareValue"]))
                            if row["entityType"]=="FOR_PERSON":
                                big_list.append(first_part+"MEMBERS"+"|"+\
                                    "fullname:"+row['name']+"|"+\
                                    "personCode:"+row['personCode']+"|"+\
                                    "sharePercent:"+str(row['sharePercent'])+"|"+\
                                    "shareCount:"+str(row['shareCount'])+"|"+\
                                    "shareValue:"+str(row["shareValue"]))
        if key == "procurations":
            url='https://info.ur.gov.lv/api/legalentity/api/'+elem+json_path[key]
            response = requests.get(url)
            dati = response.json()
            if('records') in dati:
                if len(dati['records']) >= 1:
                    for subelem in range(0,len(dati['records'])):
                        for key in dati['records'][subelem]:
                            if key == "procurationPersons":
                                for subkey in dati['records'][subelem][key]:
                                    if subkey["entityType"]=="PERSON":
                                        big_list.append(first_part+"PROCURATIONS"+"|"+\
                                        "fullname:"+subkey['name']+" "+subkey['surname']+"|"+\
                                        "personCode:"+subkey['personCode']+"|"+\
                                        "country:"+"Latvijas Republika")
                                    if subkey["entityType"]=="FOR_PERSON":
                                        big_list.append(first_part+"PROCURATIONS"+"|"+\
                                        "fullname:"+subkey['name']+" "+subkey['surname']+"|"+\
                                        "personCode:"+subkey['personCode']+"|"+\
                                        "country:"+subkey["identityDocument"]["country"])
        if key == "officers":
            url='https://info.ur.gov.lv/api/legalentity/api/'+elem+json_path[key]
            response = requests.get(url)
            dati = response.json()
            if len(dati['records']) > 1:
                for subelem in range(0,len(dati['records'])):
                    for key in dati['records'][subelem]:
                            if dati['records'][subelem][key]==("FOR_PERSON"):
                                big_list.append(first_part+"OFFICERS"+"|"+\
                                    "fullname:"+dati['records'][subelem]['fullname']+"|"+\
                                    "personCode:"+dati['records'][subelem]['personCode']+"|"+\
                                    "positionText:"+dati['records'][subelem]['positionText']+"|"+\
                                    "country:"+dati['records'][subelem]['identityDocument']["country"])
                            if dati['records'][subelem][key]==("PERSON"):
                                big_list.append(first_part+"OFFICERS"+"|"+\
                                    "fullname:"+dati['records'][subelem]['fullname']+"|"+\
                                    "personCode:"+dati['records'][subelem]['personCode']+"|"+\
                                    "positionText:"+dati['records'][subelem]['positionText']+"|"+\
                                    "country:"+"Latvijas Republika")
            else:
                for row in dati['records']:
                    if('fullname' in row):
                        if row['identityDocument']==None:
                            big_list.append(first_part+"OFFICERS"+"|"+\
                                "fullname:"+row['fullname']+"|"+\
                                "personCode:"+row['personCode']+"|"+\
                                "positionText:"+row['positionText']+"|"+\
                                "country:"+"Latvijas Republika")
                    else:
                        big_list.append(first_part+"OFFICERS"+"|"+\
                            "fullname:"+row['fullname']+"|"+\
                            "personCode:"+row['personCode']+"|"+\
                            "positionText:"+row['positionText']+"|"+\
                            "country:"+row['identityDocument']["country"])
        if key == "beneficiaries":
            url='https://info.ur.gov.lv/api/legalentity/api/'+elem+json_path[key]
            response = requests.get(url)
            dati = response.json()
            if('records') in dati:
                if len(dati['records']) > 1:
                    for subelem in range(0,len(dati['records'])):
                        for key in dati['records'][subelem]:
                            if dati['records'][subelem][key]==("FOR_PERSON"):
                                big_list.append(first_part+"BENEFICIARIES"+"|"+\
                                    "fullname:"+dati['records'][subelem]['firstname']+" "+dati['records'][subelem]['lastname']+"|"+\
                                    "personCode:"+dati['records'][subelem]['personCode']+"|"+\
                                    "residesCountryText:"+dati['records'][subelem]['residesCountryText']+"|"+\
                                    "citizenCountryText:"+dati['records'][subelem]['citizenCountryText'])
                            if dati['records'][subelem][key]==("PERSON"):
                                big_list.append(first_part+"BENEFICIARIES"+"|"+\
                                    "fullname:"+dati['records'][subelem]['firstname']+" "+dati['records'][subelem]['lastname']+"|"+\
                                    "personCode:"+dati['records'][subelem]['personCode']+"|"+\
                                    "residesCountryText:"+dati['records'][subelem]['residesCountryText']+"|"+\
                                    "citizenCountryText:"+dati['records'][subelem]['citizenCountryText'])
                else:                         
                    for row in dati['records']:
                        if('firstname' in row):
                            if row["entityType"] == "FOR_PERSON":
                                big_list.append(first_part+"BENEFICIARIES"+"|"+\
                                "fullname:"+row['firstname']+" "+row['lastname']+"|"+\
                                "personCode:"+row['personCode']+"|"+\
                                "residesCountryText:"+row['residesCountryText']+"|"+\
                                "citizenCountryText:"+row['citizenCountryText'])
                            if row["entityType"]=="PERSON":
                                big_list.append(first_part+"BENEFICIARIES"+"|"+\
                                    "fullname:"+row['firstname']+" "+row['lastname']+"|"+\
                                    "personCode:"+row['personCode']+"|"+\
                                    "residesCountryText:"+row['residesCountryText']+"|"+\
                                    "citizenCountryText:"+row['citizenCountryText'])

#write first line to file
title_line="Reģistrācijas_numurs|Nosaukums|Status|Informācija|Reģistrācijas_datums|6|7|8|9|10|11|"
with open(path+"result.csv", 'w') as writer:
        writer.write(title_line+"\n")
        writer.close()

#write big_list to file
result_file=open(path+"result.csv",'a')
for line in big_list:
    result_file.write(line+"\n")
result_file.close()

end = time.time()
end_tuple = time.localtime()
end_time = time.strftime("%Y-%m-%d %H:%M:%S", end_tuple)
print("Script ended: "+end_time)
print("Script running time: "+time.strftime('%H:%M:%S', time.gmtime(end - start)))