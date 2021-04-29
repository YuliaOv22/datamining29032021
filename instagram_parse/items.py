# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Instagram(scrapy.Item):
    _id = scrapy.Field()
    f_list = scrapy.Field()


class InstagramConnection(Instagram):
    pass
