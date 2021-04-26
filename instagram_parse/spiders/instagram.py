import json
import scrapy
import datetime as dt
from urllib.parse import urlencode
from ..items import InstagramTag, InstagramPost


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["https://www.instagram.com/"]
    _login_url = "/accounts/login/ajax/"
    api_url = "/graphql/query/"

    def __init__(self, login, password, users, *args, **kwargs):
        self.login = login
        self.password = password
        self.users = users
        super().__init__(*args)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                response.urljoin(self._login_url),
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password},
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]},
            )
        except AttributeError:
            if response.json()['authenticated']:
                for user in self.users:
                    yield response.follow(f"{user}/", callback=self.user_page_parse)

    def user_page_parse(self, response):
        js_data = self.js_data_extract(response)
        insta_tag = InstaTag(js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"])
        yield insta_tag.get_tag_item()
        yield from insta_tag.get_post_items()
        yield response.follow(
            f"{self.api_url}?{urlencode(insta_tag.paginate_params())}",
            callback=self._api_tag_parse,
        )

    def _api_tag_parse(self, response):
        data = response.json()
        insta_tag = InstaTag(data["data"]["hashtag"])
        yield from insta_tag.get_post_items()
        yield response.follow(
            f"{self.api_url}?{urlencode(insta_tag.paginate_params())}",
            callback=self._api_tag_parse,
        )

    def js_data_extract(self, response):
        script = response.xpath(
            "//body/script[contains(text(), 'window._sharedData =')]/text()"
        ).extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])


class InstaTag:
    query_hash = "5aefa9893005572d237da5068082d8d5"

    def __init__(self, hashtag: dict):
        self.variables = {
            "tag_name": hashtag["name"],
            "first": 50,
            "after": hashtag["edge_hashtag_to_media"]["page_info"]["end_cursor"],
        }
        self.hashtag = hashtag

    def get_tag_item(self):
        item = InstagramTag()
        item["date_parse"] = dt.datetime.now()
        data = {}
        for key, value in self.hashtag.items():
            if not (isinstance(value, dict) or isinstance(value, list)):
                data[key] = value
        item["data"] = data
        return item

    def paginate_params(self):
        url_query = {
            "query_hash": self.query_hash,
            "variables": json.dumps(self.variables)
        }
        return url_query

    def get_post_items(self):
        for edge in self.hashtag["edge_hashtag_to_media"]["edges"]:
            yield InstagramPost(
                date_parse=dt.datetime.now(),
                data=edge["node"],
                photos=edge["node"]["display_url"]
            )
