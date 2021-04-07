import requests
from urllib.parse import urljoin
import bs4
import pymongo
import datetime as dt

months = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}


class MagnitParse:
    def __init__(self, start_url, db_client):
        self.start_url = start_url
        db = db_client["gb_data_mining_29_03_2021"]
        self.collection = db["magnit_sales"]

    def _get_response(self, url, *args, **kwargs):
        try:
            return requests.get(url, *args, **kwargs)
        except requests.ConnectionError:
            print("Ошибка подключения.")
        except requests.Timeout:
            print("Время ожидания запроса истекло.")
        except requests.RequestException:
            print("Упс! Не удалось подключиться.")

    def _get_soup(self, url, *args, **kwargs):
        try:
            return bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        except AttributeError:
            print("Парсинг остановлен.")
            quit()

    def run(self):
        for product in self._parse(self.start_url):
            self._save(product)

    @property
    def _template(self):
        return {
            "url": lambda tag: urljoin(self.start_url, tag.attrs.get("href", "")),
            "promo_name": lambda tag: tag.find("div", attrs={"class": "card-sale__name"}).text,
            "product_name": lambda tag: tag.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda tag: float(
                ".".join(tag.find("div", attrs={"class": "label__price_old"}).text.split())),
            "new_price": lambda tag: float(
                ".".join(tag.find("div", attrs={"class": "label__price_new"}).text.split())),
            "image_url": lambda tag: urljoin(self.start_url, tag.picture.img.attrs.get("data-src", "")),
            "date_from": lambda tag: self._get_date(tag.find("div", attrs={"class": "card-sale__date"}).text)[0],
            "date_to": lambda tag: self._get_date(tag.find("div", attrs={"class": "card-sale__date"}).text)[1]
        }

    def _get_date(self, parsed_date):
        dates_list = parsed_date.replace("с ", "").replace("\n", "").split("до")
        date_new_format = []
        for date in dates_list:
            dates_list_new = date.split()
            date_new_format.append(
                dt.datetime(
                    year=dt.datetime.now().year,
                    month=months.get(dates_list_new[1][:3].lower()),
                    day=int(dates_list_new[0])
                )
            )

        # Переопределяем год, если акция на стыке годов
        if (date_new_format[1].month - date_new_format[0].month) < 0:
            date_new_format[0] = dt.datetime(
                year=dt.datetime.now().year - 1,
                month=date_new_format[0].month,
                day=date_new_format[0].day)

        return date_new_format

    def _parse(self, url):
        soup = self._get_soup(url)
        catalog_main = soup.find("div", attrs={"class": "сatalogue__main"})
        try:
            product_tags = catalog_main.find_all("a", recursive=False)
            for product_tag in product_tags:
                product = {}
                for key, funk in self._template.items():
                    try:
                        product[key] = funk(product_tag)
                    except (AttributeError, ValueError):
                        pass
                yield product
        except AttributeError:
            print("Проверьте корректность введенного URL.")
            quit()

    def _save(self, data):
        self.collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()
