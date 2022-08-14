# <p align="center">INFOMONEY-SPIDER</p>
*Infomoney-spider is a web crawler developed with [Scrapy](https://scrapy.org/) for scraping historical price data of Brazilian Stocks from [Infomoney](https://www.infomoney.com.br/) website. Infomoney provides daily price data (OHLCV) and earnings data for more than 700 assets. [English readme :gb:/:us:](#installation)*

Infomoney-spider é um web crawler desenvolvido com [Scrapy](https://scrapy.org/) para extração dos dados históricos de preço dos ativos da B3 disponibilizados na página [Infomoney](https://www.infomoney.com.br/). A Infomoney disponibiliza dados de preço diário (OHLCV) e dados de proventos para mais de 700 ativos. [Leia-me em português :brazil:](#instalando)

## Instalando
Clone o repositório e instale as dependências.
```sh
$ git clone https://github.com/renatodvc/infomoney-spider.git
$ pip install -r requirements.txt
```
*Infomoney-spider requer Python 3.6+*

Se você pretende usar um banco de dados SQL para armazenar os dados:
- Preencha o campo `DATABASE_URI` dentro de `settings.py` com as informações de conexão com o banco. 
	- *O projeto usa a ORM do [SQLAlchemy](https://www.sqlalchemy.org/), verifique os [DBs suportados](https://docs.sqlalchemy.org/en/13/dialects/index.html)*.

- Após preencher o campo `DATABASE_URI`, **execute as migrações**:
```sh
$ alembic upgrade head
```

## Executando o spider
Execute no terminal:
```sh
$ scrapy crawl infomoney [-a param=value] 
```

### Parâmetros aceitos:
*Todos os parâmetros são opcionais.*
- **asset**: Código do ativo na B3. Se nenhum ativo for informado o spider fará requisições para todos os ativos disponíveis na [lista de cotações da Infomoney](https://www.infomoney.com.br/ferramentas/altas-e-baixas/). Ex: `-a asset=PETR4`
- **start_date**: Busca os dados históricos a partir da data informada (utilizar padrão *dd/mm/yyyy*). Se nenhuma data for informada a requisição será feita para o período máximo disponível (2 anos). Ex: `-a start_date=01/01/2019`
- **end_date**: Busca os dados históricos até a data informada (utilizar padrão *dd/mm/yyyy*). Se nenhuma data for informada será utilizado o dia da execução. Ex: `-a end_date=01/01/2020`
- **no_earnings**: Se `True` o spider não fará coleta dos dados de proventos (JSCP, dividendos, etc). Se não informado a coleta é realizada automaticamente. Ex: `-a no_earnings=True`
- **no_price**: Se `True` o spider não fará coleta dos dados de preço (Abertura, Máxima, Fechamento, etc). Se não informado a coleta é realizada automaticamente. Ex: `-a no_price=True`
- **force**: Se `True` o spider atualizará os registros já existentes no banco de dados com as novas informações obtidas. Se não informado registros que já constam no banco de dados serão ignorados. **AFETA APENAS BANCO DE DADOS SQL**. Ex: `-a force=True`

### Pipelines:
Por padrão ambos os pipelines `SplitInCSVsPipeline` e `StoreInDatabasePipeline` estão ativados, você pode alterar isto comentando suas linhas no arquivo `settings.py`.

- **SplitInCSVsPipeline**: Os dados extraídos são armazenados em arquivos CSV na pasta `csv_output`. Para alterar o diretório de armazenamento edite `FILES_STORAGE_FOLDER` e/ou `FILES_STORAGE_PATH` dentro do arquivo `settings.py`. Os dados de cada ativo são armazenados em arquivos diferentes, dados de proventos também são separados dos dados de preços.

- **StoreInDatabasePipeline**: Se nenhuma informação de conexão com o banco de dados for incluída no campo `DATABASE_URI` do `settings.py`, essa pipeline se desativará automaticamente. A pipeline utiliza da ORM do [SQLAlchemy](https://www.sqlalchemy.org/), para suportar diferentes opções de banco de dados, [veja quais são eles](https://docs.sqlalchemy.org/en/13/dialects/index.html). Quando ativa, os dados de preço e proventos serão armazenados nas tabelas `assets_earnings` e `assets_prices` respectivamente. 

### Alertas:
- `INFO: Earnings data for XXXX returned empty.`: A maioria dos ativos listados não possuem dados de proventos disponíveis.
- `ERROR: No redirect from asset code BLCP11. Page returned 404.`: A página de alguns ativos não redireciona como esperado, é possível que a página exista, mas o link que consta na [fonte](https://www.infomoney.com.br/ferramentas/altas-e-baixas) está quebrado.
- `SQLite Decimals Dialect sqlite+pysqlite does *not* support Decimal objects natively, and SQLAlchemy must convert from floating point - rounding errors and other issues may occur. Please consider storing Decimal numbers as strings or integers on this platform for lossless storage.`: Os dados numéricos são armazenados como objetos Decimals, o banco de dados SQLite não suporta esse tipo nativamente, o que pode causar problemas de arredondamento.

### Formato dos dados:
Os dados não sofrem alteração e são armazenados integralmente como são disponibilizados pela plataforma da Infomoney.

A estrutura colunar dos dados na fonte seguem os seguintes padrões:

- Histórico de Preço:

**`Data | Timestamp (POSIX Time) | Abertura | Máxima | Mínima | Fechamento | Volume | Variação`**

- Histórico de Proventos:

**`Tipo | Valor | % / Fator | Valor Emissão | Data de Aprovação | Data de Ex-Dividendos¹ | Data de Pagamento`**

*¹: [Data Ex-Dividendos](https://pt.wikipedia.org/wiki/Ex-dividendos).*

## A Fazer
 - Incluir testes.
 - Permitir operação de incrementar o CSV ao invés de sobrescrever.

## Licença
[MIT](https://github.com/renatodvc/infomoney-spider/blob/master/LICENSE)

---
 ![](https://github.githubassets.com/images/icons/emoji/unicode/1f1ec-1f1e7.png?v8) ![](https://github.githubassets.com/images/icons/emoji/unicode/1f1fa-1f1f8.png?v8)

## Installation
Clone the repository and install the dependencies.
```sh
$ git clone https://github.com/renatodvc/infomoney-spider.git
$ pip install -r requirements.txt
```
*Infomoney-spider requires Python 3.6+*

If you plan to use a SQL database to store the data:
- Fill in the `DATABASE_URI` field within `settings.py` with your DB connection information.
	- *The project uses [SQLAlchemy](https://www.sqlalchemy.org/) ORM, check the [supported DBs](https://docs.sqlalchemy.org/en/13/dialects/index.html)*.

- After filling in the `DATABASE_URI` field, **execute the migrations**:
```sh
$ alembic upgrade head
```

## Executing the spider
Run in terminal:
```sh
$ scrapy crawl infomoney [-a param=value] 
```

### Accepted parameters:
*All parameters are optional.*
- **asset**: Asset code in B3 (Brazillian stock exchange). If no asset is informed, the spider will make requests for all assets available in the [Infomoney's asset list](https://www.infomoney.com.br/ferramentas/altas-e-baixas/). Ex: `-a asset=PETR4`
- **start_date**: Search the historical data starting from the informed date (use *dd/mm/yyyy* format). If no date is given, the request will be made for the maximum available period (2 years). Ex: `-a start_date=01/01/2019`
- **end_date**: Search historical data up to the given date (use *dd/mm/yyyy* format). If no date is given, the current day will be used. Ex: `-a end_date=01/01/2020`
- **no_earnings**: If `True` the spider will not collect the earnings data. If not informed, scraping is performed automatically. Ex: `-a no_earnings=True`
- **no_price**: If `True` the spider will not collect the price data (Open, High, Close ...). If not informed, scraping is performed automatically. Ex: `-a no_price=True`
- **force**: If `True` the spider will update the existing records in the database with the most recent information obtained. If not informed, records that already exist in the database will be ignored. **AFFECTS ONLY SQL DATABASE**. Ex: `-a force=True`

### Pipelines:
By default, both the `SplitInCSVsPipeline` and `StoreInDatabasePipeline` pipelines are enabled, you can change this by commenting out their lines in the `settings.py` file.

- **SplitInCSVsPipeline**: The extracted data is stored in CSV files in the `csv_output` folder. To change the storage directory, edit `FILES_STORAGE_FOLDER` and/or `FILES_STORAGE_PATH` inside the `settings.py` file. The data for each asset is stored in a different file, earnings data are also separated from the price data.

- **StoreInDatabasePipeline**: If no database connection information is included in the `DATABASE_URI` field of `settings.py`, this pipeline will be disabled automatically. The pipeline uses the [SQLAlchemy](https://www.sqlalchemy.org/) ORM, to support multiple database options, [see what they are](https://docs.sqlalchemy.org/en/13/dialects/index.html). When activated, the price and earnings data will be stored in the `assets_earnings` and `assets_prices` tables respectively.

### Warnings:
- `INFO: Earnings data for XXXX returned empty.`: Most of the listed assets do not have earnings data available.
- `ERROR: No redirect from asset code BLCP11. Page returned 404.`: Some asset pages doesn't redirect as expected, it is possible that the page exists, but the link in the [source page](https://www.infomoney.com.br/ferramentas/altas-e-baixas) is broken.
- `SQLite Decimals Dialect sqlite+pysqlite does *not* support Decimal objects natively, and SQLAlchemy must convert from floating point - rounding errors and other issues may occur. Please consider storing Decimal numbers as strings or integers on this platform for lossless storage.`: Numerical data is stored as Decimal objects, the SQLite database does not support this type natively, which can cause rounding errors and other issues.

### Data format:
The data is not altered by the spider and is stored in its entirety as provided by the Infomoney platform. (*Data types are converted when storing in SQL databases.*)

The columnar structure of the data at the source follows these patterns:

- Price data:

**`Date | Timestamp (POSIX Time) | Open | High | Low | Close | Volume | Variation`**

- Earnings data:

**`Type | Value | % / Factor | Emission Value | Approval Date | Date of Record¹ | Date of Payment`**

*¹: [Ex-dividend date](https://en.wikipedia.org/wiki/Ex-dividend_date).*

## TODO
 - Write tests.
 - Allow for append operations in the CSV instead of overwriting.

## License
[MIT](https://github.com/renatodvc/infomoney-spider/blob/master/LICENSE)
