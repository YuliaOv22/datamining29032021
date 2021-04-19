import re
from urllib.parse import urljoin
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


def clear_price(price):
    try:
        result = float(price.replace("\u2009", ""))
    except ValueError:
        result = None
    return result


def get_characteristic(item: str) -> dict:
    selector = Selector(text=item)
    data = {
        "name": selector.xpath(
            '//div[contains(@class, "AdvertSpecs_label")]/text()'
        ).extract_first(),
        "value": selector.xpath(
            '//div[contains(@class, "AdvertSpecs_data")]//text()'
        ).extract_first(),
    }
    return data


def get_author_id(text):
    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
    result = re.findall(re_pattern, text)
    try:
        user_link = f"https://youla.ru/user/{result[0]}"
    except IndexError:
        user_link = None
        pass
    return user_link


def flat_text_salary(items):
    return "".join(items)

def flat_text_description(items):
    return "\n".join(items)


def hh_user_url(user_id):
    return urljoin("https://hh.ru/", user_id)


class HhLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = flat_text_salary
    description_out = flat_text_description
    author_in = MapCompose(hh_user_url)
    author_out = TakeFirst()
