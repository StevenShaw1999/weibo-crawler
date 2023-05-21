from itertools import filterfalse
import json
import redis
import scrapy
import logging
from lxml import etree
from tqdm import tqdm
from urllib.parse import quote
from ..items import WeiboTopicItem


def wrap(dic, keyList, default = ""):
    try:
        for key in keyList:
            dic = dic[key]
        return dic
    except:
        return default
    
    
class WeiboTopicSpider(scrapy.Spider):
    
    name = "WeiboTopic"
    
    def __init__(self, settings, *args, **kwargs):
            
        super().__init__()
        self.settings = settings
        self.allowed_domains = ["weibo.cn", "weibo.com"]
        self.db = 1
        self.red = redis.Redis(host = settings.get('REDIS_HOST'), 
                               port = settings.get('REDIS_PORT'), 
                               password = settings.get('REDIS_PASSWORD'),
                               db = self.db) 
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider
    

    def start_requests(self):
        # movie_ids = ["100120004665"]
        movie_ids = list(self.red.smembers('weibo_movie_id'))
        movie_ids.sort()
        pbar = tqdm(movie_ids)
        for i, movie_id in enumerate(movie_ids):
            movie_id = str(movie_id, 'utf-8') if type(movie_id) != str else movie_id
            pbar.set_description("Crawling:")
            yield scrapy.Request(url = f"https://m.weibo.cn/api/container/getIndex?containerid={movie_id}",
                                 callback = self.get_name,
                                 priority = 10,
                                 meta = {
                                     'movie_id': movie_id,
                                     
                                     'index_value': movie_id,
                                     'duplicate_removal': True,
                                     'store_db': self.db,
                                     'store_key': 'seen_weibo_movie_id_for_topic',
                                 })
    
    def get_name(self, response):
        movie_id = response.meta['movie_id']

        data = json.loads(response.body)
        try:
            if data['ok'] == 0:
                return
        except:
            logging.error(response, response.body)
            
        movie_title = wrap(data, ["data", "pageInfo", "nick"])
        containerid = quote(f"100103type=38&q={movie_title}&t=0", 'utf-8')
        url = f"https://m.weibo.cn/api/container/getIndex?containerid={containerid}&page_type=searchall&page=1"
        yield scrapy.Request(url = url,
                     callback = self.search_topics,
                     priority = 10,
                     meta = {
                         'movie_id': movie_id,
                         'movie_title': movie_title,
                         'page_id': 1,
                         
                         'duplicate_removal': False,
                     })
        

    def search_topics(self, response):
        movie_id = response.meta['movie_id']
        movie_title = response.meta['movie_title']
        page_id = response.meta['page_id']
        # print(movie_id, movie_title, page_id)
        data = json.loads(response.body)
        try:
            if data['ok'] == 0:
                return
        except:
            logging.error(response, response.body)
        # import ipdb; ipdb.set_trace()
        cards = wrap(data, ["data", "cards"])
        for sub in cards:
            for sub_card in wrap(sub, ["card_group"]):
                # print(wrap(sub_card, "card_type"))
                if wrap(sub_card, ["card_type"]) == 8:
                    # print(wrap(sub_card, ["title_sub"]))
                    topicItem = WeiboTopicItem()
                    topicItem['type'] = "weibotopicitem"
                    topicItem['weibo_movie_id'] = movie_id
                    topicItem['weibo_movie_name'] = movie_title
                    topicItem['title_sub'] = wrap(sub_card, ["title_sub"])
                    topicItem['desc1'] = wrap(sub_card, ["desc1"])
                    topicItem['desc2'] = wrap(sub_card, ["desc2"])
                    topicItem['pic'] = wrap(sub_card, ["pic"])
                    topicItem['item_id'] = wrap(sub_card, ["item_id"])
                    topicItem['analysis_extra'] = wrap(sub_card, ["analysis_extra"])
                    yield topicItem
                    

        page_id += 1
        containerid = quote(f"100103type=38&q={movie_title}&t=0", 'utf-8')
        url = f"https://m.weibo.cn/api/container/getIndex?containerid={containerid}&page_type=searchall&page={page_id}"
        yield scrapy.Request(url = url,
                     callback = self.search_topics,
                     priority = 5,
                     meta = {
                         'movie_id': movie_id,
                         'movie_title': movie_title,
                         'page_id': page_id,
                         
                         'duplicate_removal': False,
                     })