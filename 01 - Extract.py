from bs4 import BeautifulSoup
import requests
from colorama import Fore, Style
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

#class dos titulos JtKRv


INFO = (Style.BRIGHT + "[INFO]" + Style.RESET_ALL)
ERRO = (Fore.RED + "[ERRO]" + Fore.RESET)
OK = (Fore.GREEN + "[OK]"+ Fore.RESET)

caminho = "https://news.google.com/"
#config web driver
options = Options()
#options.add_argument("--headless")
if os.name == "posix":
    options.binary_location = os.path.join(os.path.abspath("linux_drivers"), "chrome-linux64","chrome")
    service = Service(executable_path=os.path.join(os.path.abspath("linux_drivers"),"chromedriver-linux64","chromedriver"))
else:
    options.binary_location = (os.path.join(
        os.path.join(os.path.abspath("windows_drivers"),"windows_drivers","chromedriver-win64","chrome.exe")))
    service = Service(executable_path=os.path.join(
        os.path.join(os.path.abspath("windows_drivers"),"chromedriver-win64","chromedriver.exe")))


driver = webdriver.Chrome(options=options,service=service)
driver.get(caminho)

input("aperte enter para parar")