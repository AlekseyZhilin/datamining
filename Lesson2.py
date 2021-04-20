import requests
import bs4
from pathlib import Path
from urllib.parse import urljoin
import pymongo
import time


class MagnitParse:
    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client["magnit_data_mining"]
        self.collection = self.db["products"]

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
            if len(product) == 2:
                yield product

    def _save(self, data: dict):
        self.collection.insert_one(data)


def get_save_path(dir_name):
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    save_path = get_save_path("magnit_product")
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = MagnitParse(url, db_client)
    parser.run()
    print(1)
