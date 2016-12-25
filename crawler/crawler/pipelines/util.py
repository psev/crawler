import functools

def get_stamp(data):
    bill = data['billStatus']['bill']
    return "{date}-{type}-{number}".format(
        date=bill['createDate'],
        type=bill['billType'],
        number=bill['billNumber'],
    )

def check_pipeline(process_item_method):

    @functools.wraps(process_item_method)
    def wrapper(self, item, spider):

        # message template for debugging
        msg = '%%s %s pipeline step' % (self.__class__.__name__,)

        # if class is in the spider's pipeline, then use the
        # process_item method normally.
        if self.__class__ in spider.pipeline:
            spider.log(msg % 'executing', level=log.DEBUG)
            return process_item_method(self, item, spider)

        # otherwise, just return the untouched item (skip this step in
        # the pipeline)
        else:
            spider.log(msg % 'skipping', level=log.DEBUG)
            return item

    return wrapper
