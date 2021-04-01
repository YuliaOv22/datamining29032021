from pathlib import Path
import json
import requests

headers = {
    "User-Agent": "JuliJu"
}

params = {
    "store": None,
    "records_per_page": 12,
    "page": 1,
    "categories": 870,
    "ordering": None,
    "price_promo__gte": None,
    "price_promo__lte": None,
    "search": None
}

url = "https://5ka.ru/api/v2/categories/"

# url = "https://5ka.ru/api/v2/special_offers/"

response: requests.Response = requests.get(url, headers=headers, params=params)

print(1)

file = Path(__file__).parent.joinpath("cat5ka.json")

file.write_text(response.text, encoding="UTF-8")

# data = json.loads(response.text)

print(1)
