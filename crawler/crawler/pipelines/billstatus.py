from xml.etree.ElementTree import fromstring

from util import check_pipeline, MongoDBPipeline


def get_stamp(data):
    bill = data['billStatus']['bill']
    return "{date}-{type}-{number}".format(
        date=bill['createDate'],
        type=bill['billType'],
        number=bill['billNumber'],
    )


class BillStatus(MongoDBPipeline):

    def initialize(self):
        collection = self.settings.get('mongodb_collection', 'billstatus')

        self.collection = self.db.get_collection(collection)
        self.duplicates = self.db.get_collection(collection + '_duplicates')

    @check_pipeline
    def process_item(self, item, spider):
        data = self.to_json.data(fromstring(item['xml']))

        data['url'] = item['url']
        data['stamp'] = get_stamp(data)
        del(data['billStatus']['dublinCore'])

        existing = self.collection.find_one({ 'stamp': data['stamp'] })

        if existing:
            if self.settings['mongodb_ignore_duplicate']:
                return None
            self.duplicates.insert_one(data)
            self.stats.inc_value('duplicate')
            return None

        self.collection.insert_one(data)
        self.stats.inc_value('processed')
        return data
