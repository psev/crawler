import re

from xml.etree.ElementTree import fromstring

from util import check_pipeline, MongoDBPipeline

from pprint import pprint


def _get_stamp(data):
    bill = data['resolution']['form']['legis-num']
    if not isinstance(bill_number, str):
        bill = data['resolution']['form']['legis-num']['content']

    congress = data['resolution']['form']['congress']
    if not isinstance(congress, str):
        congress = data['resolution']['form']['congress']['content']

    return '%s%s' % (congress, bill)

def get_stamp(meta):
    return '{congress}/{session}/{type}/{number}/{format}'.format(**meta)


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

        data['meta'] = item['meta']
        data['stamp'] = get_stamp(item['meta'])

        existing = self.collection.find_one({ 'stamp': data['stamp'] })

        if existing:
            self.duplicates.insert_one(data)
            self.stats.inc_value('duplicate')
            return None

        self.collection.insert_one(data)
        self.stats.inc_value('processed')
        return data
