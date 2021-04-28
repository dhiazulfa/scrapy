import pymongo

import sys,json,os,ssl
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch,RequestsHttpConnection
from scrapy.exceptions import DropItem

class SanitizePipline(object):
    """docstring for SanitizePipline."""

# class yang akan melakukan filter duplicate item serta insert data ke mongoDB
class NewsMongoPipeline:
    # nama collection untuk mongoDB
    collection_name = 'latest_news_2'

    def __init__(self,mongo_server,mongo_port,mongo_db):
        self.ids_seen = []
        self.mongo_server = mongo_server
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        # mengembalikan nilai ke fungsi init
        return cls(
            mongo_server = crawler.settings.get('MONGODB_SERVER'),
            mongo_port = crawler.settings.get('MONGODB_PORT'),
            mongo_db = crawler.settings.get('MONGODB_DB')
        )

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_server,self.mongo_port)
        self.db = self.client[self.mongo_db]
        for x in self.db[self.collection_name].find():
            self.ids_seen.append(x['title'])

    def close_spider(self, spider):
        self.client.close()
    # proses insert data ke mongoDB
    def process_item(self, item, spider):
        # adapter = ItemAdapter(item)
        # print('mencoba',self.ids_seen)
        # if adapter['title'] in self.ids_seen:
        #     print('Duplicatecog')
        #     raise DropItem(f"Duplicate item found: {item!r}")
        # else:
        self.db[self.collection_name].insert_one(dict(item))
        return item


class NewsElasticPipeline(object):
    """docstring for NewsElasticPipeline."""

    def __init__(self,elastic_server,elastic_port,elastic_index,elastic_type):
        self.ids_seen = set()
        self.elastic_server = elastic_server
        self.elastic_port = elastic_port
        self.elastic_index = elastic_index
        self.elastic_type = elastic_type

    @classmethod
    def from_crawler(cls, crawler):
        # mengembalikan nilai ke fungsi init
        return cls(
            elastic_server = crawler.settings.get('ES_HOST'),
            elastic_port = crawler.settings.get('ES_PORT'),
            elastic_index = crawler.settings.get('ES_INDEX'),
            elastic_type = crawler.settings.get('ES_TYPE')
        )

    def open_spider(self,spider):
        self.elastic = Elasticsearch(hosts=[self.elastic_server+':'+self.elastic_port],use_ssl=False,connection_class=RequestsHttpConnection)
        if not self.elastic.ping():
            raise ValueError('Cnnection failed')
        else:
            print('Connection redy')

    def outputJSON(self,obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def process_item(self,item,spider):
        documents = json.dumps(item, default=self.outputJSON)
        return self.elastic.index(index=self.elastic_index,doc_type=self.elastic_type, body=documents)
