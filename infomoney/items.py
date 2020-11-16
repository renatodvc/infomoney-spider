import scrapy


class AssetPriceItem(scrapy.Item):
    asset_code = scrapy.Field()
    date = scrapy.Field()
    timestamp = scrapy.Field()
    open = scrapy.Field()
    high = scrapy.Field()
    low = scrapy.Field()
    close = scrapy.Field()
    volume = scrapy.Field()
    variation = scrapy.Field()


class AssetEarningsItem(scrapy.Item):
    asset_code = scrapy.Field()
    type = scrapy.Field()
    value = scrapy.Field()
    pct_factor = scrapy.Field()
    emission_value = scrapy.Field()
    date_of_approval = scrapy.Field()
    date_of_record = scrapy.Field()
    date_of_payment = scrapy.Field()
