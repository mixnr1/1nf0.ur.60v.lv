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
options = FirefoxOptions()
options.add_argument("--incognito")
options.add_argument("--headless")
my_list=open(path+'list.txt', 'r')
result_file=open(path+"result.csv",'a')
big_list=[]
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
            mylist[3]=str(elem.text.strip())
        elif elem.text.strip() == "Reģistrācijas datums" and mylist[2] == "NEDERĪGS":
            mylist[4]="Reģistrācijas datums: "+str(elem.next_element.next_element.text.strip())
        elif elem.text.strip() == "Reģistrācijas datums" and not mylist[2] == "NEDERĪGS":
            mylist[0]=str(reg.rstrip())
            mylist[1]=str(firma)
            mylist[2]=str("DERĪGS")
            mylist[4]="Reģistrācijas datums: "+str(elem.next_element.next_element.text.strip())
    for elem in soup.find_all("div", {"class": "ContentLight"}):
        if elem.text.strip() == "Adrese" and not mylist[2] == "NEDERĪGS":
            mylist[3]="Adrese: "+str(elem.next_element.next_element.text.strip())  
    big_list.append(mylist)
    driver.quit()
#write big_list to file
with open(path+"result.csv",'w') as f:
    for sublist in big_list:
        line = "{}|{}|{}|{}|{}\n".format(sublist[0], sublist[1], sublist[2], sublist[3], sublist[4])
        f.write(line)
    
my_list.close()

end = time.time()
end_tuple = time.localtime()
end_time = time.strftime("%Y-%m-%d %H:%M:%S", end_tuple)
print("Script ended: "+end_time)
print("Script running time: "+time.strftime('%H:%M:%S', time.gmtime(end - start)))
