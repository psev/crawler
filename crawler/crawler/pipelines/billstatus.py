from xml.etree.ElementTree import fromstring

from util import check_pipeline, MongoDBPipeline


class BillStatus(MongoDBPipeline):

    def initialize(self):
        collection = self.settings.get('mongodb_collection', 'billstatus')

        self.collection = self.db.get_collection(collection)
        self.duplicates = self.db.get_collection(collection + '_duplicates')

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
