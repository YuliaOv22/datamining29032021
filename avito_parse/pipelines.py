# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
import re
import base64
import requests
import pymongo


class AvitoParsePipeline:
    def process_item(self, item, spider):
        return item


class AvitoParseMongoPipeline:
    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client["avito_parse"]

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item


class AvitoPhoneImageDownloadPipeline:
    def process_item(self, item, spider):
        re_pattern_data = re.compile(r'data:image/png;base64,([a-zA-Z|\d].+)"}')
        re_pattern_id_product = re.compile(r'phone/([a-zA-Z|\d]+)')
        if "phone_url" in item:
            data = requests.get(item["phone_url"]).content
            data_decoded = base64.decodebytes(re.findall(re_pattern_data, str(data))[0].encode('utf-8'))
            with open(f'imagePhone_{re.findall(re_pattern_id_product, item["phone_url"])[0]}.png', "wb") as fh:
                fh.write(data_decoded)
        return item
