import re

from xml.etree.ElementTree import fromstring

from util import check_pipeline, MongoDBPipeline

from pprint import pprint


class Bill(MongoDBPipeline):

    def initialize(self):
        collection = self.settings.get('mongodb_collection', 'bill')

        self.collection = self.db.get_collection(collection)
        self.duplicates = self.db.get_collection(collection + '_duplicates')

    @check_pipeline
    def process_item(self, item, spider):
        data = self.to_json.data(fromstring(item['xml']))

        new_core = { }
        core = data['resolution']['metadata']['dublinCore']

        for k, v in core.iteritems():
            match = re.match('.*\\}(\w+)$', k)
            new_key = match.group(1)
            new_core[new_key] = v

        data['resolution']['metadata']['dublinCore'] = new_core

        #existing = self.collection.find_one({ 'stamp': stamp })

        #if existing:
            #self.duplicates.insert_one(data)
            #self.stats.inc_value('duplicate')
            #return None

        self.collection.insert_one(data)
        self.stats.inc_value('processed')
        return data
