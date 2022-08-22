from datetime import datetime
from decimal import Decimal
import hashlib
import logging

from scrapy.exceptions import NotConfigured
from sqlalchemy.exc import SQLAlchemyError, StatementError
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
            return self._process_price_item(item, force, spider)
        elif isinstance(item, AssetEarningsItem):
            return self._process_earnings_item(item, force, spider)
        else:
            return item

    def close_spider(self, spider):
        self.session.close()
        self.logger.debug('Closed database session.')

    def _process_earnings_item(self, item, force_update, spider):
        """Process an instance of the AssetEarningsItem into the data types the
        model expects and inserts into the DB.
        :param item: Item containing the data to be processed.
        :type item: Scrapy Item object.
        :param force_update: Flag to force the records to be updated in the DB
        :type force_update: bool
        """
        base_string = (
            f'{item["asset_code"]}{item["type"]}'
            f'{item.get("date_of_approval") or item.get("date_of_payment")}'
        )
        _id = self._build_hash_id(base_string)

        query = self.session.query(AssetEarningsModel) \
                    .filter(AssetEarningsModel._id == _id)
        record_exist = query.first()
        record = item.copy()  # Keeping the original item through the pipelines
        record.update({
            'value': self._convert_to_decimal(record.get('value')),
            'pct_factor': self._convert_to_decimal(record.get('pct_factor')),
            'emission_value': self._convert_to_decimal(
                record.get('emission_value')
            ),
            'date_of_approval': record.get('date_of_approval'),
            'date_of_record': record.get('date_of_record'),
            'date_of_payment': record.get('date_of_payment'),
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
            spider.crawler.stats.inc_value(
                f'dropped/sql/earnings/duplicated/{item["asset_code"]}'
            )
            return item

        try:
            self.session.commit()
        except (SQLAlchemyError, StatementError):
            self.session.rollback()
            self.logger.exception('Failed to commit the database transaction.')

        return item

    def _process_price_item(self, item, force_update, spider):
        """Process an instance of the AssetPriceItem into the data types the
        model expects and inserts into the DB.
        :param item: Item containing the data to be processed.
        :type item: Scrapy Item object.
        :param force_update: Flag to force the records to be updated in the DB
        :type force_update: bool
        """
        base_string = (
            f'{item["asset_code"]}{item.get("timestamp") or item["date"]}'
        )
        _id = self._build_hash_id(base_string)

        query = self.session.query(AssetPriceModel) \
                    .filter(AssetPriceModel._id == _id)
        record_exist = query.first()
        record = item.copy()  # Keeping the original item through the pipelines
        record.update({
            'date': record['date'],
            'timestamp': self._parse_timestamp(record.get('timestamp')),
            'open': self._convert_to_decimal(record.get('open')),
            'high': self._convert_to_decimal(record.get('high')),
            'low': self._convert_to_decimal(record.get('low')),
            'close': self._convert_to_decimal(record.get('close')),
            'variation': self._convert_to_decimal(record.get('variation')),
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
            spider.crawler.stats.inc_value(
                f'dropped/sql/price/duplicated/{item["asset_code"]}'
            )
            return item

        try:
            self.session.commit()
        except (SQLAlchemyError, StatementError):
            self.session.rollback()
            self.logger.exception('Failed to commit the database transaction.')

        return item

    def _build_hash_id(self, base_string):
        """Build unique identifier used to prevent duplicated data."""
        base_string = bytes(base_string, encoding='utf-8')
        return hashlib.md5(base_string).hexdigest()

    def _convert_to_decimal(self, value):
        return Decimal(value) if value else None

    def _parse_timestamp(self, timestamp):
        # Timestamp includes timing, but unrelated to market close.
        return datetime.fromtimestamp(int(timestamp)) if timestamp else None
