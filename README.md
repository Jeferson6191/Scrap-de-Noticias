# Scrap Google News

Scraper de manchetes do [Google News](https://news.google.com/) usando **Selenium** (Chrome headless) + **BeautifulSoup**. O script coleta os títulos das notícias em destaque e seus links, e exporta o resultado em um `DataFrame` do `pandas`.

> Apesar do nome da pasta, este projeto raspa o **Google News**, não a Wikipédia.

## Pré-requisitos

- **Python 3.10+**
- **Google Chrome** compatível com a versão do `chromedriver` utilizado
- Drivers do Chrome para a sua plataforma (veja a seção [Instalação dos drivers](#instalação-dos-drivers))

## Instalação

1. Clone o repositório e entre na pasta:

    ```bash
    git clone <url-do-repo>
    cd Scrap-WikiPedia
    ```

2. Crie e ative um ambiente virtual:

    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Linux/macOS
    .venv\Scripts\activate      # Windows
    ```

3. Instale as dependências:

    ```bash
    pip install -r requeriments.txt
    ```

4. Crie um arquivo `.env` na raiz (use o exemplo abaixo como base):

    ```env
    SENHA=
    ```

    > O arquivo `.env` já está listado no `.gitignore` e **não deve** ser commitado.

## Instalação dos drivers

O script detecta automaticamente a plataforma e usa o driver apropriado. Você precisa baixar o **Chrome for Testing** correspondente e extrair nas pastas esperadas:

- `linux_drivers/chrome-linux64/chrome` + `linux_drivers/chromedriver-linux64/chromedriver`
- `windows_drivers/chromedriver-win64/chrome.exe` + `windows_drivers/chromedriver-win64/chromedriver.exe`

Baixe em: <https://googlechromelabs.github.io/chrome-for-testing/>

> As pastas `linux_drivers/` e `windows_drivers/` estão no `.gitignore` — cada máquina baixa a sua.

## Uso

```bash
python "01 - Extract.py"
```

Saída esperada (exemplo):

```
[INFO][OK]...
                                              Titulo                                              Links
0                              Manchete de exemplo 1            https://news.google.com/...
1                              Manchete de exemplo 2            https://news.google.com/...
...
aperte enter para parar
```

O navegador roda em modo **headless** (sem janela visível) e é fechado ao final.

## Estrutura do projeto

```
Scrap-WikiPedia/
├── 01 - Extract.py         # Script principal de scraping
├── requeriments.txt        # Dependências Python
├── .env                    # Variáveis de ambiente (não versionado)
├── .gitignore
├── linux_drivers/          # Chrome + chromedriver para Linux (não versionado)
└── windows_drivers/        # Chrome + chromedriver para Windows (não versionado)
```

## Dependências principais

- `selenium` — automação do navegador
- `beautifulsoup4` — parsing do HTML
- `pandas` — estruturação dos dados
- `python-dotenv` — leitura do `.env`
- `colorama` — saída colorida no terminal

A lista completa está em [requeriments.txt](requeriments.txt).

## Observações

- Os seletores CSS usados (`a.JtKRv`) são específicos do layout atual do Google News e podem quebrar caso o site mude.
- A impressão de `SENHA_BANCO` no console é proposital apenas para debug — remova antes de usar em produção.
- O `input("aperte enter para parar")` mantém o driver aberto para inspeção manual. Remova a linha se preferir que o script termine sozinho.
