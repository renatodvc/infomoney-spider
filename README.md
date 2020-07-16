# INFOMONEY-SPIDER 
*This project is a web crawler developed with Scrapy for scraping historical price data of Brazilian Stocks from Infomoney website.*

Infomoney-spider é um web crawler desenvolvido com [Scrapy](https://scrapy.org/) para extração dos dados históricos de preço dos ativos da B3 disponibilizados na página [Infomoney](https://www.infomoney.com.br/).

## Instalando
Clone o repositório e instale as dependências.
```sh
$ git clone https://github.com/renatodvc/infomoney-spider.git
$ pip install -r requirements.txt
```
*Infomoney-spider requer Python 3.6+*

## Utilização
Execute no terminal:
```sh
$ scrapy crawl infomoney [-a param=value] 
```
### Parâmetros:
* **asset**: Código do ativo na B3. Se nenhum ativo for informado o spider fará requisições para todos os ativos disponíveis na [lista de cotações da Infomoney](https://www.infomoney.com.br/ferramentas/altas-e-baixas/).

Exemplo: `-a asset=PETR4`
* **start_date**: Busca os dados históricos a partir da data informada (utilizar padrão *dd/mm/yyyy*). Se nenhuma data for informada a requisição será feita para o período máximo disponível (2 anos).

Exemplo:  `-a start_date=01/01/2019`
* **end_date**: Busca os dados históricos até a data informada (utilizar padrão *dd/mm/yyyy*). Se nenhuma data for informada será utilizado o dia da execução. 

Exemplo:  `-a end_date=01/01/2020`
* **no_earnings**: Se `True` o spider não fará coleta dos dados de proventos (JSCP, dividendos, etc). Se não informado a coleta é realizada automaticamente.

Exemplo:  `-a no_earnings=True`

### Armazenamento de dados:
Os dados extraídos são armazenados em arquivos CSV na pasta `scraped_data`. Para alterar o diretório de armazenamento edite `FILES_STORAGE_FOLDER` e/ou `FILES_STORAGE_PATH` dentro do arquivo `settings.py`.

### Formato dos dados:
Os dados não sofrem alteração e são armazenados integralmente como são disponibilizados pela plataforma da Infomoney.

A estrutura colunar dos dados nos arquivos CSV seguem os seguintes padrões:

- Histórico de Preço

**`Data | Timestamp (POSIX Time) | Abertura | Máxima | Mínima | Fechamento | Volume | Variação`**

- Histórico de Proventos

**`Tipo | Valor | Data Aprovação | Data COM¹ | Data Pagamento | Situação`**

*¹: Infomoney informa este dado como "DATA COM". Possivelmente equivalente a [Data Ex-Dividendos](https://pt.wikipedia.org/wiki/Ex-dividendos).*


## A Fazer
 - Construir arquivo estático para reduzir a quantidade de requests
 - Incluir parâmetro para update do arquivo estático
 - Checar a existência do CSV e incluir parâmetros para incrementar ou substituir.
 - Construir pipeline para inserir dados em banco de dados.
 - Testes

## Licença
MIT