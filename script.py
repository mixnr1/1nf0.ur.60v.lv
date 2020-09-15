import os
import re
import time
from selenium import webdriver
import requests
import config
start = time.time()
path=config.path
driver = webdriver.Firefox(executable_path=config.driver_path)
my_list=open(path+'list.txt', 'r')
result_file=open(path+"result.csv",'a')
for elem in my_list:
    driver.get('https://info.ur.gov.lv/?#/legal-entity/'+elem)
    time.sleep(3)
    Url=str('https://info.ur.gov.lv/?#/legal-entity/'+elem)
    Nosaukums=driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[4]/div/div/div/div[2]/div/div[3]/div[1]/div[1]/h1').text #Nosaukums
    Vienotais_registracijas_numurs=driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[4]/div/div/div/div[2]/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[1]/div/div[2]').text #Vienotais reģistrācijas numurs
    SEPA_identifikators=driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[4]/div/div/div/div[2]/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]').text #SEPA identifikators
    Registracijas_datums=driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[4]/div/div/div/div[2]/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]').text #Reģistrācijas datums
    Iesniegtie_gada_parskati=driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[4]/div/div/div/div[2]/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[6]/div/div/div[2]').text #Iesniegtie gada pārskati
    Adrese=driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[4]/div/div/div/div[2]/div/div[3]/div[2]/div/div[2]/div/div/div[1]/div[1]/div[4]/div/div[2]').text #Adrese
    result_file.write(Url.rstrip()+"|"+\
        Nosaukums+"|"+\
        Vienotais_registracijas_numurs+"|"+\
        Adrese+"|"+\
        SEPA_identifikators+"|"+\
        Registracijas_datums+"|"+\
        Iesniegtie_gada_parskati+ '\n')
    time.sleep(5)
driver.close()
result_file.close()
my_list.close()

end = time.time()
end_tuple = time.localtime()
end_time = time.strftime("%Y-%m-%d %H:%M:%S", end_tuple)
print("Script ended: "+end_time)
print("Script running time: "+time.strftime('%H:%M:%S', time.gmtime(end - start)))
