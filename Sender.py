import pandas as pd
from sqlalchemy import create_engine, inspect, text
from datetime import datetime
from colorama import Fore, Style
from dotenv import load_dotenv
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
hoje = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)

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

#extraindo dados do banco de dados

engine = None
try:
    engine = create_engine(f'postgresql+psycopg2://{USUARIO}:{SENHA}@{HOST}:{PORTA}/{NOME_DO_BANCO}')
    insp = inspect(engine)
    print(OK, "Conexao com o banco de dados estabelecida")
except Exception as e:
    print(ERRO, f"Falha ao conectar ao banco de dados: {e}")
    raise

query = f"""
SELECT "Titulo","Links" FROM "Noticias"
WHERE "Data_Extracao" >= '{hoje}';
"""

df = pd.read_sql(query, con=engine)

# Executando envio de email


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from urllib.parse import quote
from functools import lru_cache

import requests

# Encurtador de links (TinyURL, sem autenticacao)
TINYURL_ENDPOINT = "https://tinyurl.com/api-create.php"

@lru_cache(maxsize=512)
def encurtar_url(url: str) -> str:
    """Encurta uma URL via TinyURL. Devolve a URL original em caso de falha."""
    if not url:
        return url
    try:
        resp = requests.get(
            TINYURL_ENDPOINT,
            params={"url": url},
            timeout=5,
            allow_redirects=True,
        )
        resp.raise_for_status()
        curto = resp.text.strip()
        # TinyURL devolve o link em texto puro; sanity check basico
        if curto.startswith("https://tinyurl.com/"):
            return curto
        print(ERRO, f"Resposta inesperada do TinyURL para {url}: {curto!r}")
        return url
    except Exception as e:
        print(ERRO, f"Falha ao encurtar {url}: {e}")
        return url

# Configuração para Gmail via .env
try:
    EMAIL_SENDER = os.environ["EMAIL_SENDER"]
    EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
    EMAIL_RECEIVER = os.environ["EMAIL_RECEIVER"]
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))
    print(OK, "Variaveis de e-mail obtidas com sucesso")
except KeyError as e:
    print(ERRO, f"Variavel de ambiente de e-mail nao encontrada: {e}")
    raise

# Montando o corpo do e-mail a partir do DataFrame
data_fmt = hoje.strftime('%d/%m/%Y')
total = len(df)

if df.empty:
    itens_html = """
      <tr>
        <td style="padding:24px 0;color:#6b7280;font-size:14px;">
          Nenhuma noticia foi extraida hoje.
        </td>
      </tr>
    """
    itens_texto = "Nenhuma noticia foi extraida hoje."
else:
    linhas_html = []
    linhas_texto = []
    for _, row in df.iterrows():
        titulo = str(row["Titulo"]).strip()
        link = str(row["Links"]).strip()
        link_curto = encurtar_url(link)
        linhas_html.append(f"""
        <tr>
          <td style="padding:14px 0;border-bottom:1px solid #e5e7eb;">
            <a href="{escape(link_curto)}" target="_blank"
               style="color:#1d4ed8;text-decoration:none;font-size:16px;font-weight:600;">
              {escape(titulo)}
            </a>
            <div style="color:#6b7280;font-size:12px;margin-top:4px;word-break:break-all;">
              {escape(link_curto)}
            </div>
          </td>
        </tr>
        """)
        linhas_texto.append(f"- {titulo}\n  {link_curto}")
    itens_html = "\n".join(linhas_html)
    itens_texto = "\n".join(linhas_texto)

html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background-color:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f3f4f6;padding:24px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0"
               style="background-color:#ffffff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.08);overflow:hidden;">
          <tr>
            <td style="background-color:#1d4ed8;padding:24px 32px;">
              <h1 style="margin:0;color:#ffffff;font-size:22px;font-weight:600;">
                Resumo de Noticias
              </h1>
              <p style="margin:6px 0 0 0;color:#dbeafe;font-size:14px;">
                Edicao de {data_fmt}
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 32px 8px 32px;">
              <p style="margin:0;color:#374151;font-size:14px;line-height:1.5;">
                Ola! Confira abaixo as <strong>{total}</strong> noticia(s) extraida(s) hoje.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:8px 32px 24px 32px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
                     style="border-collapse:collapse;">
                {itens_html}
              </table>
            </td>
          </tr>
          <tr>
            <td style="background-color:#f9fafb;padding:16px 32px;border-top:1px solid #e5e7eb;">
              <p style="margin:0;color:#9ca3af;font-size:12px;text-align:center;">
                Enviado automaticamente pelo Scrap-Noticias
              <p style="margin:0;color:#9ca3af;font-size:12px;text-align:center;">
                by: <a href="https://github.com/Jeferson6191" style="color:#9ca3af;">Jeferson6191</a>
            </p>         
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

texto = f"""Resumo de Noticias - {data_fmt}

Ola! Confira abaixo as {total} noticia(s) extraida(s) hoje.

{itens_texto}

---
Enviado automaticamente pelo Scrap-Noticias
by: Jeferson6191
"""

msg = MIMEMultipart("alternative")
msg['Subject'] = f"Resumo de Noticias - {data_fmt}"
msg['From'] = EMAIL_SENDER
msg['To'] = EMAIL_RECEIVER

msg.attach(MIMEText(texto, "plain", _charset="utf-8"))
msg.attach(MIMEText(html, "html", _charset="utf-8"))

try:
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
    print(OK, f"E-mail enviado para {EMAIL_RECEIVER} com {len(df)} noticia(s)")
except Exception as e:
    print(ERRO, f"Falha ao enviar e-mail: {e}")
    raise