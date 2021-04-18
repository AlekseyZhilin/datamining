import time
import json
from pathlib import Path
import requests


class Parse5ka:
    headers = {"User-Agent": "Aleksey"}

    def __init__(self, start_url: str, save_path: Path):
        self.start_url = start_url
        self.save_path = save_path

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(1)

    def run(self):
        for product in self._parse(self.start_url):
            product_path = self.save_path.joinpath(f"{product['id']}.json")
            self._save(product, product_path)

    def _parse(self, url: str):
        while url:
            response = self._get_response(url)
            data: dict = response.json()
            url = data["next"]
            for product in data["results"]:
                yield product

    def _save(self, data: dict, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class Parse5kaCat(Parse5ka):
    def __init__(self, start_url, save_path, cat_url):
        super().__init__(start_url, save_path)
        self.cat_url = cat_url

    def run(self):
        response_cut = requests.get(self.cat_url, headers=self.headers)
        if response_cut.status_code == 200:
            data_cut: dict = response_cut.json()
            for cur_cut in data_cut:
                params = {'categories': cur_cut['parent_group_code']}
                cut_product = self.save_path.joinpath(f"{cur_cut['parent_group_name']}.json")

                array_product = []
                for product in self._parse(self.start_url, params):
                    array_product.append(product)
                self._save(array_product, cut_product)

    def _parse(self, url: str, params: dict):
        while url:
            response = self._get_response(url, params)
            data: dict = response.json()
            url = data["next"]
            for product in data["results"]:
                yield product

    def _get_response(self, url, params):
        while True:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response
            time.sleep(1)


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == "__main__":
    url = "https://5ka.ru/api/v2/special_offers/"
    cat_url = "https://5ka.ru/api/v2/categories/"
    save_path_products = get_save_path("products")
    # parser_products = Parse5ka(url, save_path_products)
    parser_products = Parse5kaCat(url, save_path_products, cat_url)
    parser_products.run()
