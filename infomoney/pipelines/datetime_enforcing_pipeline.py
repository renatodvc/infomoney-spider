import re
from datetime import datetime

from infomoney.items import AssetEarningsItem, AssetPriceItem


class DatetimeEnforcementPipeline:
    """Enforces the same date format for all items.
    FIIs returns earnings and price with format %d-%m-%YT%H:%M:%S, other assets
    returns earnings with %d/%m/%y and price with %d/%m/%Y.
    """

    def process_item(self, item, spider):
        if isinstance(item, AssetPriceItem):
            date = self.parse_date(item['date'])
            item['date'] = date

        elif isinstance(item, AssetEarningsItem):
            date = self.parse_date(item['date_of_payment'])
            item['date_of_payment'] = date
            if item.get('date_of_approval'):
                item['date_of_approval'] = self.parse_date(
                    item['date_of_approval']
                )
            if item.get('date_of_record'):
                item['date_of_record'] = self.parse_date(
                    item['date_of_record']
                )
        return item

    def parse_date(self, date):
        if date == 'n/d':
            return

        t_format = re.search(r'(\d{2})-(\d{2})-(20\d{2})T', date)
        if t_format:
            day, month, year = t_format.groups()
            return datetime.strptime(day + month + year, '%d%m%Y')

        try:
            dt = datetime.strptime(date, '%d/%m/%Y')
        except ValueError:
            dt = datetime.strptime(date, '%d/%m/%y')
        return dt
