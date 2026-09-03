# Scrap Google News

Scraper de manchetes do [Google News](https://news.google.com/) usando **Selenium** (Chrome headless) + **BeautifulSoup**, com persistência automática em **PostgreSQL** via **SQLAlchemy**. O script coleta os títulos das notícias em destaque e seus links, estrutura tudo em um `DataFrame` do `pandas` e grava na tabela `Noticias` do banco.

> Apesar do nome da pasta, este projeto raspa o **Google News**, não a Wikipédia.

## Funcionalidades

- Coleta de manchetes do Google News em modo headless.
- Extração de título e link de cada notícia.
- Log colorido no terminal via `colorama` (`[INFO]`, `[OK]`, `[ERRO]`).
- Criação automática da tabela `Noticias` no PostgreSQL caso ainda não exista.
- Truncate + insert na tabela existente a cada execução (mantém apenas os dados mais recentes).
- Encerramento controlado do driver e do engine do SQLAlchemy.

## Pré-requisitos

- **Python 3.10+**
- **Google Chrome** compatível com a versão do `chromedriver` utilizado
- **PostgreSQL** acessível a partir da máquina onde o script roda
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
    USUARIO=
    PORTA=
    NOME_DO_BANCO=
    HOST=
    ```

    O script lê essas variáveis para montar a string de conexão do SQLAlchemy:

    ```
    postgresql+psycopg2://{USUARIO}:{SENHA}@{HOST}:{PORTA}/{NOME_DO_BANCO}
    ```

    > O arquivo `.env` já está listado no `.gitignore` e **não deve** ser commitado.

## Instalação dos drivers

O script detecta automaticamente a plataforma e usa o driver apropriado. Você precisa baixar o **Chrome for Testing** correspondente e extrair nas pastas esperadas:

- `linux_drivers/chrome-linux64/chrome` + `linux_drivers/chromedriver-linux64/chromedriver`
- `windows_drivers/windows_drivers/chromedriver-win64/chrome.exe` + `windows_drivers/chromedriver-win64/chromedriver.exe`

Baixe em: <https://googlechromelabs.github.io/chrome-for-testing/>

> As pastas `linux_drivers/` e `windows_drivers/` estão no `.gitignore` — cada máquina baixa a sua.

## Uso

```bash
python MAIN.py
```

O fluxo é:

1. Carrega as variáveis de ambiente do `.env`.
2. Configura e inicia o Chrome headless.
3. Acessa o Google News e extrai os elementos `<a class="JtKRv">`.
4. Monta um `DataFrame` com as colunas `Titulo` e `Links`.
5. Conecta ao PostgreSQL.
6. Se a tabela `Noticias` não existir, cria e insere os dados; caso contrário, faz `TRUNCATE` e reinsere.

Saída esperada (exemplo):

```
[INFO] Variaveis de ambiente carregadas
[OK] Variaveis de ambiente obtidas com sucesso
[OK] Driver configurado
[OK] Pagina carregada com sucesso
[OK] HTML parseado com sucesso
[OK] Dados extraidos com sucesso
[OK] Scraping de dados feito com sucesso
[INFO] Driver encerrado
[INFO] Iniciando transferencia para banco de dados
[OK] Conexao com o banco de dados estabelecida
[OK] Tabela criada e dados inseridos
[INFO] Conexao com o banco encerrada
```

O navegador roda em modo **headless** (sem janela visível) e é fechado ao final.

## Estrutura do projeto

```
Scrap-WikiPedia/
├── MAIN.py                 # Script principal (scraping + carga no PostgreSQL)
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
- `SQLAlchemy` — conexão e carga no banco
- `psycopg2-binary` — driver PostgreSQL para SQLAlchemy
- `colorama` — saída colorida no terminal

A lista completa está em [requeriments.txt](requeriments.txt).

## Banco de dados

A tabela de destino é **sempre** chamada `Noticias` e possui duas colunas:

| Coluna  | Tipo    | Descrição                              |
|---------|---------|----------------------------------------|
| Titulo  | text    | Manchete da notícia                    |
| Links   | text    | URL relativa prefixada com `https://news.google.com/` |

Comportamento em cada execução:

- **Tabela não existe** → é criada e o `DataFrame` é gravado com `if_exists="replace"`.
- **Tabela já existe** → é feito `TRUNCATE TABLE "Noticias"` e o `DataFrame` é gravado com `if_exists="append"`.

> O schema de carga é `multi`, com `chunksize=1500`. Se o volume aumentar, ajuste esse valor conforme a capacidade do seu banco.

## Observações

- Os seletores CSS usados (`a.JtKRv`) são específicos do layout atual do Google News e podem quebrar caso o site mude.
- A cada execução a tabela `Noticias` é truncada — o banco sempre reflete **apenas a última coleta**. Se quiser histórico, troque o `TRUNCATE` por uma estratégia de append com `timestamp`.
- O `engine.dispose()` é chamado em `finally`, então mesmo se a inserção falhar a conexão com o banco é liberada.
- O `driver.quit()` também está em `finally`, então o navegador sempre é encerrado, mesmo se algo falhar no parsing.
- Tome cuidado com caracteres especiais na senha do banco (ex.: `@`, `/`, `:`) — eles precisam ser codificados na URL ou causarão erro de conexão.
