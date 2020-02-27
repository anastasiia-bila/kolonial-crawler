from kolonial_crawler import KolonialCrawler
from db import DB
import time


if __name__ == '__main__':
    start = time.time()
    config_file = 'config.json'
    crawler = KolonialCrawler(config_file)
    products = crawler.recover()
    if not products:
        products = crawler.run()

    db_name = 'kolonial.db'
    table_schema = '''CREATE TABLE IF NOT EXISTS products
        (NAME   TEXT                NOT NULL,
         LINK   TEXT                NOT NULL,
         PRICE  REAL                NOT NULL,
         COLLECT_DAYS TEXT,
         CONSTRAINT product_row UNIQUE (NAME, LINK, PRICE, COLLECT_DAYS)
         );'''
    db = DB(db_name, table_schema)
    operation = 'INSERT OR REPLACE INTO products (NAME, LINK, PRICE, COLLECT_DAYS) \
          VALUES (?, ?, ?, ?)'

    db.execute(operation, products)
    print(time.time() - start)
