import scrapy
import pymongo
import re
import base64
import urllib


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']
    _css_selectors = {
        "brands": "div.ColumnItemList_container__5gTrc a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "car": "#serp article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu",
        "title": ".AdvertCard_advertTitle__1S1Ak",
        "description": ".AdvertCard_descriptionInner__KnuRi",
        "img": "div.PhotoGallery_photoWrapper__3m7yM figure.PhotoGallery_photo__36e_r img"
    }

    def _get_follow(self, response, selector_css, callback, **kwargs):
        for link_selector in response.css(selector_css):
            yield response.follow(link_selector.attrib.get("href"), callback=callback)

    def parse(self, response, **kwargs):
        yield from self._get_follow(response, self._css_selectors["brands"], self.brand_parse)

    def brand_parse(self, response):
        yield from self._get_follow(response, self._css_selectors["pagination"], self.brand_parse)
        yield from self._get_follow(response, self._css_selectors["car"], self.car_parse)

    def car_parse(self, response):
        data = {
            "title": response.css(f'{self._css_selectors["title"]}::text').get(),
            "url": response.url,
            "price": response.css("div.AdvertCard_price__3dDCr::text").get().replace("\u2009", " "),
            "description": response.css(f'{self._css_selectors["description"]}::text').get(),
            "img_list": AutoyoulaSpider.get_photos(response),
            "characteristics": [
                {
                    "name": itm.css(".AdvertSpecs_label__2JHnS::text").get(),
                    "value": itm.css(".AdvertSpecs_data__xK2Qx a.blackLink::text").get() or itm.css(
                        ".AdvertSpecs_data__xK2Qx::text").get()
                }
                for itm in response.css("div.AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX")
            ],
            "author_url": AutoyoulaSpider.get_author_id(response),
            "phone": AutoyoulaSpider.get_phone(response)
        }
        self.db_client["autoyoula_parse"][self.name].insert_one(data)

    @staticmethod
    def get_photos(response):
        marker_photos = "window.transitState = decodeURIComponent"
        for script in response.css("script"):
            try:
                if marker_photos in script.css("::text").get():
                    re_pattern_photos = re.compile(r"%2Fdocument%2Fm%2F([a-zA-Z|\d\-%.]+)%22%2C%22isCatalog")
                    result_photos = re.findall(re_pattern_photos, script.css("::text").get())
                    img_list = []
                    for img_url in result_photos:
                        img_list.append(
                            f"https://static.am/automobile_m3/document/l/{urllib.parse.unquote_plus(img_url)}")
                    return (
                        img_list
                        if result_photos
                        else None
                    )
            except TypeError:
                pass

    @staticmethod
    def get_author_id(response):
        marker = "window.transitState = decodeURIComponent"
        for script in response.css("script"):
            try:
                if marker in script.css("::text").get():
                    re_pattern_users = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern_users, script.css("::text").get())
                    if not result:
                        re_pattern_cardealers = re.compile(r"cardealers%2F([a-zA-Z|\d\-]+)%2F%23info")
                        result_cardealers = re.findall(re_pattern_cardealers, script.css("::text").get())
                        return (
                            response.urljoin(f"/cardealers/{result_cardealers[0]}")
                            if result_cardealers
                            else None
                        )
                    return (
                        response.urljoin(f"/user/{result[0]}").replace("auto.", "", 1)
                        if result
                        else None
                    )
            except TypeError:
                pass

    @staticmethod
    def get_phone(response):
        marker_phone = "window.transitState = decodeURIComponent"
        for script in response.css("script"):
            try:
                if marker_phone in script.css("::text").get():
                    re_pattern_phone = re.compile(r"phone%22%2C%22([a-zA-Z|\d]+)%3D%3D%22%2C%22time")
                    result_phone = re.findall(re_pattern_phone, script.css("::text").get())
                    return (
                        base64.b64decode(base64.b64decode(
                            base64.b64decode(base64.b64encode(result_phone[0].encode("ascii"))) + b'==')).decode(
                            "utf-8")
                        if result_phone
                        else None
                    )
            except TypeError:
                pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient("mongodb://localhost:27017")
