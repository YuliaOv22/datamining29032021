import json
import scrapy
from urllib.parse import urlencode
from ..items import InstagramConnection


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
                    yield response.follow(f"{self.start_urls[0]}{user}/", callback=self.user_page_parse)

    def user_page_parse(self, response):
        js_data = self.js_data_extract(response)
        insta_user_id = InstaUser(js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"])
        yield response.follow(f"{self.api_url}?{urlencode(insta_user_id.paginate_params_followers)}",
                              callback=self._api_followers_parse)
        yield response.follow(f"{self.api_url}?{urlencode(insta_user_id.paginate_params_followings)}",
                              callback=self._api_followings_parse)

    def _api_followers_parse(self, response):
        data = response.json()
        followers = InstaUserConnections(data)
        yield followers.get_followers()

    def _api_followings_parse(self, response):
        data = response.json()
        followings = InstaUserConnections(data)
        yield followings.get_followings()

    def js_data_extract(self, response):
        script = response.xpath(
            "//body/script[contains(text(), 'window._sharedData =')]/text()"
        ).extract_first()
        return json.loads(script.replace("window._sharedData = ", "")[:-1])


class InstaUser:
    query_hash_followers = "5aefa9893005572d237da5068082d8d5"
    query_hash_followings = "3dec7e2c57367ef3da3d987d89f9dbc8"

    def __init__(self, user: dict):
        self.variables = dict(id=user["id"], first=100)
        self.user = user

    def paginate_params_followers(self):
        url_query = {
            "query_hash": self.query_hash_followers,
            "variables": json.dumps(self.variables)
        }
        return url_query

    def paginate_params_followings(self):
        url_query = {
            "query_hash": self.query_hash_followings,
            "variables": json.dumps(self.variables)
        }
        return url_query


class InstaUserConnections:
    def __init__(self, data: dict):
        self.data = data

    def get_followers(self):
        item = InstagramConnection()
        followers = []
        for usr in range(len(self.data["data"]["user"]["edge_followed_by"]["edges"])):
            followers.append(self.data["data"]["user"]["edge_followed_by"]["edges"][usr]["node"]["username"])
        item["f_list"] = followers
        return item

    def get_followings(self):
        item = InstagramConnection()
        followings = []
        for usr in range(len(self.data["data"]["user"]["edge_follow"]["edges"])):
            followings.append(self.data["data"]["user"]["edge_follow"]["edges"][usr]["node"]["username"])
        item["f_list"] = followings
        return item
