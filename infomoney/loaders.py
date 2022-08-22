import re

from scrapy.loader import ItemLoader
from itemloaders.processors import Compose, TakeFirst


def replace_decimal_separator(value):
    """Replaces commas with points as decimal separator."""
    if value == 'n/d':
        return '0'
    if isinstance(value, str):
        return value.replace('.', '').replace(',', '.')
    return value


def pct_factor_decimal_separator(value):
    """Unexpected format for decimal separator in pct_factor field from source
    """
    if value == 'n/d':
        return '0'
    if isinstance(value, str):
        return re.sub(r'(.*\d+)(,)(\d{2})$', r'\1.\3', value).replace(',', '')
    return value


class BaseInfomoneyLoader(ItemLoader):
    default_output_processor = TakeFirst()


class AssetEarningsLoader(BaseInfomoneyLoader):
    value_out = Compose(TakeFirst(), replace_decimal_separator)
    pct_factor_out = Compose(TakeFirst(), pct_factor_decimal_separator)
    emission_value_out = Compose(TakeFirst(), replace_decimal_separator)


class AssetPriceLoader(BaseInfomoneyLoader):
    open_out = Compose(TakeFirst(), replace_decimal_separator)
    high_out = Compose(TakeFirst(), replace_decimal_separator)
    low_out = Compose(TakeFirst(), replace_decimal_separator)
    close_out = Compose(TakeFirst(), replace_decimal_separator)
    variation_out = Compose(TakeFirst(), replace_decimal_separator)
