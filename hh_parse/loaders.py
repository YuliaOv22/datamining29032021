from urllib.parse import urljoin
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


def flat_text_salary(items):
    return "".join(items)


def flat_text_description(items):
    return "\n".join(items)


def hh_user_url(url_part):
    return urljoin("https://hh.ru/", url_part)


class HhVacLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = flat_text_salary
    description_out = flat_text_description
    author_in = MapCompose(hh_user_url)
    author_out = TakeFirst()


class HhEmpLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = flat_text_salary
    description_out = flat_text_description
    jobs_url_in = MapCompose(hh_user_url)
    jobs_url_out = TakeFirst()
