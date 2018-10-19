from django.db import models
from datetime import datetime
from elasticsearch_dsl import Date, Nested, Boolean, \
    analyzer, Completion, Keyword, Text, Integer, DocType
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import CustomAnalyzer as ca


# Create your models here.
connections.create_connection(hosts=["localhost"])

class CustomAnalyzer(ca):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word", filter=['lowercase'])

class ArticleType(DocType):
    suggest = Completion(analyzer=ik_analyzer)    #自动补全设置
    title = Text(analyzer='ik_max_word')
    date = Date()
    font_image_url = Keyword()
    prais_nums = Integer()
    fav_nums = Integer()
    arg_nums = Integer()
    content = Text(analyzer='ik_max_word')
    Tags = Text(analyzer='ik_max_word')
    url = Keyword()
    url_object_id = Keyword()

    class Meta:
        index = "jobbole"
        doc_type = "article"

if __name__ == "__main__":
    ArticleType.init()