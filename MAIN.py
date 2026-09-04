from bs4 import BeautifulSoup
import requests
from colorama import Fore, Style
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, inspect, text
import time
import os

#class dos titulos JtKRv
try:
    load_dotenv()
    print(INFO if (INFO := (Style.BRIGHT + "[INFO]" + Style.RESET_ALL)) else "", "Variaveis de ambiente carregadas")
except Exception as e:
    print(ERRO if (ERRO := (Fore.RED + "[ERRO]" + Fore.RESET)) else "", f"Falha ao carregar variaveis de ambiente: {e}")
    raise

INFO = (Style.BRIGHT + "[INFO]" + Style.RESET_ALL)
ERRO = (Fore.RED + "[ERRO]" + Fore.RESET)
OK = (Fore.GREEN + "[OK]"+ Fore.RESET)

try:
    SENHA = os.environ["SENHA"]
    USUARIO = os.environ["USUARIO"]
    PORTA = os.environ["PORTA"]
    NOME_DO_BANCO = os.environ["NOME_DO_BANCO"]
    HOST = os.environ["HOST"]
    print(OK, "Variaveis de ambiente obtidas com sucesso")
except KeyError as e:
    print(ERRO, f"Variavel de ambiente nao encontrada: {e}")
    raise

caminho = "https://news.google.com/"

#config web driver
options = Options()
options.add_argument("--headless")

try:
    if os.name == "posix":
        options.binary_location = os.path.join(os.path.abspath("linux_drivers"), "chrome-linux64","chrome")
        service = Service(executable_path=os.path.join(os.path.abspath("linux_drivers"),"chromedriver-linux64","chromedriver"))
    else:
        options.binary_location = (os.path.join(os.path.join(os.path.abspath("windows_drivers"),"windows_drivers","chromedriver-win64","chrome.exe")))
        service = Service(executable_path=os.path.join(os.path.join(os.path.abspath("windows_drivers"),"chromedriver-win64","chromedriver.exe")))
    print(OK, "Driver configurado")
except Exception as e:
    print(ERRO, f"Falha ao configurar o driver: {e}")
    raise


driver = None
try:
    driver = webdriver.Chrome(options=options,service=service)
    driver.get(caminho)
    time.sleep(3)
    print(OK, "Pagina carregada com sucesso")
except Exception as e:
    print(ERRO, f"Falha ao iniciar o navegador ou carregar a pagina: {e}")
    if driver:
        driver.quit()
    raise

try:
    html = driver.page_source
    soup = BeautifulSoup(html,"html.parser")
    a = soup.find_all("a",class_="JtKRv")
    print(OK, "HTML parseado com sucesso")
except Exception as e:
    print(ERRO, f"Falha ao parsear o HTML: {e}")
    driver.quit()
    raise

contents = {"Titulo":[],
            "Links":[]}

try:
    for htmls in a:
        titulo = htmls.get_text()
        link = f'https://news.google.com/{htmls["href"]}'

        contents["Titulo"].append(titulo)
        contents["Links"].append(link)
    print(OK, "Dados extraidos com sucesso")
except Exception as e:
    print(ERRO, f"Falha ao extrair os dados: {e}")
    driver.quit()
    raise

try:
    df = pd.DataFrame(contents)
    print(df)
    df.insert(0, "Data_Extracao", pd.Timestamp.now().replace(hour=0,minute=0,second=0,microsecond=0))
    print(OK, "Scraping de dados feito com sucesso")
except Exception as e:
    print(ERRO, f"Falha ao criar o DataFrame: {e}")
    driver.quit()
    raise
finally:
    try:
        driver.quit()
        print(INFO, "Driver encerrado")
    except Exception as e:
        print(ERRO, f"Falha ao encerrar o driver: {e}")

print(INFO, "Iniciando transferencia para banco de dados")
engine = None
try:
    engine = create_engine(f'postgresql+psycopg2://{USUARIO}:{SENHA}@{HOST}:{PORTA}/{NOME_DO_BANCO}')
    insp = inspect(engine)
    print(OK, "Conexao com o banco de dados estabelecida")
except Exception as e:
    print(ERRO, f"Falha ao conectar ao banco de dados: {e}")
    raise

try:
    if "Noticias" not in insp.get_table_names():
        print(INFO, f"A tabela Noticias nao foi encontrada, criando do zero...")
        df.to_sql("Noticias",con=engine,method="multi",if_exists="replace",chunksize=1500, index=False)
        print(OK, "Tabela criada e dados inseridos")
    else:
        with engine.connect() as connection:
            connection.execute(text(f""" delete from "Noticias" WHERE "Data_Extracao" >= '{datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)}' """))
            connection.commit()
        df.to_sql("Noticias",con=engine,method="multi",if_exists="append",chunksize=1500, index=False)
        print(OK, "Dados inseridos na tabela existente")
except Exception as e:
    print(ERRO, f"Falha ao inserir dados no banco: {e}")
    raise
finally:
    try:
        if engine:
            engine.dispose()
            print(INFO, "Conexao com o banco encerrada")
    except Exception as e:
        print(ERRO, f"Falha ao encerrar conexao com o banco: {e}")
