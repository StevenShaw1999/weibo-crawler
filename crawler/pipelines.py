# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import pymysql
from twisted.enterprise import adbapi
from pymysql import cursors
from rich import print

from itemadapter import ItemAdapter
from pymysql import cursors


from weibo.items import PeopleItem, StatusesItem, CommentItem
from scrapy.utils.project import get_project_settings

from scrapy.exporters import JsonLinesItemExporter
class WeiboPipeline(object):
    def __init__(self):
        settings = get_project_settings()
        lower = settings.get('LOWER')
        upper = settings.get('UPPER')
        print(lower)
        self.comments_fp = open("bowen_json/comments-test.json", "wb")
        self.people_fp = open(f'bowen_json/people-test.json', 'wb')
        self.statuses_fp = open(f'bowen_json/statuses-test.json', 'wb')
        self.comments_exporter = JsonLinesItemExporter(self.comments_fp,
                                              ensure_ascii=False)
        self.people_exporter = JsonLinesItemExporter(self.people_fp,
                                              ensure_ascii=False)
        self.statuses_exporter = JsonLinesItemExporter(self.statuses_fp,
                                              ensure_ascii=False)

    def process_item(self, item, spider):
        if isinstance(item, CommentItem):
            self.comments_exporter.export_item(item)
        elif isinstance(item, PeopleItem):
            self.people_exporter.export_item(item)
        else:
            self.statuses_exporter.export_item(item)

        return item

    def close_item(self, spider):
        print("存储成功！")
        self.comments_fp.close()
        self.people_fp.close()
        self.statuses_fp.close()


class WeiboTwistedPipeline(object):
    
    def __init__(self):
        settings = get_project_settings()
        dbparams = {
            'host'       : settings.get('MYSQL_HOST'),
            'port'       : settings.get('MYSQL_PORT'),
            'user'       : settings.get('MYSQL_USER'),
            'password'   : settings.get('MYSQL_PASSWORD'),
            'database'   : settings.get('MYSQL_DBNAME'),
            'charset'    : 'utf8mb4',
            'cursorclass': cursors.DictCursor,
        }
        self.dbpool = adbapi.ConnectionPool('pymysql',**dbparams)



    def process_item(self, item, spider):
        defer = self.dbpool.runInteraction(self.insert_item, item) 
        defer.addErrback(self.handle_error, item, spider) 
        return item
        
    
    def insert_item(self, cursor, item):

        table_name = item['type']
        fields = list(item.fields.keys())
        field_sql = ",".join(fields)
        value_sql = ",".join(["%s"] * len(fields))
        sql = f"insert into {table_name}({field_sql}) VALUES({value_sql})"
        values = list(item[field] for field in fields)
        cursor.execute(sql, values)

    
    
    def handle_error(self, error, item, spider):
        print('='*20+'error'+'='*20)
        print(error)
        print('='*20+'error'+'='*20)