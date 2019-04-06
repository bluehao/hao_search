# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import pymysql
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi
import pymysql.cursors


class ScPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWithEncodingpipeline(object):
    #自定义json文件的导出
    def __init__(self):
        self.file = codecs.open("article.json", "w", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()

class JsonExporter(object):
    #调用scrapy提供的jsonExporter导出json文件
    def __init__(self):
        self.file = open("articleExporter.json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def clos_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class MysqlPipeline(object):
    # 将爬取的数据保存到MySQL中
    def __init__(self):
        self.conn = pymysql.connect('localhost', 'root', '13259733459', 'articleInfo')
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
                            insert into jobbole(title, url, url_object_id, font_image_url, prais_nums, fav_nums, arg_nums, content, Tags, date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
        self.cursor.execute(insert_sql, (
        item["title"], item["url"], item["url_object_id"], item['font_image_url'], item['prais_nums'], item['fav_nums'],
        item['arg_nums'], item['content'], item['Tags'], item['date']))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    # 实现异步插入数据到MySQL
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):

        dbparms = dict(
            host = settings['MYSQL_HOST'],
            user = settings['MYSQL_USER'],
            password = settings['MYSQL_PASSWD'],
            db = settings['MYSQL_DB']
        )

        dbpool = adbapi.ConnectionPool('pymysql', **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)   #处理异常

    def handle_error(self, failure):
        #处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """
                    insert into jobbole(title, url, url_object_id, font_image_url, prais_nums, fav_nums, arg_nums, Tags, date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        cursor.execute(insert_sql, (item["title"], item["url"], item["url_object_id"], item['font_image_url'], item['prais_nums'], item['fav_nums'], item['arg_nums'], item['Tags'], item['date']))

class ElasticsearchPipeline(object):
    #将爬取的数据保存到elasticsearch中
    def process_item(self, item, spider):
        #将item转换为es的数据
        item.saveToEs()
        return item


