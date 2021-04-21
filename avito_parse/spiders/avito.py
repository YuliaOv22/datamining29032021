import scrapy
import re
from avito_parse.loaders import AvitoLoader


class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domapipins = ["avito.ru"]
    start_urls = ["https://www.avito.ru/krasnodar/kvartiry/prodam"]

    _xpath_selectors = {
        "pagination": '//div[@class="pagination-pages clearfix"]/a[@class="pagination-page"]/@href',
        "apartment": '//div[@class="iva-item-titleStep-2bjuh"]/a[@data-marker="item-title"]/@href'
    }

    _xpath_data_query_apartment = {
        "title": '//h1[@class="title-info-title"]/span[@class="title-info-title-text"]/text()',
        "price": '//span[@class="js-item-price"]/text()',
        "address": '//div[@itemprop="address"]//text()',
        "characteristics": '//li[@class="item-params-list-item"]//text()',
        "author_name": '//div[@class="seller-info-name js-seller-info-name"]/a/text()',
        "author_url": '//div[@class="seller-info-name js-seller-info-name"]/a/@href'
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.loader = None

    def _get_follow_xpath(self, response, selector, callback, **kwargs):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, **kwargs):
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["pagination"], self.parse
        )
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["apartment"], self.apartment_parse
        )

    def apartment_parse(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for key, selector in self._xpath_data_query_apartment.items():
            loader.add_xpath(key, selector)
        re_pattern = re.compile(r"et._([\d]+)")
        loader.add_value("phone_url", re.findall(re_pattern, loader.load_item()["url"]))
        yield loader.load_item()
