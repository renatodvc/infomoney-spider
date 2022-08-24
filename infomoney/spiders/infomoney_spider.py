import json
from datetime import datetime, timedelta

from scrapy import FormRequest, Request, Spider
from scrapy.downloadermiddlewares.retry import get_retry_request
from w3lib.url import add_or_replace_parameter

from infomoney.items import AssetEarningsItem, AssetPriceItem
from infomoney.loaders import AssetEarningsLoader, AssetPriceLoader


class InfomoneySpider(Spider):
    """Spider designed to retrieve historical price and earnings data of
    Brazilian stocks from Infomoney website.
    """
    name = 'infomoney'
    results_per_page = 500

    # API URLs
    base_details_url = 'https://www.infomoney.com.br/{asset_code}'
    start_url = (
        'https://api.infomoney.com.br/markets/high-low/b3?sector=Todos&order'
        'Atributte=Volume&pageIndex={page}&pageSize={size}&search=&type=json'
    )
    fii_earnings_api = (
        'https://fii-api.infomoney.com.br/api/v1/fii/provento/'
        'historico?Ticker={asset_code}'
    )
    fii_price_api = (
        'https://fii-api.infomoney.com.br/api/v1/fii/cotacao/historico/'
        'grafico?Ticker={asset_code}'
    )
    earnings_api = (
        'https://www.infomoney.com.br/wp-json/infomoney/v1/quotes/earnings'
    )
    price_api = (
        'https://www.infomoney.com.br/wp-json/infomoney/v1/quotes/history'
    )

    # Broken URLs that redirect to wrong pages
    broken_asset_urls = {
        'BRPR3': 'https://www.infomoney.com.br/cotacoes/b3/acao/br-properties-brpr3/', # noqa E501
        'FRAS3': 'https://www.infomoney.com.br/cotacoes/b3/acao/fras-le-fras3/',  # noqa E501
        'HAGA4': 'https://www.infomoney.com.br/cotacoes/b3/acao/haga-haga4/',
        'ROMI3': 'https://www.infomoney.com.br/cotacoes/b3/acao/inds-romi-romi3/',  # noqa E501
        'TELB4': 'https://www.infomoney.com.br/cotacoes/b3/acao/telebras-telb4/',  # noqa E501
        'TPIS3': 'https://www.infomoney.com.br/cotacoes/b3/acao/triunfo-part-tpis3/',  # noqa E501
        'USIM3': 'https://www.infomoney.com.br/cotacoes/b3/acao/usiminas-usim3/',  # noqa E501
    }

    def start_requests(self):
        """Build initial request(s)"""
        assets = getattr(self, 'assets', None)
        if assets:
            self.logger.info('Requesting data for asset(s): %s', assets)
            for asset in assets.split(','):
                yield Request(
                    url=self.base_details_url.format(asset_code=asset),
                    callback=self.parse_details_page,
                    cb_kwargs={
                        'code': asset,
                    }
                )
        else:
            self.logger.info('Requesting data for ALL available assets.')
            yield Request(
                url=self.start_url.format(page=1, size=self.results_per_page),
                callback=self.parse
            )

    def parse(self, response):
        """Parse initial page"""
        data = response.json()
        for asset in data.get('Data'):
            code = asset.get('StockCode')
            yield Request(
                url=self.base_details_url.format(asset_code=code),
                callback=self.parse_details_page,
                cb_kwargs={'code': code},
            )

        if data.get('PageIndex') < data.get('TotalPages'):
            yield Request(
                url=self.start_url.format(
                    page=data.get('PageIndex') + 1,
                    size=self.results_per_page
                ),
                callback=self.parse
            )

    def parse_details_page(self, response, code):
        """Yields requests for the historical price data and earnings pages"""
        # The response is a redirect to the correct page for the asset code.
        if response.status == 404:
            self.logger.warning(
                'Page for %s didn\'t redirect, returned 404. Maybe the asset '
                'is no longer tradable.', code
            )
            return
        if response.url.endswith('.png') or response.url.endswith('.gif'):
            # A few assets links are redirecting to images (USIM3, HAGA4, etc)
            if code in self.broken_asset_urls:
                yield Request(
                    url=self.broken_asset_urls[code],
                    callback=self.parse_details_page,
                    cb_kwargs={'code': code}
                )
                return
            self.logger.error(
                'Details page for %s returned an unexpected response. URL: %s',
                code, response.url
            )
            return

        if not getattr(self, 'no_price', None) == 'True':
            yield self._make_price_request(response, code)
        if not getattr(self, 'no_earnings', None) == 'True':
            yield self._make_earnings_request(response, code)

    def _make_earnings_request(self, response, code):
        # FIIs have a different endpoint from other assets
        if 'b3/fii/' in response.url:
            url = self.fii_earnings_api.format(asset_code=code)
            return Request(
                url, callback=self.parse_fii_earnings, cb_kwargs={'code': code}
            )

        return FormRequest(
            url=self.earnings_api,
            callback=self.parse_earnings_data,
            cb_kwargs={'code': code},
            formdata={
                'symbol': code,
                'type': 'null',
                'page': '0',
                'perPage': str(self.results_per_page),
            },
        )

    def _make_price_request(self, response, code):
        # FIIs have a different endpoint from other assets
        if 'b3/fii/' in response.url:
            url = self.fii_price_api.format(asset_code=code)
            start_date, end_date = self._get_date_attributes(st_offset=365 * 5)
            url = add_or_replace_parameter(
                url, 'DataInicio', start_date.replace('/', '-')
            )
            url = add_or_replace_parameter(
                url, 'DataFim', end_date.replace('/', '-')
            )
            return Request(
                url, callback=self.parse_fii_prices, cb_kwargs={'code': code}
            )

        start_date, end_date = '', ''
        if getattr(self, 'start_date', None) or getattr(self, 'end_date', None):  # noqa E501
            start_date, end_date = self._get_date_attributes()

        return FormRequest(
            url=self.price_api,
            callback=self.parse_prices_data,
            cb_kwargs={'code': code},
            formdata={
                'page': '0',
                'numberItems': str(self.results_per_page),
                'initialDate': start_date,
                'finalDate': end_date,
                'symbol': code,
            },
        )

    def parse_fii_earnings(self, response, code):
        """Parse JSON with FII earnings data into Item."""
        data = self._is_data_valid(response, code, 'earnings')
        if not data:
            return get_retry_request(
                response.request, spider=self, reason='Invalid response'
            )

        data = response.json()
        for row in data:
            loader = AssetEarningsLoader(item=AssetEarningsItem())
            loader.add_value('asset_code', code)
            loader.add_value('type', 'Rendimento')
            loader.add_value('value', row['rendimento'])
            loader.add_value('pct_factor', row['yield'])
            loader.add_value('date_of_payment', row['data'])
            item = loader.load_item()
            yield item

        self.logger.info('Parsed %s earning records for %s', len(data), code)

    def parse_fii_prices(self, response, code):
        """Parse JSON with FII historical price data into Item."""
        data = self._is_data_valid(response, code, 'prices', 'dataValor')
        if not data:
            return get_retry_request(
                response.request, spider=self, reason='Invalid response'
            )

        for row in data['dataValor']:
            loader = AssetPriceLoader(item=AssetPriceItem())
            loader.add_value('asset_code', code)
            loader.add_value('date', row.get('data'))
            loader.add_value('close', row['valor'])
            item = loader.load_item()
            yield item

        self.logger.info(
            'Parsed %s price records for %s', len(data['dataValor']), code
        )

    def parse_earnings_data(self, response, code):
        """Parse JSON with earnings data into Item."""
        data = self._is_data_valid(response, code, 'earnings', 'aaData')
        if not data:
            return get_retry_request(
                response.request, spider=self, reason='Invalid response'
            )

        for row in data.get('aaData')[::-1]:
            loader = AssetEarningsLoader(item=AssetEarningsItem())
            loader.add_value('asset_code', code)
            loader.add_value('type', row[0])
            loader.add_value('value', row[1])
            loader.add_value('pct_factor', row[2])
            loader.add_value('emission_value', row[3])
            loader.add_value('date_of_approval', row[4])
            loader.add_value('date_of_record', row[5])
            loader.add_value('date_of_payment', row[6])
            item = loader.load_item()
            yield item

        self.logger.info(
            'Parsed %s earnings records for %s', len(data.get('aaData')), code
        )

    def parse_prices_data(self, response, code):
        """Parse JSON with historical price data into Item."""
        data = self._is_data_valid(response, code, 'prices')
        if not data:
            return get_retry_request(
                response.request, spider=self, reason='Invalid response'
            )

        for row in data[::-1]:
            loader = AssetPriceLoader(item=AssetPriceItem())
            loader.add_value('asset_code', code)
            loader.add_value('date', row[0].get('display'))
            loader.add_value('timestamp', row[0].get('timestamp'))
            loader.add_value('open', row[1])
            loader.add_value('high', row[5])
            loader.add_value('low', row[4])
            loader.add_value('close', row[2])
            loader.add_value('volume', row[6])
            loader.add_value('variation', row[3])
            item = loader.load_item()
            yield item

        self.logger.info('Parsed %s price records for %s', len(data), code)

    def _is_data_valid(self, response, code, _type, *args):
        """Checks if the response isn't empty or malformed.
        :param response: Response to the request
        :type response: Scrapy Response object.
        :param code: Asset code for the request.
        :type code: str
        :param _type: Type of data expected from the response, used only for
        logging purposes.
        :type _type: str
        :param *args: Keys that are expected in the response JSON.
        :type *args: List[str]
        """
        if not response.body:
            self.logger.warning(
                'Response for %s %s returned empty.', code, _type
            )
            return

        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            self.logger.exception(
                'Response for %s %s couldn\'t be parsed.', code, _type
            )
            return

        if not data or isinstance(data, bool):
            self.logger.warning(
                'Response for %s %s returned a malformed JSON.', code, _type
            )
            return

        for key in args:
            if key not in data:
                self.logger.warning(
                    "Expected key %s for %s %s isn't included in the response",
                    key, code, _type
                )
                return

        return data

    def _get_date_attributes(self, st_offset=730):
        """Return date values according to received args or standard values.
        :param st_offset: Number of days to offset the initial date. Default to
        730 (2 years).
        :type st_offset: int
        """
        start_arg = getattr(self, 'start_date', None)
        end_arg = getattr(self, 'end_date', None)

        initial_date = (
            start_arg or
            (datetime.today() - timedelta(days=st_offset)).strftime('%d/%m/%Y')
        )
        final_date = end_arg or datetime.today().strftime('%d/%m/%Y')
        return initial_date, final_date
