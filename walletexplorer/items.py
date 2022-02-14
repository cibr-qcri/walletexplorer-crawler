# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WalletexplorerItem(scrapy.Item):
    addresses = scrapy.Field()
    type = scrapy.Field()
    name = scrapy.Field()
    response = scrapy.Field()
    timestamp = scrapy.Field()
    service_url = scrapy.Field()

