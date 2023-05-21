import json
import redis
import scrapy
import logging
from lxml import etree
from tqdm import tqdm
from ..items import WeiboChaohuaItem


def wrap(dic, keyList, default = ""):
    try:
        for key in keyList:
            dic = dic[key]
        return dic
    except:
        return default


class WeiboChaohuaSpider(scrapy.Spider):
    
    name = "WeiboChaohua"
    
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
        print("Start crawling...")
        # chaohua_ids = ["100808d86d4607d6eba7077350cf8405c790a3"]
        chaohua_ids = list(self.red.smembers('weibo_chaohua_id'))
        chaohua_ids.sort()
        
        pbar = tqdm(chaohua_ids)
        for i, chaohua_id in enumerate(pbar):
            chaohua_id = str(chaohua_id, 'utf-8') if type(chaohua_id) != str else chaohua_id
            pbar.set_description("Crawling:")
            yield scrapy.Request(url = f"https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&containerid={chaohua_id}",
                                 callback = self.parse,
                                 priority = 10,
                                 meta = {
                                     'chaohua_id': chaohua_id,
                                     'page_id': 0,

                                     'index_value': chaohua_id,
                                     'duplicate_removal': True,
                                     'store_db': self.db,
                                     'store_key': 'seen_weibo_chaohua_id',
                                 })

    def parse(self, response):
        chaohua_id = response.meta['chaohua_id']
        page_id = response.meta['page_id']
        data = json.loads(response.body)
        
        try:
            if data['ok'] == 0:
                return
        except:
            logging.error(response, response.body)
        
        nick = wrap(data, ['data', 'nick'])
        since_id = wrap(data, ['data', 'pageInfo','since_id'])
        
        for uData in wrap(data, ['data', 'cards'], []):
            if wrap(uData, ['card_type']) != "11":
                continue
            for card_data in wrap(uData, ['card_group']):
                if wrap(card_data, ['card_type']) != "9":
                    continue
                chaohuaItem = WeiboChaohuaItem()
                chaohuaItem['type'] = 'weibochaohuaitem'
                chaohuaItem['chaohua_id'] = chaohua_id
                chaohuaItem['cid'] = wrap(card_data, ['mblog', 'id'])
                chaohuaItem['nick'] = nick
                chaohuaItem['comments_count'] = wrap(card_data, ['mblog', 'comments_count'])
                chaohuaItem['created_at'] = wrap(card_data, ['mblog', 'created_at'])
                chaohuaItem['source'] = wrap(card_data, ['mblog', 'source'])
                chaohuaItem['text'] = wrap(card_data, ['mblog', 'text'])
                chaohuaItem['user_id'] = wrap(card_data, ['mblog', 'user', 'id'])
                chaohuaItem['description'] = wrap(card_data, ['mblog', 'user', 'description'])
                chaohuaItem['screen_name'] = wrap(card_data, ['mblog', 'user', 'screen_name'])
                chaohuaItem['followers_count'] = wrap(card_data, ['mblog', 'user', 'followers_count'])
                chaohuaItem['verified_reason'] = wrap(card_data, ['mblog', 'user', 'verified_reason'])
                yield chaohuaItem
                # print(chaohuaItem['screen_name'], page_id, since_id)

        url = f"https://m.weibo.cn/api/container/getIndex?jumpfrom=weibocom&containerid={chaohua_id}&since_id={since_id}"

        yield scrapy.Request(url = url,
                             callback = self.parse, 
                             meta = {
                                 'chaohua_id': chaohua_id, 
                                 'page_id': page_id + 1,
                             }, 
                             priority = 10)
