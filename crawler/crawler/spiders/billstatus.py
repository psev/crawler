# -*- coding: utf-8 -*-

from urlparse import urljoin

import scrapy

from crawler.items import XMLItem
from crawler import pipelines


BASE = 'https://www.gpo.gov/fdsys/'
SECTION = 'bulkdata/BILLSTATUS'


class BillStatus(scrapy.Spider):

    name = 'billstatus'
    allowed_domains = ['gpo.gov']

    start_urls = (
        urljoin(BASE, SECTION),
    )

    pipeline = (
        pipelines.BillStatus
    )

    def extract(self, response):
        return response.xpath('//a[contains(@href, "bulkdata/%s")]/@href' % SECTION).extract()

    def select(self, urls, select):
        return [ u for u in urls if u.endswith(select) ]

    def drop(self, urls, drop):
        return [ u for u in urls if not u.endswith(drop) ]

    # parse the index
    def parse(self, response):
        # skip 'bulkdata/BILLSTATUS/resources' url
        urls = self.drop(self.extract(response), 'resources')

        for url in urls:
            yield scrapy.Request(urljoin(BASE, url), callback=self.billstatus)

    # parse the session
    def billstatus(self, response):
        # skip 'bulkdata/BILLSTATUS' url
        urls = self.drop(self.extract(response), 'BILLSTATUS')

        for url in urls:
            yield scrapy.Request(urljoin(BASE, url), callback=self.billtype)

    def billtype(self, response):
        # select only '.xml' files
        urls = self.select(self.extract(response), '.xml')

        for url in urls:
            yield scrapy.Request(urljoin(BASE, url), callback=self.billmeta)

    def billmeta(self, response):
        yield XMLItem(xml=response.body)
