from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


def flat_text(items):
    return "".join(items).replace("\n ", "")


def avito_full_url(url_part):
    return urljoin("https://avito.ru/", url_part)


def phone_url(url):
    return urljoin("https://www.avito.ru/web/1/items/phone/", url)


class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_out = TakeFirst()
    address_out = flat_text
    characteristics = flat_text
    author_name_in = TakeFirst()
    author_name_out = flat_text
    author_url_in = MapCompose(avito_full_url)
    author_url_out = TakeFirst()
    phone_url_in = MapCompose(phone_url)
    phone_url_out = TakeFirst()
