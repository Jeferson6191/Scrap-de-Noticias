from bs4 import BeautifulSoup
import requests
from colorama import Fore, Style

INFO = (Style.BRIGHT + "[INFO]" + Style.RESET_ALL)
ERRO = (Fore.RED + "[ERRO]" + Fore.RESET)
OK = (Fore.GREEN + "[OK]"+ Fore.RESET)

caminho = requests.get("https://news.google.com/home?hl=pt-BR&gl=BR&ceid=BR%3Apt-419")
soup = BeautifulSoup(caminho.text, "html.parser")
noticias = soup.find_all("div",class_="XlKvRb")

links = []
for div in noticias:
    for a in div.find_all("a"):
        links.append(f"https://news.google.com/{a.get_attribute_list('href')[0]}")

print(INFO, len(links), "links encontrados")

