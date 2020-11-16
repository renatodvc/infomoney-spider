import logging
import os

from scrapy.exceptions import NotConfigured
from scrapy.exporters import CsvItemExporter

from infomoney.items import AssetEarningsItem, AssetPriceItem


class SplitInCSVsPipeline:
    def __init__(self, file_directory):
        self.logger = logging.getLogger(__name__)
        self.file_directory = file_directory
        self.asset_exporters = {
            'earnings': {},
            'price': {},
        }

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        if not settings.get('FILES_STORAGE_PATH'):
            raise NotConfigured('CSV storage directory is not configured.')
        return cls(settings.get('FILES_STORAGE_PATH'))

    def process_item(self, item, spider):
        filename = self._get_filename(spider, item)
        if isinstance(item, AssetPriceItem):
            exporter = self._process_price_item(item, filename)
        elif isinstance(item, AssetEarningsItem):
            exporter = self._process_earnings_item(item, filename)
        else:
            return item
        exporter.export_item(item)
        return item

    def close_spider(self, spider):
        """Signal end of exporting process for all exporters."""
        for price_exporter in self.asset_exporters['price'].values():
            price_exporter.finish_exporting()
        for earnings_exporter in self.asset_exporters['earnings'].values():
            earnings_exporter.finish_exporting()

    def _process_price_item(self, item, filename):
        """Instantiate and store the price exporters for each asset code."""
        code = item['asset_code']
        if code not in self.asset_exporters['price']:
            file = open(filename, 'wb')
            exporter = CsvItemExporter(file)
            exporter.start_exporting()
            self.asset_exporters['price'][code] = exporter
        return self.asset_exporters['price'][code]

    def _process_earnings_item(self, item, filename):
        """Instantiate and store the earnings exporters for each asset code."""
        code = item['asset_code']
        if code not in self.asset_exporters['earnings']:
            file = open(filename, 'wb')
            exporter = CsvItemExporter(file)
            exporter.start_exporting()
            self.asset_exporters['earnings'][code] = exporter
        return self.asset_exporters['earnings'][code]

    def _get_filename(self, spider, item):
        """Determine the name of the CSV file depending on the data being
        exported or spider received arguments.
        """
        code = item['asset_code']
        start_arg = getattr(spider, 'start_date', None)
        end_arg = getattr(spider, 'end_date', None)
        if isinstance(item, AssetEarningsItem):
            filename = f'earnings_{code}.csv'
        elif start_arg or end_arg:  # Spider executed with custom dates args
            start_arg = start_arg.replace('/', '-') if start_arg else None
            end_arg = end_arg.replace('/', '-') if end_arg else None
            filename = f'custom_date_{code}_{start_arg}_to_{end_arg}.csv'
        else:
            filename = f'{code}.csv'

        return os.path.join(self.file_directory, filename)
