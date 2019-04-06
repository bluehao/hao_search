# -*- coding: utf-8 -*-
import scrapy


class PininSpider(scrapy.Spider):
    name = 'pinin'
    allowed_domains = ['hanyu.baidu.com/s?wd=一']
    start_urls = ['http://hanyu.baidu.com/s?wd=一/']

    def parse(self, response):
        pass
