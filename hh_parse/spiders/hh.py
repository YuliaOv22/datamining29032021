import scrapy
from hh_parse.loaders import HhVacLoader, HhEmpLoader


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = ["https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"]

    _xpath_selectors = {
        "pagination": '//div[@data-qa="pager-block"]//a[@class="bloko-button"]/@href',
        "vacancy": '//div[contains(@data-qa, "vacancy-serp__vacancy")]//a[@data-qa="vacancy-serp__vacancy-title"]/@href'
    }

    _xpath_data_query_vacancy = {
        "title": '//h1[@data-qa="vacancy-title"]/text()',
        "salary": '//p[@class="vacancy-salary"]//text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "skills": '//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]/text()',
        "author": '//a[@data-qa="vacancy-company-name"]/@href'
    }

    _xpath_data_query_company = {
        "title": '//h1[@data-qa="bloko-header-1"]/span[@data-qa="company-header-title-name"]/text()',
        "url": '//div[@data-qa="sidebar-text-color"]//a[@data-qa="sidebar-company-site"]/@href',
        "profareas": '//div[@class="employer-sidebar-block"]/p/text()',
        "description": '//div[@data-qa="company-description-text"]//text()',
        "jobs_url": '//a[@data-qa="employer-page__employer-vacancies-link"]/@href'
    }

    def __init__(self, name=None, **kwargs):
        super().__init__(name=None, **kwargs)
        self.loader = None

    def _get_follow_xpath(self, response, selector, callback, **kwargs):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response):
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["pagination"], self.parse
        )
        yield from self._get_follow_xpath(
            response, self._xpath_selectors["vacancy"], self.vacancy_parse
        )

    def vacancy_parse(self, response):
        loader = HhVacLoader(response=response)
        loader.add_value("url", response.url)
        for key, selector in self._xpath_data_query_vacancy.items():
            loader.add_xpath(key, selector)
        yield loader.load_item()
        yield response.follow(loader.load_item()["author"], callback=self.company_parse)

    def company_parse(self, response):
        loader_2 = HhEmpLoader(response=response)
        loader_2.add_value("url", response.url)
        for key, selector in self._xpath_data_query_company.items():
            loader_2.add_xpath(key, selector)
        yield loader_2.load_item()
