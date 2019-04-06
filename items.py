# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from w3lib.html import remove_tags
from sc.modles.es_types import ArticleType
from elasticsearch_dsl.connections import connections

es = connections.create_connection(ArticleType._doc_type.using)

def gen_suggest(index, info_tuple):
    #根据字符串生成搜索建议
    use_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            #调用es的接口analyze分析字符串
            words = es.indices.analyze(index=index, analyzer='ik_max_word', params={'filter':['lowercase']}, body=text)
            analyze_words = set(r['token'] for r in words['tokens'] if len(r['token'])>1)
            new_words = analyze_words - use_words
        else:
            new_words = set()
        if new_words:
            suggests.append({'input': list(new_words), 'weight': weight})
    return suggests

class ScItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    font_image_url = scrapy.Field()
    prais_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    arg_nums = scrapy.Field()
    content = scrapy.Field()
    Tags = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()

    def saveToEs(self):
        article = ArticleType()
        article.title = self['title']
        article.date = self['date']
        article.url = self['url']
        # article.url_object_id = item['url_object_id']
        article.font_image_url = self['font_image_url']
        article.arg_nums = self['arg_nums']
        article.fav_nums = self['fav_nums']
        article.prais_nums = self['prais_nums']
        article.content = remove_tags(self['content'])
        article.Tags = self['Tags']
        article.meta.id = self['url_object_id']

        article.suggest = gen_suggest(ArticleType._doc_type.index, ((article.title, 10), (article.Tags, 7)))

        article.save()