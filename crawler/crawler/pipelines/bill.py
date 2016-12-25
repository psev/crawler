from util import check_pipeline

class Bill(object):

    @check_pipeline
    def process_item(self, item, spider):
        pass
