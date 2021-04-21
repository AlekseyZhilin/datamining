import requests
import bs4
from urllib.parse import urljoin
import pymongo
import time
import datetime as dt


class MagnitParse:
    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client["magnit_home"]
        self.collection = self.db["products_home"]

    def _get_response(self, url):
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            time.sleep(1)

    def _get_soup(self, url):
        response = self._get_response(url)
        return bs4.BeautifulSoup(response.text, "lxml")

    def run(self):
        for product in self._parse(self.start_url):
            self._save(product)

    @property
    def template(self):
        return {
            "product_name": lambda tag: tag.find("div", attrs={"class": "card-sale__title"}).text,
            "url": lambda tag: urljoin(self.start_url, tag.attrs.get("href", "")),
            "promo_name": lambda tag: tag.find("div", attrs={"class": "card-sale__name"}).text,
            "old_price": lambda tag: self._str_to_flost(".".join(
                item for item in tag.find("div", attrs={"class": "label__price_old"}).text.split())),
            "new_price": lambda tag: self._str_to_flost(".".join(
                item for item in tag.find("div", attrs={"class": "label__price_new"}).text.split())),
            "image_url": lambda tag: urljoin(self.start_url, tag.find("img").attrs.get("data-src", "")),
            "date_from": lambda tag: self._str_to_date(tag.find("div", attrs={"class": "card-sale__date"}).text, 0),
            "date_to": lambda tag: self._str_to_date(tag.find("div", attrs={"class": "card-sale__date"}).text, 1)
        }

    def _parse(self, url):
        soup = self._get_soup(url)
        catalog_main = soup.find('div', attrs={"class": "сatalogue__main"})
        poduct_tags = catalog_main.find_all('a', recursive=False)
        for poduct_tag in poduct_tags:
            product = {}
            for key, funk in self.template.items():
                try:
                    product[key] = funk(poduct_tag)
                except(AttributeError, ValueError):
                    pass

            yield product

    def _save(self, data: dict):
        self.collection.insert_one(data)

    def _str_to_date(self, date: str, pos: int) -> dt.date:
        month = {'января': 1,
                 'февраля': 2,
                 'марта': 3,
                 'апреля': 4,
                 'мая': 5,
                 'июня': 6,
                 'июля': 7,
                 'августа': 8,
                 'сентября': 9,
                 'октября': 10,
                 'ноября': 11,
                 'декабря': 12}

        date = date.replace('\n', '')
        date = date.replace('с ', '')
        date_array = date.split(sep='до ')

        if date_array.__len__() < 2:
            pos = 0
        str_date = date_array[pos].split()
        return dt.datetime(dt.datetime.now().year, day=int(str_date[0]), month=month[str_date[1]])

    def _str_to_flost(self, str: str) -> float:
        try:
            return float(str)
        except(AttributeError, ValueError):
            return 0.0


if __name__ == "__main__":
    url = "https://magnit.ru/promo/?geo=moskva"
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()
