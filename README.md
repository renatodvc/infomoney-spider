# <p align="center">INFOMONEY-SPIDER</p>
*Infomoney-spider is a web crawler developed with [Scrapy](https://scrapy.org/) for scraping historical price data of Brazilian Stocks from [Infomoney](https://www.infomoney.com.br/) website. Infomoney provides daily price data (OHLCV) and earnings data for more than 700 assets.*

Infomoney-spider é um web crawler desenvolvido com [Scrapy](https://scrapy.org/) para extração dos dados históricos de preço dos ativos da B3 disponibilizados na página [Infomoney](https://www.infomoney.com.br/). A Infomoney disponibiliza dados de preço diário (OHLCV) e dados de proventos para mais de 700 ativos. [Leia-me em português :brazil:](#instalando)

## Instalando
Clone o repositório e instale as dependências.
```sh
$ git clone https://github.com/renatodvc/infomoney-spider.git
$ pip install -r requirements.txt
```
*Infomoney-spider requer Python 3.6+*

Se você pretende usar um banco de dados SQL para armazenar os dados, preencha o campo `DATABASE_URI` dentro de `settings.py` com as informações de conexão com o banco. (*O projeto usa a ORM do [SQLAlchemy](https://www.sqlalchemy.org/), verifique os [DBs suportados](https://docs.sqlalchemy.org/en/13/dialects/index.html)*).

Após preencher as o campo mencionado, **execute as migrações**:
```sh
$ alembic upgrade head
```

## Utilização
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

- **SplitInCSVsPipeline**: Os dados extraídos são armazenados em arquivos CSV na pasta `scraped_data`. Para alterar o diretório de armazenamento edite `FILES_STORAGE_FOLDER` e/ou `FILES_STORAGE_PATH` dentro do arquivo `settings.py`.

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
 - Incluir testes
 - Permitir operação de incrementar o CSV ao invés de sobrescrever.

## Licença
[MIT](https://github.com/renatodvc/infomoney-spider/blob/master/LICENSE)