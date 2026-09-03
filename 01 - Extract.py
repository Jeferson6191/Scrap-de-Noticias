from bs4 import BeautifulSoup
import requests
from colorama import Fore, Style
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
import time
import os

#class dos titulos JtKRv
load_dotenv()

INFO = (Style.BRIGHT + "[INFO]" + Style.RESET_ALL)
ERRO = (Fore.RED + "[ERRO]" + Fore.RESET)
OK = (Fore.GREEN + "[OK]"+ Fore.RESET)
SENHA_BANCO = os.getenv("SENHA")

print(SENHA_BANCO)
caminho = "https://news.google.com/"
#config web driver
options = Options()
options.add_argument("--headless")
if os.name == "posix":
    options.binary_location = os.path.join(os.path.abspath("linux_drivers"), "chrome-linux64","chrome")
    service = Service(executable_path=os.path.join(os.path.abspath("linux_drivers"),"chromedriver-linux64","chromedriver"))
else:
    options.binary_location = (os.path.join(os.path.join(os.path.abspath("windows_drivers"),"windows_drivers","chromedriver-win64","chrome.exe")))
    service = Service(executable_path=os.path.join(os.path.join(os.path.abspath("windows_drivers"),"chromedriver-win64","chromedriver.exe")))


driver = webdriver.Chrome(options=options,service=service)
driver.get(caminho)
time.sleep(3)

html = driver.page_source
soup = BeautifulSoup(html,"html.parser")
a = soup.find_all("a",class_="JtKRv")

contents = {"Titulo":[],
            "Links":[]}

for htmls in a:
    titulo = htmls.get_text()
    link = f'https://news.google.com/{htmls["href"]}'

    contents["Titulo"].append(titulo) 
    contents["Links"].append(link) 

df = pd.DataFrame(contents)
print(df)

input("aperte enter para parar")
driver.quit()
