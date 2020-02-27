import json
import os
import redis

from selenium import webdriver


class AbstractCrawler(object):

    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as file:
            config = json.load(file)
            self._driver_path = config['driver_path']
            self._base_url = config['base_url']
        self._redis = redis.Redis()

    def _setup_driver(self):
        os.environ['PATH'] += os.pathsep + self._driver_path
        self._driver = webdriver.Firefox()
        self._driver.get(self._base_url)

    def _teardown_driver(self):
        # Clean up once task is completed
        self._driver.close()

    def _find_categories_urls(self):
        pass

    def _find_sub_categories_urls(self, categories_urls):
        pass

    def _find_products_urls(self, sub_categories_urls):
        pass

    def _find_products(self, products_urls, ignore_urls):
        pass

    def run(self):
        products_info = list()
        try:
            self._setup_driver()
            categories_urls = self._find_categories_urls()
            sub_categories_urls = self._find_sub_categories_urls(categories_urls)
            products_urls = self._find_products_urls(sub_categories_urls, set())
            self._redis.sadd('product_urls', *products_urls)
            products_info = self._find_products(products_urls)

            # self._redis.delete('products')
            # self._redis.delete('product_urls')
        except Exception as e:
            print(e)
        finally:
            self._teardown_driver()

        return products_info

    def recover(self):
        # Retrieving a set for product urls
        product_urls = [url.decode('utf-8') for url in self._redis.smembers('product_urls')]
        ignore_urls = {url.decode('utf-8') for url in self._redis.hkeys('products')}
        if product_urls:
            products_info = list()
            try:
                self._setup_driver()
                products_info = self._find_products(product_urls, ignore_urls)
            except Exception as e:
                self._teardown_driver()
                raise e
            finally:
                self._teardown_driver()
            return products_info
        else:
            print('Products are processed. Please, re-run the crawler.')
