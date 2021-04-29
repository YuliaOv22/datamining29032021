# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
import pymongo


class InstagramParsePipeline:
    def process_item(self, item, spider):
        return item


class InstagramParseMongoPipeline:
    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client["instagram_parse"]

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item
