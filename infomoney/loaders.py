from scrapy.loader import ItemLoader
from itemloaders.processors import Compose, TakeFirst


def replace_decimal_separator(value):
    """Replaces commas with points as decimal separator."""
    if value == 'n/d':
        return '0'
    return value.replace('.', '').replace(',', '.')


class BaseInfomoneyLoader(ItemLoader):
    default_output_processor = TakeFirst()


class AssetEarningsLoader(BaseInfomoneyLoader):
    value_out = Compose(TakeFirst(), replace_decimal_separator)
    pct_factor_out = Compose(TakeFirst(), replace_decimal_separator)
    emission_value_out = Compose(TakeFirst(), replace_decimal_separator)


class AssetPriceLoader(BaseInfomoneyLoader):
    open_out = Compose(TakeFirst(), replace_decimal_separator)
    high_out = Compose(TakeFirst(), replace_decimal_separator)
    low_out = Compose(TakeFirst(), replace_decimal_separator)
    close_out = Compose(TakeFirst(), replace_decimal_separator)
    variation_out = Compose(TakeFirst(), replace_decimal_separator)
