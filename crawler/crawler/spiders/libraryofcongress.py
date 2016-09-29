# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response


class LibraryOfCongressSpider(scrapy.Spider):
    name = "libraryofcongress"
    allowed_domains = ["gpo.gov"]
    start_urls = (
        'https://www.gpo.gov/fdsys/bulkdata/BILLSTATUS',
    )

    def parse(self, response):
        urls = response.xpath('//a[contains(@href, "bulkdata/BILLSTATUS")]/@href').extract()

        # skip the 'bulkdata/BILLSTATUS/resources' url
        urls = [ u for u in urls if not u.endswith('resources') ]

        for url in urls:
            yield scrapy.Request(url, callback=self.billstatus)

    def billstatus(self, response):
        inspect_response(response, self)
