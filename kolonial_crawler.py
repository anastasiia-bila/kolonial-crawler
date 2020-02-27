from abstract_crawler import AbstractCrawler
import time
import json


class KolonialCrawler(AbstractCrawler):

    def _find_categories_urls(self):
        category_sidebar = self._driver.find_element_by_id('navbar-category-sidebar')
        # Extract lists of parent-categories
        categories = category_sidebar.find_elements_by_xpath('.//li[@class="parent-category "]')

        categories_urls = list()
        for category in categories:
            category_url = category.find_element_by_tag_name('a')
            categories_urls.append(category_url.get_attribute('href'))

        return categories_urls

    def _find_sub_categories_urls(self, categories_urls):
        sub_categories_urls = list()
        for i, category_url in enumerate(categories_urls):
            self._driver.get(category_url)
            category_sidebar = self._driver.find_element_by_id('navbar-category-sidebar')
            active_category = category_sidebar.find_elements_by_xpath('.//li[@class="parent-category active"]')
            if active_category:
                sub_categories = active_category[0].find_elements_by_xpath('.//li[@class="child-category "]')
                for sub_category in sub_categories:
                    sub_category_url = sub_category.find_element_by_tag_name('a')
                    sub_categories_urls.append(sub_category_url.get_attribute('href'))

            else:
                sub_categories_urls.append(category_url)

            print('Processed {0} out of {1} categories'.format(i + 1, len(categories_urls)))

        return sub_categories_urls

    def _find_products_urls(self, sub_categories_urls):
        product_urls = set()

        for i, sub_category_url in enumerate(sub_categories_urls):
            self._driver.get(sub_category_url)

            if '?page=' not in sub_category_url:
                pagination = self._driver.find_elements_by_xpath('.//ul[@class="pagination"]//a')
                if pagination:
                    for page in pagination[1:-1]:
                        sub_category_url_additional_page = page.get_attribute('href')
                        sub_categories_urls.append(sub_category_url_additional_page)
            products_on_page = self._driver.find_elements_by_class_name('product-list-item')
            for item in products_on_page:
                product_link = item.find_element_by_tag_name('a')
                if product_link:
                    product_urls.add(product_link.get_attribute('href'))
                else:
                    print('Product does not have url. Check: {}'.format(sub_category_url))

            print('Processed {0} out of {1} subcategories'.format(i + 1, len(sub_categories_urls)))

        return product_urls

    def _find_products(self, product_urls, ignore_urls):
        for i, product_url in enumerate(list(product_urls)):
            print('Processing: {}'.format(product_url))
            if product_url not in ignore_urls:

                self._driver.get(product_url)
                product_details = self._driver.find_element_by_class_name('product-detail')
                product_name = product_details.find_element_by_xpath('.//span[@itemprop="name"]')
                product_price = product_details.find_element_by_xpath('.//div[@itemprop="price"]')
                collect_days_value = product_details.find_element_by_xpath(
                    './/span[text()="Utleveringsdager"]/parent::th/parent::tr//span[@itemprop="value"]')

                product_info = product_name.text, product_url, product_price.get_attribute('content'), collect_days_value.text
                # Add element to Redis in Hash by key url, value object
                self._redis.hset('products', product_url, json.dumps(product_info))
            print('Processed {0} out of {1} products'.format(i + 1, len(product_urls)))

        return [tuple(json.loads(value)) for value in self._redis.hmget('products', *product_urls)]


if __name__ == '__main__':
    start = time.time()
    crawler = KolonialCrawler()
    crawler.run()
    end = time.time()
    print(end - start)
