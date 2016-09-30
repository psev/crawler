# -*- coding: utf-8 -*-

from urlparse import urljoin

import scrapy
from scrapy.shell import inspect_response

from crawler.items import LibraryOfCongressItem

BASE = 'https://www.gpo.gov/fdsys/'

class LibraryOfCongressSpider(scrapy.Spider):
    name = "libraryofcongress"
    allowed_domains = ["gpo.gov"]

    start_urls = (
        urljoin(BASE, 'bulkdata/BILLSTATUS'),
    )

    def extract(self, response):
        return response.xpath('//a[contains(@href, "bulkdata/BILLSTATUS")]/@href').extract()

    def select(self, urls, select):
        return [ u for u in urls if u.endswith(select) ]

    def drop(self, urls, drop):
        return [ u for u in urls if not u.endswith(drop) ]

    # parse the index
    def parse(self, response):
        # skip 'bulkdata/BILLSTATUS/resources' url
        urls = self.drop(self.extract(response), 'resources')

        for url in urls:
            #yield scrapy.Request(urljoin(BASE, url), callback=self.billstatus)
            return scrapy.Request(urljoin(BASE, url), callback=self.billstatus)

    # parse the session
    def billstatus(self, response):
        # skip 'bulkdata/BILLSTATUS' url
        urls = self.drop(self.extract(response), 'BILLSTATUS')

        for url in urls:
            #yield scrapy.Request(urljoin(BASE, url), callback=self.billtype)
            return scrapy.Request(urljoin(BASE, url), callback=self.billtype)

    def billtype(self, response):
        # select only '.xml' files
        urls = self.select(self.extract(response), '.xml')

        for url in urls:
            #yield scrapy.Request(urljoin(BASE, url), callback=self.bill)
            return scrapy.Request(urljoin(BASE, url), callback=self.bill)

    def bill(self, response):
        yield LibraryOfCongressItem(xml=response.body)
