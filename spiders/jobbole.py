# -*- coding: utf-8 -*-
import datetime

import scrapy
import re
from scrapy.http import Request
from urllib import parse
from sc.items import ScItem
from sc.utils.comeon import get_md5

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表页中的文章url并交给scrapy进行解析。
        2.获取下一页的url并交给scrapy进行下载，下载完成后交给parse解析。
        :param response:
        :return:exex
        """
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            image_url = post_node.css('img::attr(src)').extract_first()
            post_url = post_node.css('::attr(href)').extract_first()
            #yield Request(url=post_url, callback=self.parse_detail)
            yield Request(url=parse.urljoin(response.url, post_url), meta={'font_image':image_url}, callback=self.parse_detail)

        #提取下一页
        nextPage = response.css('.next.page-numbers::attr(href)').extract_first()
        if nextPage:
            yield Request(url=nextPage, callback=self.parse)
    def parse_detail(self, response):
        sc_item = ScItem()
        #提取文章的具体字段
        font_image_url = response.meta.get('font_image')
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract_first().strip().replace("·","").strip()
        prais_nums = int(response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract_first())
        fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract_first()
        i_match = re.match('.*?(\d+).*', fav_nums)
        if i_match:
            fav_nums = int(i_match.group(1))
        else:
            fav_nums = 0
        arg_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first()
        a_match = re.match('.*?(\d+).*', arg_nums)
        if a_match:
            arg_nums = int(a_match.group(1))
        else:
            arg_nums = 0
        content = response.xpath('//div[@class="entry"]').extract_first()
        Tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        Tag_list = [element for element in Tag_list if not element.strip().endswith('评论')]
        Tags = ','.join(Tag_list)

        sc_item['title'] = title
        sc_item['url'] = response.url
        sc_item['url_object_id'] = get_md5(response.url)
        try:
            date = datetime.datetime.strptime(date, "%Y/%m/%d").date()
        except Exception as e:
            date = datetime.datetime.now().date()
        sc_item['date'] = date
        sc_item['font_image_url'] = [font_image_url]
        sc_item['prais_nums'] = prais_nums
        sc_item['fav_nums'] = fav_nums
        sc_item['arg_nums'] = arg_nums
        sc_item['content'] = content
        sc_item['Tags'] = Tags
        yield sc_item
