from django.shortcuts import render
from django.views.generic.base import View
from search.models import ArticleType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import json

# Create your views here.

client = Elasticsearch({"127.0.0.1"})

class SearchSuggest(View):
    #搜索建议自动补全
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_dates = []
        if key_words:
            s = ArticleType.search()
            s = s.suggest("my_suggest", key_words, completion={
                "field":"suggest", "fuzzy":{
                    "fuzziness":2
                },
                "size":10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_dates.append(source['title'])
        return HttpResponse(json.dumps(re_dates), content_type='application/json')

class SearchList(View):
    #搜索列表
    def get(self, request):
        key_words = request.GET.get('q', '')
        page = request.GET.get('p', '1')
        try:
            page = int(page)
        except:
            page = 1
        start_time = datetime.now()      #查询开始时间
        response = client.search(
            index= "jobbole",
            body={
                "query":{
                    "multi_match":{
                        "query":key_words,
                        "fields":["Tags", "title", "content"]
                    }
                },
                "from":(page - 1) * 10,
                "size":10,
                "highlight":{
                    "pre_tags": ['<span class="keyword">'],
                    "post_tags": ['</span>'],
                    "fields":{
                        "title":{},
                        "content":{}
                    }
                }
            }
        )
        end_time = datetime.now()    #查询结束时间
        last_time = (end_time - start_time).total_seconds()    #计算查询时间
        total_nums = response['hits']['total']    #查询到的结果总数
        if (page % 10 > 0):
            page_nums = int(total_nums / 10) + 1
        else:
            page_nums = int(total_nums / 10)
        hit_list = []
        for hit in response['hits']['hits']:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict['title'] = "".join(hit["highlight"]["title"])
            else:
                hit_dict['title'] = hit["_source"]["title"]
            if "content" in hit["highlight"]:
                hit_dict['content'] = "".join(hit["highlight"]["content"])[:500]
            else:
                hit_dict['content'] = hit["_source"]["content"][:500]

            hit_dict['date'] = hit["_source"]["date"]
            hit_dict['url'] = hit["_source"]["url"]
            hit_dict['score'] = hit["_score"]
            hit_list.append(hit_dict)

        return render(request, "result.html", {"page":page, "page_nums":page_nums,
                                               "total_nums":total_nums, "all_hits":hit_list,
                                               "key_words":key_words, "last_time":last_time})

