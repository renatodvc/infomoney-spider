from datetime import datetime
from decimal import Decimal
import hashlib
import logging

from scrapy.exceptions import NotConfigured
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session

from infomoney.models import (
    session_factory, AssetEarningsModel, AssetPriceModel
)
from infomoney.items import AssetEarningsItem, AssetPriceItem


class StoreInDatabasePipeline:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = scoped_session(session_factory)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        if not settings.get('DATABASE_URI'):
            raise NotConfigured('Database settings are not configured.')
        return cls()

    def process_item(self, item, spider):
        force = getattr(spider, 'force', None) == 'True'
        if isinstance(item, AssetPriceItem):
            return self._process_price_item(item, force)
        elif isinstance(item, AssetEarningsItem):
            return self._process_earnings_item(item, force)
        else:
            return item

    def close_spider(self, spider):
        self.session.close()
        self.logger.debug('Closed database session.')

    def _process_earnings_item(self, item, force_update):
        """Process an instance of the AssetEarningsItem into the data types the
        model expects and inserts into the DB.
        :param item: Item containing the data to be processed.
        :type item: Scrapy Item object.
        :param force_update: Flag to force the records to be updated in the DB
        :type force_update: bool
        """
        base_string = (
            f'{item["asset_code"]}{item["type"]}{item["date_of_approval"]}'
        )
        _id = self._build_hash_id(base_string)

        query = self.session.query(AssetEarningsModel) \
                    .filter(AssetEarningsModel._id == _id)
        record_exist = query.first()
        record = item.copy()  # Keeping the original item through the pipelines
        record.update({
            'value': Decimal(record['value']),
            'pct_factor': Decimal(record['pct_factor']),
            'emission_value': Decimal(record['emission_value']),
            'date_of_approval': self._parse_date(record['date_of_approval']),
            'date_of_record': self._parse_date(record['date_of_record']),
            'date_of_payment': self._parse_date(record['date_of_payment']),
        })

        if not record_exist:
            row = AssetEarningsModel(**record)
            row._id = _id
            self.session.add(row)
        elif force_update:
            self.logger.debug('Updating record "%s".', _id)
            query.update(record, synchronize_session=False)
        else:
            self.logger.debug(
                'Record "%s" already exists in the database, dropping...', _id
            )
            return item

        try:
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            self.logger.exception('Failed to commit the database transaction.')

        return item

    def _process_price_item(self, item, force_update):
        """Process an instance of the AssetPriceItem into the data types the
        model expects and inserts into the DB.
        :param item: Item containing the data to be processed.
        :type item: Scrapy Item object.
        :param force_update: Flag to force the records to be updated in the DB
        :type force_update: bool
        """
        base_string = f'{item["asset_code"]}{item["timestamp"]}'
        _id = self._build_hash_id(base_string)

        query = self.session.query(AssetPriceModel) \
                    .filter(AssetPriceModel._id == _id)
        record_exist = query.first()
        record = item.copy()  # Keeping the original item through the pipelines
        record.update({
            'date': self._parse_date(record['date']),
            'timestamp': self._parse_timestamp(record['timestamp']),
            'open': Decimal(record['open']),
            'high': Decimal(record['high']),
            'low': Decimal(record['low']),
            'close': Decimal(record['close']),
            'variation': Decimal(record['variation']),
        })

        if not record_exist:
            row = AssetPriceModel(**record)
            row._id = _id
            self.session.add(row)
        elif force_update:
            self.logger.debug('Updating record "%s".', _id)
            query.update(record, synchronize_session=False)
        else:
            self.logger.debug(
                'Record "%s" already exists in the database, dropping...', _id
            )
            return item

        try:
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            self.logger.exception('Failed to commit the database transaction.')

        return item

    def _build_hash_id(self, base_string):
        """Build unique identifier used to prevent duplicated data."""
        base_string = bytes(base_string, encoding='utf-8')
        return hashlib.md5(base_string).hexdigest()

    def _parse_date(self, date):
        # Date will always store time as 00:00:00
        if date == 'n/d':
            return
        try:
            return datetime.strptime(date, '%d/%m/%Y')
        except ValueError:
            return datetime.strptime(date, '%d/%m/%y')

    def _parse_timestamp(self, timestamp):
        # Timestamp includes timing, but unrelated to market close.
        return datetime.fromtimestamp(int(timestamp))
