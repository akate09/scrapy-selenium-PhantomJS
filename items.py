# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TaobaoItem(scrapy.Item):
    title= scrapy.Field()
    price = scrapy.Field()
    deal = scrapy.Field()
    image_url = scrapy.Field()
    place = scrapy.Field()
    shop_name = scrapy.Field()
    comment = scrapy.Field()
