# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymongo
'''
#这个管道是将结果直接写入到MongoDB中
class TaobaoPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        db = self.client['taobao']
        self.movies = db['infos']

    def process_item(self, item, spider):
        data = dict(item)
        self.movies.insert(data)
        return item
    
'''
#这个是测试，先将文件写入到json文件中

class TaobaoPipeline2(object):
    def __init__(self):
        self.writer = open('information.json','w')
    def process_item(self, item, spider):
        text =json.dumps(dict(item),ensure_ascii = False) + '\n'
        self.writer.write(text.encode('utf-8'))
        return item
    def close_spider(self,spider):
        self.writer.close()

