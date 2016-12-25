from xmljson import Yahoo
from pymongo import MongoClient

from xml.etree.ElementTree import fromstring

from util import check_pipeline

class BillStatus(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler=crawler)

    def __init__(self, crawler):
        self.to_json = Yahoo(dict_type=dict)

        self.stats = crawler.stats

        self.stats.set_value('processed', 0)
        self.stats.set_value('duplicate', 0)

        settings = crawler.settings

        path = settings.get('mongodb_path', 'localhost')
        port = int(settings.get('mongodb_port', '27017'))
        database = settings.get('mongodb_database', 'libraryofcongress')
        collection = settings.get('mongodb_collection', 'billstatus')

        self.client = MongoClient(path, port)
        self.db = self.client.get_database(database)
        self.collection = self.db.get_collection(collection)
        self.duplicates = self.db.get_collection(collection + '_duplicates')

    def close_spider(self, spider):
        self.client.close()

    @check_pipeline
    def process_item(self, item, spider):
        data = self.to_json.data(fromstring(item['xml']))

        del(data['billStatus']['dublinCore'])
        data['stamp'] = get_stamp(data)

        existing = self.collection.find_one({ 'stamp': data['stamp'] })

        if existing:
            self.duplicates.insert_one(data)
            self.stats.inc_value('duplicate')
            return None

        self.collection.insert_one(data)
        self.stats.inc_value('processed')
        return data
