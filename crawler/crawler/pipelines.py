# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from bson.objectid import ObjectId

from collections import OrderedDict
from xmljson import Yahoo

from xml.etree.ElementTree import fromstring

def get_stamp(data):
    bill = data['billStatus']['bill']
    return "{type}-{number}-{date}".format(
        type=bill['billType'],
        number=bill['billNumber'],
        date=bill['createDate']
    )

class MongoDBPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler=crawler)

    def __init__(self, crawler):
        self.to_json = Yahoo(dict_type=dict)

        self.logger = crawler.logger
        self.stats = crawler.stats

        self.stats.set_value('processed', 0)
        self.stats.set_value('duplicate', 0)

        settings = crawler.settings

        path = settings.get('mongodb_path', 'localhost')
        port = int(settings.get('mongodb_port', '27017'))
        database = settings.get('mongodb_database', 'crawler')
        collection = settings.get('mongodb_collection', 'libraryofcongress')

        self.client = MongoClient(path, port)
        self.db = self.client.get_database(database)
        self.collection = self.db.get_collection(collection)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        data = self.to_json.data(fromstring(item['xml']))

        data['stamp'] = get_stamp(data)
        del(data['billStatus']['dublinCore'])

        existing = self.collection.find_one({ 'stamp': data['stamp'] })

        if existing:
            self.logger.info(data['stamp'])
            self.stats.inc_value('duplicate')
            return None

        self.collection.insert_one(data)
        self.stats.inc_value('processed')
        return data


class CayleyPipeline(object):

    pass
