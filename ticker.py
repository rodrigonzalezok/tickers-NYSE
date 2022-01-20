from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.common.keys import Keys
import time
from os import system
from time import sleep

#Creamos el broser
browser = webdriver.Chrome(executable_path=".\driver\chromedriver.exe")
#Maximizamos la ventana
browser.maximize_window()
#Abrimos la pagina
browser.get("https://www.nyse.com/listings_directory/stock")
#Esperamos a que se cargue la pagina
WebDriverWait(browser, 30000).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, 'div.row')))
#Creamos una lista vacia
tickers = []
#Iteramos sobre todos los elementos de la tabla
for i in range(0,800):
    #Obtenemos el ticker
    lista = browser.find_elements(By.CSS_SELECTOR, 'td a')
    for ticker in lista:
        #Lo agregamos a la lista
        tickers.append(ticker.text)
    #Pasamos a la siguiente página
    browser.find_elements(By.CSS_SELECTOR, 'li.whitespace-nowrap')[-2].click()
    #Esperamos a que se cargue la pagina
    WebDriverWait(browser, 30000).until(expected_conditions.invisibility_of_element_located((By.CSS_SELECTOR, 'div.has-loader-is-loading')))
    time.sleep(1)
#Imprimimos la lista
print(tickers)