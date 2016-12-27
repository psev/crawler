import scrapy
import re

from urlparse import urljoin

from crawler.items import XMLItem
from crawler import pipelines

from scrapy.shell import inspect_response


BASE = 'https://www.gpo.gov/fdsys/'
SECTION = 'bulkdata/BILLS'

class Bill(scrapy.Spider):

    name = 'bill'
    allewed_domains = ['gpo.gov']

    start_urls = (
        urljoin(BASE, SECTION),
    )

    pipeline = (
        pipelines.Bill,
    )

    def __init__(self, *args, **kargs):
        super(Bill, self).__init__(*args, **kargs)
        self.re = re.compile('.*(?P<session>\d+)/[a-z]+/BILLS\-(?P<congress>\d+)(?P<type>[a-z]+)(?P<number>\d+)(?P<format>[a-z]+).xml$')

    def extract(self, response):
        return response.xpath('//a[contains(@href, "%s")]/@href' % SECTION).extract()

    def select(self, urls, pattern):
        return filter(lambda u: re.match(pattern, u), urls)

    def drop(self, urls, pattern):
        return filter(lambda u: not re.match(pattern, u), urls)

    # parse the index
    def parse(self, response):
        # skip 'bulkdata/BILLS/resources' url
        urls = self.drop(self.extract(response), '.*resources$')

        for url in urls:
            yield scrapy.Request(urljoin(BASE, url), callback=self.session)

    def session(self, response):
        # skip 'bulkdata/BILLS' url
        urls = self.drop(self.extract(response), '.*BILLS$')

        for url in urls:
            yield scrapy.Request(urljoin(BASE, url), callback=self.type)

    def type(self, response):
        urls = self.select(self.extract(response), '.*[a-zA-Z]+$')

        for url in urls:
            yield scrapy.Request(urljoin(BASE, url), callback=self.number)

    def number(self, response):
        urls = self.select(self.extract(response), '.*\.xml$')

        for url in urls:
            yield scrapy.Request(urljoin(BASE, url), callback=self.bill)

    def bill(self, response):
        match = self.re.match(response.url)
        yield XMLItem(xml=response.body, meta=match.groupdict(), url=response.url)
