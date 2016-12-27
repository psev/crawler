import functools

from xmljson import Yahoo
from pymongo import MongoClient


def check_pipeline(process_item_method):

    @functools.wraps(process_item_method)
    def wrapper(self, item, spider):

        # message template for debugging
        #msg = '%%s %s pipeline step' % (self.__class__.__name__,)

        # if class is in the spider's pipeline, then use the
        # process_item method normally.
        if self.__class__ in spider.pipeline:
            #spider.log(msg % 'executing', level=log.DEBUG)
            return process_item_method(self, item, spider)

        # otherwise, just return the untouched item (skip this step in
        # the pipeline)
        else:
            #spider.log(msg % 'skipping', level=log.DEBUG)
            return item

    return wrapper


class MongoDBPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler=crawler)

    def __init__(self, crawler):
        self.to_json = Yahoo(dict_type=dict)

        self.stats = crawler.stats

        self.stats.set_value('processed', 0)
        self.stats.set_value('duplicate', 0)

        self.settings = crawler.settings

        path = self.settings.get('mongodb_path', 'localhost')
        port = int(self.settings.get('mongodb_port', '27017'))
        database = self.settings.get('mongodb_database', 'libraryofcongress')

        self.client = MongoClient(path, port)
        self.db = self.client.get_database(database)
        self.initialize()

    def close_spider(self, spider):
        self.client.close()
