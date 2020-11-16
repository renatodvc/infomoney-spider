import json
from datetime import datetime, timedelta

from scrapy import FormRequest, Request, Spider

from infomoney.items import AssetEarningsItem, AssetPriceItem
from infomoney.loaders import AssetEarningsLoader, AssetPriceLoader


class InfomoneySpider(Spider):
    """Spider designed to retrieve historical price data of Brazilian stocks
    from Infomoney website.
    """
    name = "infomoney"
    start_url = 'https://www.infomoney.com.br/ferramentas/altas-e-baixas/'
    api_url = 'https://www.infomoney.com.br/wp-admin/admin-ajax.php'
    base_details_url = 'https://www.infomoney.com.br/{asset_code}'
    results_per_page = 1000

    def start_requests(self):
        """Build initial request(s)"""
        asset = getattr(self, 'asset', None)
        if asset:
            self.logger.info('Requesting data for single asset %s', asset)
            yield Request(
                url=self.base_details_url.format(asset_code=asset),
                callback=self.parse_details_page,
                cb_kwargs={
                    'code': asset,
                }
            )
        else:
            self.logger.info('Requesting data for ALL available assets.')
            yield Request(url=self.start_url, callback=self.parse)

    def parse(self, response):
        """Parse initial page"""
        nonce = response.xpath('//script').re_first(
            r'altas_e_baixas_table_nonce":"(\w+)",'
        )
        yield self._build_asset_list_request(nonce)

    def parse_asset_list(self, response, page):
        """Parse asset list page, yields requests for details page for every
        asset available.
        """
        result = json.loads(response.body)
        if result['iTotalRecords'] >= self.results_per_page:
            next_page = page + 1
            nonce = response.meta.get('nonce')
            yield self._build_asset_list_request(nonce, next_page)

        for asset in result.get('aaData'):
            code = asset[1]
            yield Request(
                url=self.base_details_url.format(asset_code=code),
                callback=self.parse_details_page,
                cb_kwargs={
                    'code': code
                },
            )

    def parse_details_page(self, response, code):
        """Yields requests for the historical price data and earnings pages"""
        # The response is a redirect to the correct page for the asset code.
        if response.status == 404:
            self.logger.error(
                'No redirect from asset code %s. Page returned 404.', code
            )
            return
        if response.url.endswith('.png') or response.url.endswith('.gif'):
            # A few assets links are redirecting to images (USIM3, HAGA4, etc)
            self.logger.error(
                'Details page for %s can\'t be parsed. URL: %s',
                code,
                response.url
            )
            return

        escape_price = getattr(self, 'no_price', None) == 'True'
        if not escape_price:
            yield Request(
                url=response.urljoin('historico/'),
                callback=self.parse_historic_page,
                cb_kwargs={'code': code}
            )

        escape_earnings = getattr(self, 'no_earnings', None) == 'True'
        if not escape_earnings:
            yield Request(
                url=response.urljoin('proventos/'),
                callback=self.parse_earnings_page,
                cb_kwargs={'code': code}
            )

    def parse_historic_page(self, response, code):
        """Parse historic page, yields requests for the price data"""
        nonce = response.xpath('//script').re_first(
            r'quotes_history_nonce":"(\w+)"'
        )
        start_date, end_date = self._get_date_attributes()

        form = {
            'symbol': code,
            'quotes_history_nonce': nonce,
            'numberItems': '99999',
            'page': '0',
            'action': 'more_quotes_history',
            'initialDate': start_date,
            'finalDate': end_date,
        }
        yield FormRequest(
            url=self.api_url,
            formdata=form,
            callback=self.parse_historical_data,
            cb_kwargs={
                'code': code
            },
            dont_filter=True,
        )

    def parse_historical_data(self, response, code):
        """Parse JSON with historical price data into CSV."""
        results = json.loads(response.body)
        if isinstance(results, bool):
            self.logger.error(
                'Server failed in returning the historical price data for %s',
                code
            )
            return
        if not results:
            self.logger.warning('Price data for %s returned empty.', code)
            return

        for row in results:
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

    def parse_earnings_page(self, response, code):
        """Parse earnings page, yields requests for the earnings data"""
        nonce = response.xpath('//script').re_first(
            r'quotes_earnings_nonce":"(\w+)"'
        )
        form = {
            'symbol': code,
            'quotes_earnings_nonce': nonce,
            'page': '0',
            'type': 'null',
            'action': 'more_quotes_earnings',
            'perPage': '100'
        }

        yield FormRequest(
            url=self.api_url,
            formdata=form,
            callback=self.parse_earnings_data,
            cb_kwargs={
                'code': code
            },
            dont_filter=True,
        )

    def parse_earnings_data(self, response, code):
        """Parse JSON with earnings data into CSV."""
        results = json.loads(response.body)
        if isinstance(results, bool):
            self.logger.error(
                'Server failed in returning the earnings data for %s', code
            )
            return
        if not results.get('aaData'):
            self.logger.info('Earnings data for %s returned empty.', code)
            return

        results = results.get('aaData')
        for row in results:
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

    def _build_asset_list_request(self, nonce, page=1):
        """Builds request for asset list page"""
        form = {
            'action': 'tool_altas_e_baixas',
            'pagination': f'{page}',
            'perPage': f'{self.results_per_page}',
            'altas_e_baixas_table_nonce': nonce,
            'market': '0'
        }
        return FormRequest(
            url=self.api_url,
            formdata=form,
            callback=self.parse_asset_list,
            cb_kwargs={
                'page': page
            },
            meta={
                'nonce': nonce
            },
            dont_filter=True,
        )

    def _get_date_attributes(self):
        """Return date values according to received args or standard values."""
        start_arg = getattr(self, 'start_date', None)
        end_arg = getattr(self, 'end_date', None)

        initial_date = (
            start_arg or
            (datetime.today() - timedelta(days=730)).strftime('%d/%m/%Y')
        )
        final_date = end_arg or datetime.today().strftime('%d/%m/%Y')
        return initial_date, final_date
