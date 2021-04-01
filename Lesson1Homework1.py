from pathlib import Path
import time
import json
import requests


class Parse5ka:
    headers = {
        "User-Agent": "JuliJu"
    }

    def __init__(self, start_url: str, categories_url: str, save_path: Path):
        self.start_url = start_url
        self.categories_url = categories_url
        self.save_path = save_path

    def _get_response(self, url, *args, **kwargs) -> requests.Response:
        while True:
            response = requests.get(url, *args, **kwargs, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(1)

    def run(self):
        for category in self._parse_categories(self.categories_url):
            category_path = self.save_path.joinpath(f"{category['parent_group_name']}.json")
            products = []
            for item in self._parse_products(self.start_url, category['parent_group_code']):
                products.append(item)
            category["products"] = products
            self._save(category, category_path)

    def _parse_categories(self, url):
        while url:
            response = self._get_response(url)
            data: dict = response.json()
            for product in range(0, len(data)):
                yield data[product]

    def _parse_products(self, url, params):

        params = {
            "categories": params
        }

        while url:
            response = self._get_response(url, params=params)
            data: dict = response.json()
            url = data.get("next")
            for item in data.get("results", []):
                yield item

    def _save(self, data, file_path):
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="UTF-8")


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == "__main__":
    parser = Parse5ka("https://5ka.ru/api/v2/special_offers/", "https://5ka.ru/api/v2/categories/", get_save_path("categories"))
    parser.run()
